import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file (always resolves to project root)
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def send_acceptance_mail(receiver_email, candidate_name, position_name):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("HATA: E-posta gönderici bilgileri bulunamadı. Lütfen .env dosyasını kontrol edin.")
        return False

    if not receiver_email or "@" not in receiver_email:
        return False

    subject = f"Tebrikler! {position_name} Başvurunuz Hakkında"
    body = f"""Sayın {candidate_name},\n\n{position_name} pozisyonu için başvurunuz ön değerlendirmeyi geçmiştir. Yakında online mülakat için iletişime geçeceğiz.\n\nBaşarılar."""
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        print(f"DEBUG: {receiver_email} adresine mail gönderiliyor...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("DEBUG: Mail başarıyla gönderildi!")
        return True
    except Exception as e:
        print(f"MAIL GÖNDERİM HATASI DETAYI: {e}")
        return False

def send_rejection_mail(receiver_email, candidate_name, position_name):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    if not sender_email or not sender_password:
        print("HATA: E-posta gönderici bilgileri bulunamadı. Lütfen .env dosyasını kontrol edin.")
        return False

    if not receiver_email or "@" not in receiver_email:
        return False

    subject = f"{position_name} Başvurunuz Hakkında"
    body = f"""Sayın {candidate_name},\n\n{position_name} pozisyonu için yaptığınız başvuru incelenmiş olup, üzülerek olumlu değerlendiremediğimizi bildirmek isteriz. İlginiz için teşekkür ederiz.\n\nBaşarılar dileriz."""
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return True
    except Exception as e:
        print("Mail Hatası:", e)
        return False