import fitz  # PyMuPDF

def extract_text_with_layout(pdf_path: str) -> str:
    """
    Sayfa koordinatlarını kullanarak PDF'i iki sütunlu (sol ve sağ) olarak
    mantıksal bir sırayla okur. Çift sütunlu CV şablonları için optimize edilmiştir.
    """
    try:
        doc = fitz.open(pdf_path)
        full_text = ""
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            
            # Sayfa genişliği ve sütun sınır çizgisi belirleme
            page_width = page.rect.width
            split_line = page_width * 0.40  # Sol sütun sınırı (%40)
            
            blocks = page.get_text("blocks")
            left_column = []
            right_column = []
            
            # Blokları konumlarına göre sol veya sağ sütuna ayırma
            for block in blocks:
                if block[6] == 0:  # 0: Metin bloğu
                    # block[0]: Bloğun sol kenar koordinatı (x0)
                    if block[0] < split_line:
                        left_column.append(block)
                    else:
                        right_column.append(block)
            
            # Sütunları dikey eksende (y koordinatı: block[1]) yukarıdan aşağıya sıralama
            left_column.sort(key=lambda b: b[1])
            right_column.sort(key=lambda b: b[1])
            
            # Önce sol sütun, ardından sağ sütun metinlerini birleştirme
            for block in left_column:
                text = block[4].strip()
                if text:
                    full_text += text + "\n\n"
            
            for block in right_column:
                text = block[4].strip()
                if text:
                    full_text += text + "\n\n"
                    
        return full_text
    
    except Exception as e:
        return f"Dosya okunurken hata oluştu: {str(e)}"


if __name__ == "__main__":
    test_pdf_yolu = "../data/test_cv.pdf" 
    
    print("--- Sütun Analizli PDF Metin Çıkarım Testi ---")
    ayristirilan_metin = extract_text_with_layout(test_pdf_yolu)
    print(ayristirilan_metin)