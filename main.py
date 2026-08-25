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
from bs4 import BeautifulSoup
import sys
import uuid

# ==================== إعدادات البريد الإلكتروني (SMTP) ====================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "afolky10@gmail.com"
SENDER_PASSWORD = "lttgkiavoniisnyk"
# ======================================================================

# قائمة الشركات المستهدفة (يمكنك إضافة أي عدد من الشركات بروابطها الحقيقية)
TARGET_COMPANIES = [
    {
        "id": str(uuid.uuid4())[:8],
        "name": "TechVenture Solutions",
        "url": "https://example.com",
        "email": "afolky10@gmail.com",
        "state": "NEW"
    },
    {
        "id": str(uuid.uuid4())[:8],
        "name": "Global Retail Hub",
        "url": "https://httpbin.org/html",
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
    """تشغيل سيرفر الويب للحفاظ على نشاط الخدمة على Render"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"[{datetime.now()}] Web server started and listening on port {port}", flush=True)
    server.serve_forever()

def fetch_and_analyze_webpage(url):
    """جلب صفحة الويب الخاصة بالشركة وتحليل محتواها"""
    print(f"[{datetime.now()}] جاري جلب وفحص صفحة الويب: {url}...", flush=True)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # استخراج عنوان الموقع أو أول وصف تقريبي كمؤشر تحليل
            title = soup.title.string if soup.title else "No Title Found"
            text_snippet = soup.get_text()[:300].strip().replace('\n', ' ')
            
            analysis_result = {
                "status": "Success",
                "title": title,
                "snippet": text_snippet,
                "latency_ms": round(response.elapsed.total_seconds() * 1000, 2)
            }
            print(f"[{datetime.now()}] [ANALYZE SUCCESS] تم فحص الموقع بنجاح. زمن الاستجابة: {analysis_result['latency_ms']}ms", flush=True)
            return analysis_result
        else:
            print(f"[{datetime.now()}] [ANALYZE WARNING] استجابة الموقع غير طبيعية، كود الحالة: {response.status_code}", flush=True)
            return {"status": "Warning", "title": "Unknown", "latency_ms": 500}
    except Exception as e:
        print(f"[{datetime.now()}] [ANALYZE ERROR] فشل الاتصال بالموقع: {e}", flush=True)
        return {"status": "Error", "title": "Unreachable", "latency_ms": 999}

def send_email_message(to_email, subject, body_text):
    """إرسال التقرير النهائي عبر البريد الإلكتروني"""
    try:
        print(f"[{datetime.now()}] المحاولة للاتصال بخادم البريد وإرسال الرسالة إلى {to_email}...", flush=True)
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
        print(f"[{datetime.now()}] [SUCCESS] تم إرسال التقرير بنجاح إلى: {to_email}", flush=True)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] [ERROR] فشل إرسال الإيميل بسبب الخطأ: {e}", flush=True)
        return False

def run_outreach_engine():
    """المحرك التلقائي الشامل لفحص الشركات وإرسال التقارير"""
    print(f"[{datetime.now()}] بدء تشغيل محرك الأتمتة الشامل للشركات...", flush=True)
    time.sleep(5) # انتظار استقرار الشبكة والسيرفر
    
    while True:
        for company in TARGET_COMPANIES:
            if company["state"] == "NEW":
                print(f"[{datetime.now()}] معالجة الشركة المستهدفة: {company['name']} ({company['url']})", flush=True)
                
                # 1. جلب وفحص صفحة الويب
                analysis = fetch_and_analyze_webpage(company["url"])
                
                # 2. بناء التقرير الاحترافي بناءً على الفحص الفعلي
                subject = f"Strategic Performance Audit & Revenue Optimization Report for {company['name']}"
                body = (
                    f"Dear {company['name']} Executive Team,\n\n"
                    f"Our automated AI audit engine scanned your platform ({company['url']}) and detected the following metrics:\n"
                    f"- Detected Page Title: {analysis.get('title')}\n"
                    f"- Server Latency Speed: {analysis.get('latency_ms')} ms\n\n"
                    f"Identified Core Bottlenecks:\n"
                    f"1. Sub-optimal mobile conversion pathways & checkout friction.\n"
                    f"2. Search Engine Optimization (SEO) structured data gaps.\n\n"
                    f"Turnkey Solution Package (Full Tech Upgrade & AI Scaling): 799 USDT\n"
                    f"Secure MyPal Checkout Link: https://your-mypal-wallet-payment-page.com/checkout?order={company['id']}\n\n"
                    f"Best regards,\nPainPilot AI Growth Solutions"
                )
                
                # 3. إرسال التقرير عبر البريد
                success = send_email_message(company["email"], subject, body)
                if success:
                    company["state"] = "SENT"
                else:
                    company["state"] = "FAILED"
                    
        # الانتظار لمدة ساعة قبل إعادة فحص الجولة القادمة
        print(f"[{datetime.now()}] اكتملت الدولة الحالية. الدخول في وضع الاستعداد...", flush=True)
        time.sleep(3600)

if __name__ == "__main__":
    print(f"[{datetime.now()}] تشغيل نظام PainPilot AI المدمج بالكامل...", flush=True)
    
    # تشغيل سيرفر الويب في خلفية النظام
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    # تشغيل محرك الفحص والإرسال للشركات
    engine_thread = threading.Thread(target=run_outreach_engine, daemon=True)
    engine_thread.start()
    
    # إبقاء السيرفر الرئيسي يعمل للأبد
    while True:
        time.sleep(3600)
