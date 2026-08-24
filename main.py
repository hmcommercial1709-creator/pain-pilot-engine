import time
import requests
import json
from datetime import datetime
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# إعدادات النظام والاتصال
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
WHATSAPP_TOKEN = "YOUR_ACCESS_TOKEN"
TARGET_PHONE = "YOUR_WHATSAPP_NUMBER"

# سيرفر وهمي صغير جداً لإرضاء منصة Render وفتح البورت المطلوب
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7 successfully!")
    def log_message(self, format, *args):
        pass # لإيقاف طباعة تفاصيل طلبات المتصفح المزعجة في السجل

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    print(f"[{datetime.now()}] تم تشغيل سيرفر البورت الوهمي على المنفذ {port}")
    server.serve_forever()

def send_whatsapp_alert(message):
    """دالة لإرسال التنبيهات عبر الواتساب فور حدوث أي نشاط أو طلب"""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": TARGET_PHONE,
        "type": "text",
        "text": {"body": message}
    }
    try:
        response = requests.post(WHATSAPP_API_URL, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"[{datetime.now()}] تم إرسال تنبيه الواتساب بنجاح.")
        else:
            print(f"[{datetime.now()}] خطأ في إرسال الواتساب: {response.text}")
    except Exception as e:
        print(f"[{datetime.now()}] حدث استثناء أثناء إرسال الواتساب: {e}")

def run_engine():
    print(f"[{datetime.now()}] بدأ تشغيل محرك الأتمتة بنجاح ويعمل على مدار الساعة...")
    send_whatsapp_alert("🤖 تم بدء تشغيل محرك الأتمتة بنجاح على السيرفر ويعمل الآن 24/7.")
    
    while True:
        try:
            # هنا يتم فحص الطلبات والروابط والمدفوعات بشكل دوري
            print(f"[{datetime.now()}] جاري فحص النظام والعمليات المعلقة...")
            
            # محاكاة دورة الفحص (كل 5 دقائق)
            time.sleep(300)
            
        except Exception as e:
            print(f"[{datetime.now()}] حدث خطأ في دورة التشغيل: {e}")
            time.sleep(60)

if __name__ == "__main__":
    # تشغيل سيرفر البورت في الخلفية لكي لا يعطل مهام الأتمتة الأساسية
    server_thread = threading.Thread(target=run_dummy_server, daemon=True)
    server_thread.start()
    
    # تشغيل المحرك الأساسي
    run_engine()
