import time
import requests
import json
from datetime import datetime
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid

# ==================== إعدادات البريد الإلكتروني (SMTP) ====================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "afolky10@gmail.com"
SENDER_PASSWORD = "lttgkiavoniisnyk"
# ======================================================================

TEST_COMPANY_QUEUE = [
    {
        "id": str(uuid.uuid4())[:8],
        "name": "Test Enterprise",
        "url": "https://example.com",
        "email": "afolky10@gmail.com",
        "state": "NEW"
    }
]

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PainPilot AI Enterprise Growth Engine is Live 24/7!")
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

def send_email_message(to_email, subject, body_text):
    """دالة إرسال البريد الإلكتروني الاحترافي"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body_text, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"[{datetime.now()}] [TEST SUCCESS] تم إرسال الإيميل التجريبي بنجاح إلى: {to_email}")
        return True
    except Exception as e:
        print(f"[{datetime.now()}] [TEST ERROR] فشل إرسال الإيميل: {e}")
        return False

def run_immediate_test():
    """دالة اختبار فورية تعمل بمجرد تشغيل السيرفر"""
    print(f"[{datetime.now()}] تشغيل اختبار الإرسال الفوري...")
    for company in TEST_COMPANY_QUEUE:
        subject = f"Strategic Performance Audit & Revenue Optimization Report for {company['name']}"
        body = (
            f"Dear {company['name']} Executive Team,\n\n"
            f"This is an automated test report to verify the PainPilot AI engine connection.\n"
            f"1. DETECTED ISSUE: High Server Latency & Slow Page Response\n"
            f"2. DETECTED ISSUE: Conversion Path & Checkout Friction\n"
            f"3. DETECTED ISSUE: Organic Traffic & SEO Architecture Gaps\n\n"
            f"Turnkey Solution Package: 799 USDT\n"
            f"MyPal Checkout: https://your-mypal-wallet-payment-page.com/checkout?order={company['id']}\n\n"
            f"Best regards,\nPainPilot AI Solutions"
        )
        send_email_message(company["email"], subject, body)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    # تنفيذ الاختبار الفوري للإيميل بمجرد الإقلاع
    run_immediate_test()
    
    while True:
        time.sleep(3600)
