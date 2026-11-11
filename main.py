import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

# 1. إعدادات الإيميل من GitHub Secrets
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")

# 2. رابط البحث عن الصفقات فـ بوابة الصفقات العمومية
URL = "https://www.marchespublics.gov.ma/index.php?page=entreprise.EntrepriseAdvancedSearch&AllCons"


def fetch_and_filter_tenders():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        matched_tenders = []

        # البحث على الإعلانات فـ الجدول
        rows = soup.find_all("div", class_="panel-line")

        for row in rows:
            text_content = row.get_text()

            # التصفية حسب الشروط
            if (
                "simplifié" in text_content.lower()
                or "bon de commande" in text_content.lower()
            ):
                matched_tenders.append(text_content.strip())

        return matched_tenders

    except Exception as e:
        print(f"Error fetching data: {e}")
        return []


def send_email(tenders):
    if not tenders:
        print("لا توجد صفقات جديدة تطابق الشروط اليوم.")
        return

    subject = f"🚨 تنبيه: صفقات جديدة أقل من 10,000 درهم ({len(tenders)})"

    body = "سلام، هاهوما الصفقات الجديدة اللي لقينا فـ marchespublics.gov.ma:\n\n"
    for idx, t in enumerate(tenders, 1):
        body += f"{idx}. {t}\n"
        body += "-" * 40 + "\n"

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("تم إرسال الإيميل بنجاح!")
    except Exception as e:
        print(f"خطأ فـ إرسال الإيميل: {e}")


if __name__ == "__main__":
    results = fetch_and_filter_tenders()
    if results:
        send_email(results)
