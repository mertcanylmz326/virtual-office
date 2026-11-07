import os
from flask import Flask, render_template_string

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

# HTML ve Arayüz Tasarımı Doğrudan Burada (Klasör derdi yok!)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Canlı Sanal Ofis</title>
    <style>
        body { background-color: #1e1e1e; color: #fff; font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 20px; }
        h1 { margin-bottom: 5px; }
        #office-container { position: relative; width: 900px; height: 500px; margin: 20px auto; background: #2c3e50; border: 4px solid #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }
        .employee { position: absolute; width: 65px; height: 65px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border: 2px solid #fff; }
        .employee:hover { transform: scale(1.2); z-index: 10; box-shadow: 0 0 15px #fff; }
        .tooltip { position: absolute; background: rgba(0,0,0,0.9); padding: 12px; border-radius: 6px; display: none; font-size: 13px; border: 1px solid #fff; z-index: 100; text-align: left; pointer-events: none; }
    </style>
</head>
<body>

    <h1>🏢 E-Trade Pro - Canlı Kuşbakışı Yönetim Merkezi</h1>
    <p>CEO: Mertcan | Ekip masalarında çalışıyor. Detaylar için çalışanların üzerine gelebilirsin.</p>

    <div id="office-container">
        <div id="tooltip" class="tooltip"></div>
        
        {% for name, data in employees.items() %}
        <div class="employee" style="left: {{ data.x }}px; top: {{ data.y }}px; background-color: {{ data.color }};"
             onmousemove="showTooltip(event, '{{ name }}', '{{ data.role }}', '{{ data.status }}')"
             onmouseout="hideTooltip()">
            {{ name }}
        </div>
        {% endfor %}
    </div>

    <script>
        const tooltip = document.getElementById('tooltip');

        function showTooltip(e, name, role, status) {
            tooltip.style.display = 'block';
            tooltip.style.left = (e.pageX + 15) + 'px';
            tooltip.style.top = (e.pageY + 15) + 'px';
            tooltip.innerHTML = `<strong>${name}</strong><br><em>${role}</em><br><span style="color: #2ecc71;">●</span> Durum: ${status}`;
        }

        function hideTooltip() {
            tooltip.style.display = 'none';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, employees=employees)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
