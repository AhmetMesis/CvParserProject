import sqlite3
import json

DB_NAME = "ats_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Adaylar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT,
            skills TEXT,
            assigned_role TEXT,
            match_score REAL,
            cv_path TEXT,
            education TEXT,
            experience TEXT,
            status TEXT DEFAULT 'Beklemede',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Kolon göçü kontrolü (Eğer veritabanı mevcutsa ve yeni kolonlar yoksa)
    cursor.execute("PRAGMA table_info(candidates)")
    columns = [col[1] for col in cursor.fetchall()]
    if "education" not in columns:
        cursor.execute("ALTER TABLE candidates ADD COLUMN education TEXT")
    if "experience" not in columns:
        cursor.execute("ALTER TABLE candidates ADD COLUMN experience TEXT")

    # 2. Pozisyonlar Tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE,
            required_skills TEXT,
            quota INTEGER,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Varsayılan başlangıç pozisyonları
    cursor.execute("SELECT COUNT(*) FROM positions")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO positions (title, required_skills, quota) VALUES ('Veri Bilimcisi', 'Makine Öğrenmesi,İstatistik,Veri Analizi,Veri Madenciliği,Python', 3)")
        cursor.execute("INSERT INTO positions (title, required_skills, quota) VALUES ('Yapay Zeka Mühendisi', 'Deep Learning,PyTorch,Computer Vision,YOLO,Python', 2)")

    conn.commit()
    conn.close()

def save_candidate(name, email, phone, skills_list, assigned_role, match_score, cv_path, education_list=None, experience_list=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    skills_str = json.dumps(skills_list, ensure_ascii=False)
    education_str = json.dumps(education_list or [], ensure_ascii=False)
    experience_str = json.dumps(experience_list or [], ensure_ascii=False)
    
    cursor.execute('''
        INSERT INTO candidates (name, email, phone, skills, assigned_role, match_score, cv_path, education, experience)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, phone, skills_str, assigned_role, match_score, cv_path, education_str, experience_str))
    conn.commit()
    conn.close()

def add_position(title, required_skills, quota):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Aynı isimde bir pozisyon olup olmadığını kontrol etme
    cursor.execute("SELECT id, is_active FROM positions WHERE title = ?", (title,))
    existing = cursor.fetchone()
    
    if existing:
        # Varsa, onu aktif hale getirip bilgilerini güncelleme
        pos_id = existing[0]
        cursor.execute('''
            UPDATE positions 
            SET required_skills = ?, quota = ?, is_active = 1 
            WHERE id = ?
        ''', (required_skills, quota, pos_id))
    else:
        # Yoksa yeni kayıt ekleme
        cursor.execute('''
            INSERT INTO positions (title, required_skills, quota)
            VALUES (?, ?, ?)
        ''', (title, required_skills, quota))
        
    conn.commit()
    conn.close()