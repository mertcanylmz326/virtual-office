import os
from flask import Flask, render_template

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Ofis Konumları & Durumları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "x": 100, "y": 100, "status": "Müşteri Desteğinde", "color": "#3498db"},
    "Talisca": {"role": "Sipariş Takip", "x": 250, "y": 100, "status": "Veri İşliyor", "color": "#e74c3c"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "x": 400, "y": 100, "status": "Kod Yazıyor", "color": "#2ecc71"},
    "Kante": {"role": "Pazarlama & Büyüme", "x": 550, "y": 100, "status": "Kampanya Planlıyor", "color": "#f1c40f"},
    "İrfan": {"role": "Muhasebe & Finans", "x": 700, "y": 100, "status": "Bütçe İnceliyor", "color": "#9b59b6"},
    "İsmail": {"role": "İnsan Kaynakları", "x": 100, "y": 300, "status": "Mülakatta", "color": "#e67e22"},
    "Alex": {"role": "Hukuk & Mevzuat", "x": 250, "y": 300, "status": "Sözleşme İnceliyor", "color": "#1abc9c"},
    "Skrinar": {"role": "Siber Güvenlik", "x": 400, "y": 300, "status": "Sistemi Tarıyor", "color": "#34495e"},
    "Kerem": {"role": "Müşteri Başarı", "x": 550, "y": 300, "status": "Onboarding Yapıyor", "color": "#e84393"}
}

@app.route('/')
def index():
    return render_template('index.html', employees=employees)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
