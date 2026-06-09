# 🚀 Akıllı ATS & CV Eşleştirme Portalı (AI-Powered Candidate Tracking System)

Bu proje, yapay zeka tabanlı bir **Aday Takip Sistemi (ATS - Applicant Tracking System)** ve özgeçmiş (CV) eşleştirme portalıdır. PDF formatındaki özgeçmişleri akıllı metin çıkarma yöntemleriyle okur, aday bilgilerini (isim, eğitim, deneyim, yetenekler) analiz eder ve şirket pozisyonlarıyla anlamsal (semantik) olarak eşleştirerek puanlar. Eşleşme puanı barajı (%50) aşan adaylar otomatik olarak sisteme kabul edilir ve İK paneline düşer. İK yetkilisi adayı kabul ettiğinde veya elediğinde adaya otomatik e-posta bildirimleri gider.

---

## ✨ Özellikler

- **📄 Akıllı PDF Metin Çıkarma:** Sütunlu veya karmaşık şablonlu CV'lerden satır düzenini koruyarak metin çıkarma (`PyMuPDF`).
- **🧠 Hibrit Varlık Tanıma (NER Engine):** Aday adı, eğitim bilgileri (üniversiteler, okullar ve bölümler), iş deneyimleri (şirketler) ve teknik yetenekleri tespit eden gelişmiş kurallar.
- **🛡️ E-posta İletişim Filtresi:** İletişim bilgilerini (E-posta, Telefon) regex desenleriyle hassas bir şekilde çeken kurallar (`Rules Engine`).
- **🔮 Derin Öğrenme Tabanlı Semantik Eşleştirme:** `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2` modeli) kullanarak kelimelerin harf benzerliğine değil, **anlamsal benzerliğine** (Kosinüs Benzerliği - Cosine Similarity) göre %100 Türkçe ve İngilizce destekli eşleştirme.
- **📧 Otomatik E-posta Bildirimleri:** `smtplib` ve Gmail SMTP entegrasyonu ile İK kararlarına göre (Kabul/Ret) adaylara otomatik e-posta gönderimi.
- **🖥️ Modern İK Paneli (Dashboard):** Adayların listelendiği, eşleşme puanına veya başvuru tarihine göre sıralanabildiği, yeni pozisyonların eklenebildiği/silinebildiği ve aday kabul/ret işlemlerinin yapıldığı arayüz.
- **📥 Aday Başvuru Arayüzü:** Adayların kolayca CV yükleyebileceği şık bir form.

---

## 🛠️ Teknoloji Yığını (Tech Stack)

- **Backend:** FastAPI (Python)
- **Yapay Zeka / NLP:** Sentence Transformers, PyMuPDF (fitz)
- **Veritabanı:** SQLite3
- **E-posta Servisi:** SMTP (Gmail App Password)
- **Frontend:** Vanilla HTML5, CSS3, Modern Javascript (Fetch API)

---

## ⚙️ Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/AhmetMesis/CvParserProject.git
cd CvParserProject
```

### 2. Sanal Ortam Oluşturun ve Aktive Edin
```bash
# Windows (PowerShell veya CMD)
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Çevre Değişkenlerini Ayarlayın
Projenin ana dizininde bulunan `.env.example` dosyasının bir kopyasını oluşturup adını `.env` olarak değiştirin:
```bash
# Windows (CMD)
copy .env.example .env

# Windows (PowerShell) veya macOS / Linux
cp .env.example .env
```
Ardından `.env` dosyasını açıp e-posta gönderimi için kullanılacak Gmail adresinizi ve Gmail Uygulama Şifrenizi (App Password) tanımlayın:
```env
SENDER_EMAIL=ornek_adresiniz@gmail.com
SENDER_PASSWORD=uygulama_sifreniz
```

### 5. Uygulamayı Başlatın
Sanal ortamınız aktifken aşağıdaki komutla sunucuyu başlatın:
```bash
uvicorn main:app --reload
```
Alternatif olarak sanal ortamı aktive etmeden doğrudan şu komutla da çalıştırabilirsiniz (Windows):
```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```
Uygulama varsayılan olarak `http://127.0.0.1:8000` adresinde çalışmaya başlayacaktır.
FastAPI interaktif API dokümantasyonuna `http://127.0.0.1:8000/docs` adresinden erişebilirsiniz.

### 6. Arayüzleri Açın
FastAPI sunucumuz artık web arayüzlerini de doğrudan barındırmaktadır:
- **Aday Başvuru Formu:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/) adresinden doğrudan erişebilirsiniz.
- **İK Yönetim Paneli:** [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard) adresinden doğrudan erişebilirsiniz.

---

## 📂 Proje Yapısı

```text
CvParserProject/
│
├── data/                    # Örnek test verileri ve test CV'si
├── modules/                 # Çekirdek iş mantığı ve motorlar
│   ├── database.py          # Veritabanı oluşturma ve sorgular
│   ├── mailer.py            # SMTP e-posta gönderim mantığı (Dotenv entegrasyonlu)
│   ├── matcher.py           # Yapay Zeka tabanlı semantik eşleştirici
│   ├── ner_engine.py        # Bilgi ve varlık çıkarma motoru
│   ├── pdf_extractor.py     # PDF'ten yapılandırılmış metin çıkarma
│   └── rules.py             # İletişim bilgisi çıkarma kuralları
│
├── uploads/                 # Yüklenen aday özgeçmişleri (Git tarafından yoksayılır)
├── utils/                   # Yardımcı araçlar ve yardımcı fonksiyonlar
│
├── basvuru.html             # Aday başvuru arayüzü
├── dashboard.html           # İK kontrol paneli
├── main.py                  # FastAPI sunucu giriş noktası ve API uç noktaları
├── requirements.txt         # Gerekli kütüphaneler listesi
├── .env.example             # Çevre değişkenleri şablonu
├── .gitignore               # Git tarafından takip edilmeyecek dosyalar
└── README.md                # Proje açıklama belgesi
```

---

## 🔒 Güvenlik Uyarıları

- **Asla `.env` dosyasını veya hassas şifrelerinizi GitHub'a yüklemeyin.** Bu projede `.env` dosyası ve `.db` veritabanı dosyaları `.gitignore` ile korunmaktadır.
- Gmail ile otomatik mail gönderebilmek için normal Gmail şifreniz yerine Google hesabınızdan alacağınız iki adımlı doğrulamaya bağlı **"Uygulama Şifresi" (App Password)** kullanmanız gerekmektedir.
