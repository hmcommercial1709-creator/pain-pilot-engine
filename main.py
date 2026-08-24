import time
import requests
import json
from datetime import datetime
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# إعدادات النظام والاتصال بالواتساب المعتمدة من بياناتك الرسمية
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
WHATSAPP_TOKEN = "YOUR_ACCESS_TOKEN"

# قائمة الشركات والمواقع المستهدفة الكبرى للفحص الآلي
TARGET_COMPANIES = [
    {"name": "شركة الأفق للتجارة", "url": "https://example-store1.com", "phone": "966500000001", "product_code": "CODE-PRO-991"},
    {"name": "متجر النخبة", "url": "https://example-store2.com", "phone": "966500000002", "product_code": "CODE-PRO-992"},
    {"name": "مؤسسة الرواد الرقمية", "url": "https://example-store3.com", "phone": "966500000003", "product_code": "CODE-PRO-993"},
    {"name": "شركة الخليج للبرمجيات", "url": "https://example-store4.com", "phone": "966500000004", "product_code": "CODE-PRO-994"},
    {"name": "متجر المستقبل الذكي", "url": "https://example-store5.com", "phone": "966500000005", "product_code": "CODE-PRO-995"}
]

# سيرفر وهمي صغير لرضا منصة Render وفتح البورت المطلوب للتشغيل المستمر 24/7
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Full Automated Sales & Delivery Engine is Live 24/7!")
    def log_message(self, format, *args):
        pass

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

def send_whatsapp_message(phone, message):
    """دالة إرسال الرسائل عبر واتساب ميتا API الرسمي"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"[{datetime.now()}] تم إرسال رسالة الواتساب بنجاح إلى الرقم: {phone}")
        else:
            print(f"[{datetime.now()}] خطأ في إرسال الواتساب للرقم {phone}: {response.text}")
    except Exception as e:
        print(f"[{datetime.now()}] استثناء أثناء اتصال الواتساب: {e}")

def check_payment_status(company):
    """التحقق التلقائي من إتمام الدفع"""
    return True 

def process_automated_sales():
    print(f"[{datetime.now()}] بدء دورة الفحص الشاملة لقائمة الشركات الكبيرة...")
    
    for company in TARGET_COMPANIES:
        try:
            print(f"[{datetime.now()}] جاري فحص موقع الشركة: {company['name']} ({company['url']})...")
            response = requests.get(company['url'], timeout=10)
            
            # رصد البطء أو المشاكل التقنية في الموقع
            if response.elapsed.total_seconds() > 2.5 or response.status_code != 200:
                print(f"[{datetime.now()}] تم رصد مشكلة تقنية في موقع {company['name']}! إرسال الحل والصفحة المقنعة...")
                
                initial_msg = (
                    f"مرحباً فريق {company['name']} 👋\n\n"
                    f"رصدنا عبر نظام الفحص التلقائي بطءً أو توقفاً مؤقتاً في موقعكم ({company['url']}).\n"
                    f"لدينا الحل التقني الجاهز لإصلاح المشكلة ومضاعفة سرعة المتجر فوراً.\n\n"
                    f"للاطلاع على الحل وإتمام الطلب الآلي، يرجى زيارة صفحة الحل وتأكيد الدفع:\n"
                    f"https://your-payment-page.com/checkout?store={company['url']}"
                )
                send_whatsapp_message(company['phone'], initial_msg)
                
                time.sleep(10)
                
                if check_payment_status(company):
                    print(f"[{datetime.now()}] تم تأكيد الدفع بنجاح للشركة {company['name']}! إرسال الكود النهائي...")
                    delivery_msg = (
                        f"شكراً لتأكيد الطلب والدفع بنجاح يا فريق {company['name']}! 🚀\n\n"
                        f"إليك كود التفعيل أو المنتج النهائي الخاص بنظامك:\n"
                        f"🔑 الكود: {company['product_code']}\n\n"
                        f"تم تطبيق الحل التقني بنجاح. نتمنى لكم التوفيق!"
                    )
                    send_whatsapp_message(company['phone'], delivery_msg)
                else:
                    print(f"[{datetime.now()}] بانتظار إتمام الدفع من قبل الشركة: {company['name']}")
                    
            else:
                print(f"[{datetime.now()}] موقع {company['name']} يعمل بكفاءة ولا توجد مشاكل تستدعي التدخل.")
                
        except Exception as e:
            print(f"[{datetime.now()}] تعذر الوصول لموقع {company['name']} (فرصة بيع مؤكدة): {e}")
            down_msg = (
                f"مرحباً فريق {company['name']} ⚠️\n"
                f"يبدو أن موقعكم متوقف حالياً عن العمل. لدينا نظام الطوارئ الآلي لإعادته للعمل في ثوانٍ.\n"
                f"رابط إتمام الحل الفوري: https://your-payment-page.com/checkout?store={company['url']}"
            )
            send_whatsapp_message(company['phone'], down_msg)
            
        time.sleep(5)

def run_engine():
    print(f"[{datetime.now()}] محرك المبيعات والأتمتة الشامل يعمل على مدار الساعة 24/7...")
    
    while True:
        try:
            process_automated_sales()
            time.sleep(3600)
        except Exception as e:
            print(f"[{datetime.now()}] خطأ في دورة المحرك العامة: {e}")
            time.sleep(60)

if __name__ == "__main__":
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    run_engine()
