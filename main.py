from flask import Flask, render_template, request, jsonify
import random
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/audit', methods=['POST'])
def audit_site():
    data = request.get_json()
    url = data.get('url', 'example.com')
    
    # محاكاة فحص تقني فوري سريع
    time.sleep(1.5) # إعطاء إيحاء بالبحث العميق والواقعي
    
    issues = [
        {"type": "critical", "name": "Server Response Latency (High TTFB)", "desc": "استجابة السيرفر تتجاوز 720ms، مما يؤدي لهروب العملاء فوراً."},
        {"type": "warning", "name": "Missing OpenGraph & SEO Meta Tags", "desc": "غياب الأوصاف الهيكلية يدمر ظهورك العضوي في محركات البحث."},
        {"type": "critical", "name": "Uncompressed Assets & Heavy Scripts", "desc": "ملفات ضخمة غير مضغوطة تبطئ التحميل على الهواتف المحمولة."}
    ]
    
    estimated_loss = random.randint(2400, 5900)
    
    return jsonify({
        "status": "success",
        "url": url,
        "score": random.randint(42, 58),
        "issues": issues,
        "estimated_loss": estimated_loss
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
