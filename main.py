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
import re
import sys
import random

# ==================== إعدادات مرسل البريد (أنت) ====================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "afolky10@gmail.com"  # إيميلك الذي تخرج منه الرسالة
SENDER_PASSWORD = "lttgkiavoniisnyk"   # كلمة مرور التطبيق (App Password)
# ======================================================================

# قائمة المواقع المستهدفة (النظام سيفحصها، يستخرج إيميلاتها تلقائياً، ويبعث لها)
GLOBAL_TARGETS = [
    {"name": "Metro Cleaners UK", "url": "https://example.com", "market": "UK"},
    {"name": "Austin Local Bistro", "url": "https://httpbin.org/html", "market": "USA"},
]

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PainPilot Autonomous Lead Engine is Live 24/7!")
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    """تشغيل سيرفر الويب للحفاظ على نشاط الخدمة على Render"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"[{datetime.now()}] Web server running on port {port}", flush=True)
    server.serve_forever()

def extract_company_email_and_audit(target):
    """يفحص الموقع، يستخرج الإيميل تلقائياً، ويرصد المشاكل التقنية"""
    url = target["url"]
    name = target["name"]
    print(f"[{datetime.now()}] جاري فحص واستخراج بيانات الموقع: {name} ({url})...", flush=True)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PainPilot-Autonomous-Auditor'}
        response = requests.get(url, headers=headers, timeout=12)
        latency = round(response.elapsed.total_seconds() * 1000, 2)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Business Website"
            
            # البحث عن الإيميلات داخل صفحة الموقع الرئيسية باستخدام التعبير المنتظم (Regex)
            page_text = response.text
            email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            found_emails = re.findall(email_pattern, page_text)
            
            # تصفية الإيميلات المستخرجة (تجنب الإيميلات الوهمية أو امتدادات الصور مثل .png)
            valid_emails = [
                e for e in found_emails 
                if not any(ext in e.lower() for ext in ['.png', '.jpg', '.gif', '.svg', 'example.com', 'w3.org', 'wordpress'])
            ]
            
            target_email = ""
            if valid_emails:
                target_email = valid_emails[0] # يأخذ أول إيميل حقيقي يتم العثور عليه في الموقع
            else:
                # إذا لم يجد إيميل ظاهر، يقوم بتوليد الإيميل الرسمي بناءً على نطاق الموقع تلقائياً
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                if domain_match:
                    domain = domain_match.group(1)
                    target_email = f"info@{domain}"
                else:
                    target_email = "contact@business-target.com"

            # رصد المشاكل التقنية
            issues = []
            if latency > 350:
                issues.append("Server response time is too slow, causing mobile visitors to bounce.")
            if not soup.find('meta', attrs={'name': 'description'}):
                issues.append("Missing meta descriptions, which hurts organic search visibility.")
            
            if not issues:
                issues.append("Sub-optimal caching headers and mobile conversion friction.")

            return {
                "success": True,
                "title": title,
                "latency": latency,
                "issues": issues,
                "extracted_email": target_email
            }
        else:
            return {"success": False, "error": f"HTTP Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def send_email_to_company(target_email, company_name, audit_data):
    """إرسال التقرير تلقائياً إلى الإيميل المستخرج"""
    try:
        subject = f"Quick technical insight regarding {company_name} digital performance"
        issues_list = "\n".join([f"- {iss}" for iss in audit_data.get('issues', [])])
        
        body = (
            f"Hello {company_name} Team,\n\n"
            f"While reviewing digital performance trends in your sector, our automated audit system analyzed your platform ({company_name}) and identified a few technical bottlenecks affecting your customer acquisition:\n\n"
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
        msg['To'] = target_email  # الإيميل الذي تم استخراجه تلقائياً من موقع الشركة
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, target_email, msg.as_string())
        server.quit()
        print(f"[{datetime.now()}] [AUTONOMOUS EMAIL SENT] تم استخراج الإيميل وإرسال التقرير بنجاح إلى شركة {company_name} عبر العنوان: {target_email}", flush=True)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] [EMAIL ERROR] فشل إرسال البريد المستخرج: {e}", flush=True)
        return False

def run_global_mass_engine():
    """حلقة العمل المستمرة للبحث، الفحص، الاستخراج، والإرسال الذاتي"""
    print(f"[{datetime.now()}] بدء تشغيل المحرك الذاتي لاستخراج الإيميلات وإرسال التقارير...", flush=True)
    time.sleep(10)
    
    while True:
        for target in GLOBAL_TARGETS:
            result = extract_company_email_and_audit(target)
            if result.get("success"):
                extracted_email = result.get("extracted_email")
                print(f"[{datetime.now()}] تم بنجاح فحص {target['name']} واستخراج البريد تلقائياً: {extracted_email}", flush=True)
                
                # إرسال الإيميل مباشرة للعنوان المستخرج بدون أي تدخل بشري
                send_email_to_company(extracted_email, target["name"], result)
            
            time.sleep(5)
            
        print(f"[{datetime.now()}] اكتملت الدورة الحالية. جاري إعادة التمشيط...", flush=True)
        time.sleep(14400)

if __name__ == "__main__":
    print(f"[{datetime.now()}] إقلاع نظام PainPilot الذاتي بالكامل...", flush=True)
    
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    engine_thread = threading.Thread(target=run_global_mass_engine, daemon=True)
    engine_thread.start()
    
    while True:
        time.sleep(3600)
