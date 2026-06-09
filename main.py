from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os, shutil, sqlite3, uuid
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from modules.pdf_extractor import extract_text_with_layout
from modules.rules import extract_contact_info
from modules.ner_engine import extract_entities
from modules.matcher import calculate_semantic_match
from modules.database import init_db, save_candidate, add_position
from modules.mailer import send_acceptance_mail, send_rejection_mail

init_db()

app = FastAPI(title="Akıllı ATS")

# Yüklenen özgeçmiş dosyalarının statik olarak sunulması için klasör yapılandırması
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/static_cvs", StaticFiles(directory=UPLOAD_DIR), name="static_cvs")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/", response_class=FileResponse)
def read_root():
    return FileResponse("basvuru.html")

@app.get("/dashboard", response_class=FileResponse)
def read_dashboard():
    return FileResponse("dashboard.html")


@app.post("/parse-cv/")
async def parse_cv(file: UploadFile = File(...)):
    # PDF dosyasını benzersiz bir isimle kaydetme
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        cv_text = extract_text_with_layout(file_path)
        contact_info = extract_contact_info(cv_text)
        entities_info = extract_entities(cv_text)
        
        # Aktif pozisyonları veritabanından çekme
        conn = sqlite3.connect("ats_database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT title, required_skills FROM positions WHERE is_active = 1")
        db_positions = {row[0]: row[1].split(",") for row in cursor.fetchall()}
        conn.close()

        skills_found = entities_info.get("skills", [])
        match_result = calculate_semantic_match(skills_found, db_positions)
        
        # Eşik Değer Kontrolü (Minimum %50 uyum oranı gereklidir)
        if match_result["score"] < 50.0:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Başvurunuz reddedildi. Eşleşme oranınız (%{match_result['score']:.1f}) barajın altındadır.")

        save_candidate(
            name=entities_info.get("name", "Bilinmiyor"),
            email=contact_info.get("email"),
            phone=contact_info.get("phone"),
            skills_list=skills_found,
            assigned_role=match_result["assigned_role"],
            match_score=match_result["score"],
            cv_path=unique_filename,
            education_list=entities_info.get("education", []),
            experience_list=entities_info.get("experience", [])
        )
        
        return {
            "status": "success", 
            "candidate_name": entities_info.get("name"),
            "ai_decision": {"assigned_role": match_result["assigned_role"], "confidence_score": match_result["score"]}
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise e

@app.get("/candidates/")
def get_candidates(position: str = None, sort_by: str = "score"):
    conn = sqlite3.connect("ats_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = "SELECT * FROM candidates"
    params = []
    
    if position:
        query += " WHERE assigned_role = ?"
        params.append(position)
    
    if sort_by == "date":
        query += " ORDER BY created_at DESC"
    else:
        query += " ORDER BY match_score DESC"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return {"status": "success", "data": [dict(row) for row in rows]}

@app.get("/positions/")
def get_positions():
    conn = sqlite3.connect("ats_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM positions WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    return {"status": "success", "data": [dict(row) for row in rows]}

@app.post("/positions/")
def post_position(title: str, skills: str, quota: int = 1):
    try:
        add_position(title, skills, quota)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/positions/{p_id}")
def delete_position(p_id: int):
    try:
        conn = sqlite3.connect("ats_database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE positions SET is_active = 0 WHERE id = ?", (p_id,))
        conn.commit()
        conn.close()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/candidates/{c_id}")
def delete_candidate(c_id: int):
    conn = sqlite3.connect("ats_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Aday bilgilerini sorgulama
    cursor.execute("SELECT name, email, assigned_role, cv_path FROM candidates WHERE id = ?", (c_id,))
    res = cursor.fetchone()
    
    if res:
        # Red e-postası gönderimi
        if res['email']:
            send_rejection_mail(res['email'], res['name'], res['assigned_role'])
        
        # Özgeçmiş dosyasının silinmesi
        if res['cv_path']: 
            try:
                os.remove(os.path.join(UPLOAD_DIR, res['cv_path']))
            except:
                pass
            
        cursor.execute("DELETE FROM candidates WHERE id = ?", (c_id,))
        conn.commit()
        
    conn.close()
    return {"status": "success"}

@app.post("/candidates/{c_id}/accept")
def accept_candidate(c_id: int):
    conn = sqlite3.connect("ats_database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (c_id,))
    c = dict(cursor.fetchone())
    
    mail_gitti = False
    if c['email']:
        mail_gitti = send_acceptance_mail(c['email'], c['name'], c['assigned_role'])
    
    cursor.execute("UPDATE candidates SET status = 'Kabul Edildi' WHERE id = ?", (c_id,))
    conn.commit()
    conn.close()
    
    if not c['email']:
        return {"status": "success", "message": "Aday kabul edildi ancak mail adresi sistemde kayıtlı değil."}
    
    if mail_gitti:
        return {"status": "success", "message": "Aday kabul edildi ve bilgilendirme maili gönderildi."}
    else:
        return {"status": "success", "message": "Aday kabul edildi ancak mail GÖNDERİLEMEDİ! Lütfen SMTP ayarlarınızı kontrol edin."}
