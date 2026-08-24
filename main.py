import time
import requests
import json
from datetime import datetime

# إعدادات النظام والاتصال
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
WHATSAPP_TOKEN = "YOUR_ACCESS_TOKEN"
TARGET_PHONE = "YOUR_WHATSAPP_NUMBER"

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
    run_engine()
