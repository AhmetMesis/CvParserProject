import re

def extract_entities(text: str) -> dict:
    """
    CV metninden adayın adı, eğitim bilgileri, iş deneyimleri ve yeteneklerini
    ayıklar. Sütunlu yerleşimlere uygun kurallarla optimize edilmiştir.
    """
    entities = {
        "name": None,
        "education": [],
        "experience": [],
        "skills": []
    }
    
    # Metni boşluklardan arındırıp satırlara bölme
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Ad ve Soyad ayrı satırlardaysa birleştirme (Örn: RAFET / HEKİMOĞLU)
    if len(lines) >= 2:
        if (lines[0].isupper() and lines[1].isupper()) or (lines[0].istitle() and lines[1].istitle()):
            if len(lines[0].split()) == 1 and len(lines[1].split()) == 1:
                if not any(char in lines[0] or char in lines[1] for char in [".", ",", ":", "-", "|"]):
                    lines[0] = f"{lines[0]} {lines[1]}"
                    lines.pop(1)

    # İsim ve kurum eşleşmelerinde göz ardı edilecek genel başlıklar
    headers = ["İLETİŞİM", "BECERİLER", "EĞİTİM", "HAKKIMDA", "DİLLER", "İŞ DENEYİMİ", "DENEYİM", "PROJELER", "SERTİFİCALAR"]
    
    # 1. ADIM: İsim Çıkarımı
    # - Satır tamamen büyük harf ise ve başlık değilse isim olarak değerlendirilir.
    # - Satır baş harfleri büyükse ve ilk 5 satırda yer alıyorsa isim adayıdır.
    for i, line in enumerate(lines):
        if line.upper() in headers or "|" in line or any(char.isdigit() for char in line):
            continue
        if any(punc in line for punc in [".", ",", ":", "-", "(", ")"]):
            continue

        words = line.split()
        if 1 < len(words) <= 5:
            # Tamamen büyük harf kontrolü
            if line.isupper():
                entities["name"] = line.title()
                break
            
            # İlk satırlarda baş harfleri büyük kelimeler kontrolü
            if i < 5 and (line.istitle() or all(w[0].isupper() for w in words if w.isalpha())):
                # Eğitim veya pozisyon unvanı içermediğinden emin olunması
                if not any(k in line.lower() for k in ["üniversite", "lise", "fakülte", "mühendis"]):
                    entities["name"] = line.title()
                    break

    # 2. ADIM: Eğitim ve Deneyim Kurumlarının Çıkarılması
    education_keywords = ["üniversitesi", "fakültesi", "lisesi", "enstitüsü", "yüksekokulu"]
    company_keywords = ["a.ş.", "a.ş", "ltd.", "ltd", "şirketi", "holding", "bankası", "grup", "danışmanlık", "co.", "inc."]

    for idx, line in enumerate(lines):
        lower_line = line.replace('İ', 'i').replace('I', 'ı').lower()
        
        # Kişisel tanıtım ve açıklama cümlelerini eleme (Fiil ve eylem bildiren kelimeler dahil)
        intro_words = [
            "ben", "merhaba", "adım", "öğrenci", "öğrencisiyim", "çalışıyorum", 
            "hedefliyorum", "uzmanlaşmak", "geliştiriyorum", "geliştirdim", 
            "tamamladım", "katkı", "sağladım", "görev", "aldım", "yaptım", 
            "analiz", "ettim", "tasarladım", "yönettim", "hazırladım"
        ]
        if any(iw in lower_line for iw in intro_words):
            continue
            
        if len(line) < 90:
            # Eğitim Kurumu mu?
            if any(keyword in lower_line for keyword in education_keywords):
                edu_entry = line.strip().title()
                
                # Bir sonraki satırın bölüm bilgisi olup olmadığını kontrol etme
                if idx + 1 < len(lines):
                    next_line = lines[idx + 1].strip()
                    next_lower = next_line.replace('İ', 'i').replace('I', 'ı').lower()
                    
                    dept_keywords = [
                        "mühendisliği", "bölümü", "programı", "lisansı", "yüksek lisans", 
                        "anabilim", "yönetimi", "tasarımı", "iktisat", "işletme", 
                        "öğretmenliği", "edebiyatı", "dili", "bilimleri", "fizik", 
                        "kimya", "biyoloji", "matematik"
                    ]
                    
                    if len(next_line) < 90 and any(dk in next_lower for dk in dept_keywords):
                        if not any(char.isdigit() for char in next_line):
                            edu_entry += f" - {next_line.title()}"
                
                if edu_entry not in entities["education"]:
                    entities["education"].append(edu_entry)
                    
            # Şirket / Kurum adı kontrolü
            elif any(keyword in lower_line for keyword in company_keywords):
                clean_exp = line.title()
                if clean_exp not in entities["experience"]:
                    entities["experience"].append(clean_exp)

    # 3. ADIM: Teknik Yeteneklerin Eşleştirilmesi
    tech_skills_dictionary = [
        # Diller
        "python", "java", "c++", "c#", "javascript", "r", "typescript", "golang",
        # Web & Backend / DevOps
        "fastapi", "flask", "django", "nodejs", "react", "angular", "vue", "docker", 
        "kubernetes", "aws", "azure", "git", "html", "css", "rest api", "api",
        # Veritabanı
        "sql", "mysql", "postgresql", "mongodb", "sqlite", "oracle",
        # Yapay Zeka & Makine Öğrenmesi (İngilizce & Türkçe)
        "machine learning", "makine öğrenmesi", "deep learning", "derin öğrenme", 
        "yapay zeka", "artificial intelligence", "nlp", "doğal dil işleme",
        # Kütüphaneler & Modeller
        "pytorch", "tensorflow", "keras", "opencv", "yolo", "yolov12", "yolov8", 
        "pandas", "numpy", "scikit-learn", "scipy",
        # Görüntü İşleme & Diğer
        "computer vision", "görüntü işleme", "nesne tespiti", "object detection",
        "data mining", "veri madenciliği", "data analysis", "veri analizi", "istatistik",
        "statistics", "linux"
    ]
    
    full_text_lower = text.lower()
    for skill in tech_skills_dictionary:
        # Özel karakter barındıran c++ ve c# için özel sınır tanımı
        if "++" in skill or "#" in skill:
            pattern = rf"(?:^|[\s,;._\-\/\(\)])\+*{re.escape(skill)}\+*(?:$|[\s,;._\-\/\(\)])"
        else:
            pattern = rf"\b{re.escape(skill)}\b"
            
        if re.search(pattern, full_text_lower):
            special_casings = {
                "pytorch": "PyTorch",
                "tensorflow": "TensorFlow",
                "scikit-learn": "Scikit-Learn",
                "opencv": "OpenCV",
                "fastapi": "FastAPI",
                "mongodb": "MongoDB",
                "postgresql": "PostgreSQL",
                "sqlite": "SQLite",
                "mysql": "MySQL",
                "rest api": "REST API",
                "nlp": "NLP",
                "yolov12": "YOLOv12",
                "yolov8": "YOLOv8",
                "yolo": "YOLO",
                "html": "HTML",
                "css": "CSS",
                "sql": "SQL",
                "git": "Git",
                "aws": "AWS",
                "api": "API",
                "r": "R"
            }
            if skill in special_casings:
                clean_name = special_casings[skill]
            else:
                clean_name = skill.capitalize()
            entities["skills"].append(clean_name)

    return entities


if __name__ == "__main__":
    from pdf_extractor import extract_text_with_layout
    
    test_pdf_yolu = "../data/test_cv.pdf" 
    cv_metni = extract_text_with_layout(test_pdf_yolu)
    
    print("--- Varlık Tanıma Analizi Başlatılıyor ---")
    sonuclar = extract_entities(cv_metni)
    
    print(f"\nBulunan İsim: {sonuclar['name']}")
         
    print("\nBulunan Eğitim Kurumları:")
    for edu in sonuclar["education"]:
         print(f"- {edu}")
         
    print("\nBulunan İş / Kurum Deneyimleri:")
    if not sonuclar["experience"]:
        print("- (Deneyim bulunamadı)")
    for exp in sonuclar["experience"]:
         print(f"- {exp}")
         
    print("\nBulunan Teknik Yetenekler:")
    for skill in sonuclar["skills"]:
         print(f"- {skill}")