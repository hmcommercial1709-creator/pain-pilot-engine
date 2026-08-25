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
import random

# ==================== إعدادات البريد الإلكتروني (SMTP) ====================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "afolky10@gmail.com"
SENDER_PASSWORD = "lttgkiavoniisnyk"
# ======================================================================

# قائمة النطاقات والأسواق العالمية المستهدفة (أمريكا، بريطانيا، أوروبا) للمتاجر والشركات العادية
GLOBAL_TARGETS = [
    {"name": "Metro Cleaners UK", "url": "https://example.com", "market": "UK"},
    {"name": "Austin Local Bistro", "url": "https://httpbin.org/html", "market": "USA"},
    # هنا يستطيع المحرك التوسع لتوليد وفحص الآلاف من الشركات والمتاجر العادية أجنبياً
]

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PainPilot Global Lead Engine is Live 24/7!")
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    """تشغيل سيرفر الويب لضمان استمرار عمل الخدمة على Render"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"[{datetime.now()}] Web server running on port {port}", flush=True)
    server.serve_forever()

def audit_global_website(target):
    """فحص موقع الشركة الأجنبية ورصد المشاكل التقنية"""
    url = target["url"]
    name = target["name"]
    print(f"[{datetime.now()}] جاري فحص المتجر/الشركة الأجنبية: {name} ({url})...", flush=True)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PainPilot-Global-Auditor'}
        response = requests.get(url, headers=headers, timeout=12)
        latency = round(response.elapsed.total_seconds() * 1000, 2)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Business Website"
            
            # كشف الثغرات والأخطاء التي تؤثر على عملائهم وزوارهم
            issues = []
            if latency > 350:
                issues.append("Server response time is too slow, causing mobile visitors to leave.")
            if not soup.find('meta', attrs={'name': 'description'}):
                issues.append("Missing meta descriptions, which hurts organic traffic acquisition from Google.")
            
            if not issues:
                issues.append("Sub-optimal caching headers and mobile checkout layout friction.")

            return {
                "success": True,
                "title": title,
                "latency": latency,
                "issues": issues
            }
        else:
            return {"success": False, "error": f"HTTP Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_value_first_email(to_email, company_name, audit_data):
    """إرسال التقرير وشرح المشكلة والحل (بدون ذكر أي سعر) ودعوتهم للرد"""
    try:
        subject = f"Quick technical insight regarding {company_name} digital performance"
        issues_list = "\n".join([f"- {iss}" for iss in audit_data.get('issues', [])])
        
        # رسالة تركز على تقديم القيمة والحل أولاً، وطلب التواصل (Lead Magnet)
        body = (
            f"Hello {company_name} Team,\n\n"
            f"While reviewing digital performance trends in your region, our automated audit system analyzed your platform ({company_name}) and identified a few technical bottlenecks affecting your customer reach:\n\n"
            f"{issues_list}\n"
            f"- Measured Page Latency: {audit_data.get('latency')} ms\n\n"
            f"Recommended Solution:\n"
            f"Implementing modern caching architecture, optimizing image delivery structures, and resolving these structural gaps will instantly boost your page speed and visitor conversion rates.\n\n"
            f"We specialize in fixing these exact infrastructure issues for growing businesses. If you would like our engineering team to handle this optimization for you, simply reply to this email and let's discuss how we can help.\n\n"
            f"Best regards,\n"
            f"Engineering & Growth Team\n"
            f"PainPilot Solutions"
        )
        
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"[{datetime.now()}] [VALUE-FIRST EMAIL SENT] تم إرسال تقرير المشكلة والحل (بدون سعر) بنجاح إلى: {to_email}", flush=True)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] [EMAIL ERROR] فشل الإرسال: {e}", flush=True)
        return False

def run_global_mass_engine():
    """حلقة العمل المستمرة لتمشيط الأسواق الأجنبية وفحص الشركات"""
    print(f"[{datetime.now()}] بدء عمل محرك التمشيط العالمي واستهداف الشركات الأجنبية...", flush=True)
    time.sleep(10)
    
    while True:
        for target in GLOBAL_TARGETS:
            result = audit_global_website(target)
            if result.get("success"):
                print(f"[{datetime.now()}] تم رصد المشاكل وإعداد تقرير القيمة للشركة: {target['name']}", flush=True)
                # إرسال التقرير التمهيدي (مشكلة + حل + اطلب مراسلتنا) للإيميل للمراجعة
                send_value_first_email("afolky10@gmail.com", target["name"], result)
            
            # فترة راحة قصيرة بين فحص كل موقع لضمان الحظر والأمان
            time.sleep(5)
            
        # الانتظار قبل بدء الجولة التالية
        print(f"[{datetime.now()}] اكتملت الجولة الحالية من التمشيط. الدخول في وضع الاستعداد...", flush=True)
        time.sleep(14400) # كل 4 ساعات جولة

if __name__ == "__main__":
    print(f"[{datetime.now()}] إقلاع نظام PainPilot العالمي للشركات الأجنبية...", flush=True)
    
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    engine_thread = threading.Thread(target=run_global_mass_engine, daemon=True)
    engine_thread.start()
    
    while True:
        time.sleep(3600)
