import sys
import time
from sentence_transformers import SentenceTransformer, util

# Windows konsolunda Türkçe karakter kodlama hatasını önlemek için standart UTF-8 yapılandırması
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

print("Dil modeli yükleniyor...")
# Çok dilli SentenceTransformer modeli (paraphrase-multilingual-MiniLM-L12-v2)
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Model başarıyla yüklendi.")


def calculate_semantic_match(candidate_skills: list, job_requirements: dict) -> dict:
    """
    Adayın yeteneklerini, Kosinüs Benzerliği (Cosine Similarity) kullanarak
    açık pozisyonların gereksinimleriyle anlamsal olarak karşılaştırır.
    """
    if not candidate_skills:
        return {
            "assigned_role": "Genel Başvuru Havuzu",
            "score": 0,
            "message": "Adayın özgeçmişinde yetenek tespit edilemedi."
        }

    # Aday yeteneklerinin vektör temsilini oluşturma
    candidate_embeddings = model.encode(candidate_skills, convert_to_tensor=True)
    match_results = []
    
    # Her bir pozisyon için benzerlik değerlendirmesi
    for job_title, required_skills in job_requirements.items():
        if not required_skills:
            continue
            
        # Pozisyon gereksinimlerinin vektör temsilini oluşturma
        req_embeddings = model.encode(required_skills, convert_to_tensor=True)
        
        # Kosinüs benzerliği matrisi hesaplama
        cosine_scores = util.cos_sim(candidate_embeddings, req_embeddings)
        
        total_score = 0
        matched_details = []
        
        # Pozisyonun her bir gereksinimi için adaydaki en yakın yeteneği bulma
        for i, req in enumerate(required_skills):
            best_score = cosine_scores[:, i].max().item() * 100 
            total_score += best_score
            matched_details.append(f"{req} (Uyum: %{best_score:.1f})")
            
        # Pozisyon için ortalama uyum puanı
        avg_score = total_score / len(required_skills)
        
        match_results.append({
            "job_title": job_title,
            "score": round(avg_score, 1),
            "details": matched_details
        })
        
    # En yüksek uyum sağlanan pozisyonu belirleme
    best_match = max(match_results, key=lambda x: x['score'])
    
    # Minimum uyum barajı kontrolü (Eşik Değeri: %45)
    if best_match['score'] < 45.0:
        return {
            "assigned_role": "Genel Başvuru Havuzu",
            "score": best_match['score'],
            "all_scores": match_results,
            "message": "Adayın yetenekleri mevcut pozisyonlar için yeterli görülmedi, havuza aktarıldı."
        }
    
    return {
        "assigned_role": best_match['job_title'],
        "score": best_match['score'],
        "all_scores": match_results,
        "message": "Aday anlamsal eşleşme ile uygun pozisyona atandı."
    }


if __name__ == "__main__":
    # Test amaçlı şirket pozisyonları ve örnek aday yetenekleri
    SIRKET_POZISYONLARI = {
        "Frontend Geliştirici": ["ReactJS", "Web Tasarımı", "Kullanıcı Arayüzü"],
        "Veri Bilimcisi": ["Makine Öğrenmesi", "İstatistik", "Veri Analizi", "Yapay Zeka"]
    }
    
    adaydan_gelen_yetenekler = ["Pandas", "Scikit-learn", "Deep Learning", "Data Mining", "Python"]
    
    print("\n--- Eşleştirme Testi Başlatılıyor ---")
    start_time = time.time()
    
    sonuc = calculate_semantic_match(adaydan_gelen_yetenekler, SIRKET_POZISYONLARI)
    
    print(f"\nAtanan Pozisyon: {sonuc['assigned_role']}")
    print(f"Uyum Puanı: %{sonuc['score']}")
    print(f"Hesaplama Süresi: {time.time() - start_time:.3f} saniye")
    print("Detaylar:", sonuc['all_scores'])