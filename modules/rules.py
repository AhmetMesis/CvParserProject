import re

def extract_contact_info(text: str) -> dict:
    """
    Ham CV metni içinden düzenli ifadeler (regex) ile e-posta ve telefon bilgilerini çıkarır.
    """
    contact_info = {
        "email": None,
        "phone": None
    }
    
    # E-posta deseni
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email_match = re.search(email_pattern, text)
    if email_match:
        contact_info["email"] = email_match.group()

    # Telefon Regex'i: Mobil ve Sabit hatları destekleyen Türkiye formatı (örn: 0 212 123 24 25 veya 05375620307)
    phone_pattern = r'(?:\+?90|0)?\s?[2-5]\d{2}\s?\d{3}\s?\d{2}\s?\d{2}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        contact_info["phone"] = phone_match.group().strip()

    return contact_info


if __name__ == "__main__":
    from pdf_extractor import extract_text_with_layout
    
    test_pdf_yolu = "../data/test_cv.pdf" 
    cv_metni = extract_text_with_layout(test_pdf_yolu)
    
    print("--- İletişim Bilgileri Ayıklama Testi ---")
    sonuclar = extract_contact_info(cv_metni)
    
    print(f"Bulunan E-posta : {sonuclar['email']}")
    print(f"Bulunan Telefon : {sonuclar['phone']}")