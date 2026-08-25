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

# قائمة عينة موسعة لمحاكاة آلاف الشركات والمتاجر في أمريكا، بريطانيا، وفرنسا وأوروبا
# (يمكنك لاحقاً توسيع هذه القائمة أو ربطها بمحرك جلب مخصص)
GLOBAL_MASS_TARGETS = [
    {"name": "London Elite Cleaners", "url": "https://example.com", "market": "UK"},
    {"name": "Paris Gourmet Bistro", "url": "https://httpbin.org/html", "market": "France"},
    {"name": "Austin Prime Services", "url": "https://example.org", "market": "USA"},
    {"name": "Berlin Tech Solutions", "url": "https://httpbin.org/delay/1", "market": "Germany"},
]

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"PainPilot Autonomous Mass Audit Radar is Live 24/7!")
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    """تشغيل سيرفر الويب الخفيف للحفاظ على استمرار عمل الخدمة على Render"""
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"[{datetime.now()}] Web server running on port {port}", flush=True)
    server.serve_forever()

def extract_email_and_audit(target):
    """رادار الفحص والفلترة الصارمة: يستخرج الإيميل ويفحص وجود مشاكل حقيقية فقط"""
    url = target["url"]
    name = target["name"]
    print(f"[{datetime.now()}] [رادار الفحص] جاري فحص وتمشيط موقع: {name} ({url})...", flush=True)
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) PainPilot-Mass-Auditor'}
        response = requests.get(url, headers=headers, timeout=12)
        latency = round(response.elapsed.total_seconds() * 1000, 2)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "Business Website"
            
            # استخراج الإيميل تلقائياً من محتوى الموقع
            page_text = response.text
            email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
            found_emails = re.findall(email_pattern, page_text)
            
            valid_emails = [
                e for e in found_emails 
                if not any(ext in e.lower() for ext in ['.png', '.jpg', '.gif', '.svg', 'example.com', 'w3.org', 'wordpress', 'sentry'])
            ]
            
            target_email = ""
            if valid_emails:
                target_email = valid_emails[0]
            else:
                domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
                if domain_match:
                    domain = domain_match.group(1)
                    target_email = f"info@{domain}"
                else:
                    target_email = "contact@business-target.com"

            # ----------------- الفلتر الصارم (رصد المشاكل الحقيقية فقط) -----------------
            issues = []
            
            # شرط البطء الشديد (أكثر من 350 ميلي ثانية يعتبر موقعاً متأثراً وفيه هبوط)
            if latency > 350:
                issues.append(f"Critical server response latency ({latency} ms), causing mobile visitors to bounce.")
            
            # غياب وصف السيو
            if not soup.find('meta', attrs={'name': 'description'}):
                issues.append("Missing meta descriptions, heavily hurting organic search acquisition from Google.")
            
            # إذا كان الموقع سليماً 100% ولا توجد مشاكل تذكر، نعتبره "سليم تماماً"
            has_real_pain = len(issues) > 0
            
            return {
                "success": True,
                "has_real_pain": has_real_pain,
                "title": title,
                "latency": latency,
                "issues": issues,
                "extracted_email": target_email
            }
        else:
            return {"success": False, "has_real_pain": False, "error": f"HTTP Status {response.status_code}"}
    except Exception as e:
        return {"success": False, "has_real_pain": False, "error": str(e)}

def send_value_first_email(target_email, company_name, audit_data):
    """إرسال تقرير القيمة وحل المشكلة حصرياً لمن لديه مشكلة حقيقية (بدون ذكر سعر)"""
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
        msg['To'] = target_email  # يرسل للشركة المستهدفة فقط
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, target_email, msg.as_string())
        server.quit()
        print(f"[{datetime.now()}] [صيد ثمين - تم الإرسال بنجاح] تمت محاكاة المشكلة وإرسال التقرير التقني حصرياً لشركة: {company_name} ({target_email})", flush=True)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] [EMAIL ERROR] فشل إرسال البريد: {e}", flush=True)
        return False

def run_mass_radar_engine():
    """حلقة العمل المستمرة لتمشيط الآلاف وفلترة السليم، وإرسال البريد حصرياً لمن لديه مشكلة حقيقية"""
    print(f"[{datetime.now()}] بدء عمل الرادار الآلي الشامل لتمشيط الشركات الأجنبية...", flush=True)
    time.sleep(10)
    
    while True:
        checked_count = 0
        emailed_count = 0
        
        for target in GLOBAL_MASS_TARGETS:
            checked_count += 1
            result = extract_email_and_audit(target)
            
            if result.get("success"):
                if result.get("has_real_pain"):
                    # وجدنا مشكلة صحيحة 100%! هنا فقط نرسل الإيميل لكي لا نحرق الإيميل عشوائياً
                    extracted_email = result.get("extracted_email")
                    print(f"[{datetime.now()}] [تنبيه: وجدنا مشكلة!] {target['name']} يعاني من أخطاء تقنية. جاري إرسال البريد المستهدف...", flush=True)
                    send_value_first_email(extracted_email, target["name"], result)
                    emailed_count += 1
                else:
                    # الموقع سليم وأموره تمام التمام -> نتخطاه بصمت تام دون إزعاج ودون إرسال أي شي
                    print(f"[{datetime.now()}] [موقع سليم] {target['name']} يعمل بكفاءة ولا توجد مشاكل تستدعي التواصل. تم تخطيه بصمت.", flush=True)
            
            # فاصل زمني قصير جداً بين فحص كل موقع لحماية السيرفر وعدم الحظر
            time.sleep(3)
            
        print(f"[{datetime.now()}] [تقرير الجولة] تم فحص {checked_count} شركة، وإرسال {emailed_count} إيميل فقط لمن لديهم مشاكل حقيقية. الدخول في وضع التمشيط الخلفي...", flush=True)
        time.sleep(14400) # الانتظار للجولة التالية

if __name__ == "__main__":
    print(f"[{datetime.now()}] إقلاع نظام PainPilot الرادار الذكي بالكامل...", flush=True)
    
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    engine_thread = threading.Thread(target=run_mass_radar_engine, daemon=True)
    engine_thread.start()
    
    while True:
        time.sleep(3600)
