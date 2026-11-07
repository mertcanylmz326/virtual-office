import os
from flask import Flask, render_template_string

app = FlaskName = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Ofis Konumları & Durumları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "x": 120, "y": 120, "status": "Müşteri Desteğinde", "color": "#3498db"},
    "Talisca": {"role": "Sipariş Takip", "x": 300, "y": 120, "status": "Veri İşliyor", "color": "#e74c3c"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "x": 480, "y": 120, "status": "Kod Yazıyor", "color": "#2ecc71"},
    "Kante": {"role": "Pazarlama & Büyüme", "x": 660, "y": 120, "status": "Kampanya Planlıyor", "color": "#f1c40f"},
    "İrfan": {"role": "Muhasebe & Finans", "x": 780, "y": 280, "status": "Bütçe İnceliyor", "color": "#9b59b6"},
    "İsmail": {"role": "İnsan Kaynakları", "x": 120, "y": 380, "status": "Mülakatta", "color": "#e67e22"},
    "Alex": {"role": "Hukuk & Mevzuat", "x": 300, "y": 380, "status": "Sözleşme İnceliyor", "color": "#1abc9c"},
    "Skrinar": {"role": "Siber Güvenlik", "x": 480, "y": 380, "status": "Sistemi Tarıyor", "color": "#34495e"},
    "Kerem": {"role": "Müşteri Başarı", "x": 660, "y": 380, "status": "Onboarding Yapıyor", "color": "#e84393"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Canlı Robotik Sanal Ofis</title>
    <style>
        body { background-color: #121212; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 15px; }
        h1 { margin-bottom: 5px; font-size: 22px; color: #00ffcc; }
        p { font-size: 13px; color: #aaa; margin-bottom: 15px; }
        
        #office-container { 
            position: relative; 
            width: 900px; 
            height: 520px; 
            margin: 0 auto; 
            background: linear-gradient(135deg, #1f2937, #111827); 
            border: 3px solid #00ffcc; 
            border-radius: 12px; 
            overflow: hidden; 
            box-shadow: 0 10px 30px rgba(0,255,204,0.2); 
        }

        /* Ofis İçi Bölmeler / Masalar */
        .desk { position: absolute; width: 90px; height: 50px; background: rgba(255,255,255,0.05); border: 1px dashed rgba(255,255,255,0.2); border-radius: 6px; }

        /* Hareketli Robot Karakterler */
        .robot { 
            position: absolute; 
            width: 70px; 
            height: 70px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: transform 0.5s ease-in-out;
            animation: floatRobot 3s ease-in-out infinite;
        }

        .robot-icon {
            font-size: 28px;
            background: rgba(0,0,0,0.6);
            border-radius: 50%;
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }

        .robot-name {
            font-size: 10px;
            font-weight: bold;
            background: rgba(0,0,0,0.8);
            padding: 2px 6px;
            border-radius: 4px;
            margin-top: 3px;
            white-space: nowrap;
            border: 1px solid rgba(255,255,255,0.2);
        }

        @keyframes floatRobot {
            0% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-5px) rotate(1deg); }
            100% { transform: translateY(0px) rotate(0deg); }
        }

        .robot:hover {
            transform: scale(1.2) !important;
            z-index: 50;
        }

        /* Bilgi Kutusu (Modal/Popup) */
        #info-panel {
            position: absolute;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid #00ffcc;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 14px;
            display: none;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            z-index: 100;
        }
    </style>
</head>
<body>

    <h1>🤖 E-Trade Pro - Canlı Robotik Yönetim Merkezi</h1>
    <p>CEO: Mertcan | Yapay zeka ajanlarımız sahada aktif görevde. Detaylar için robotlara dokun!</p>

    <div id="office-container">
        <!-- Dekoratif Masalar -->
        <div class="desk" style="left: 110px; top: 110px;"></div>
        <div class="desk" style="left: 290px; top: 110px;"></div>
        <div class="desk" style="left: 470px; top: 110px;"></div>
        <div class="desk" style="left: 650px; top: 110px;"></div>
        <div class="desk" style="left: 770px; top: 270px;"></div>
        <div class="desk" style="left: 110px; top: 370px;"></div>
        <div class="desk" style="left: 290px; top: 370px;"></div>
        <div class="desk" style="left: 470px; top: 370px;"></div>
        <div class="desk" style="left: 650px; top: 370px;"></div>

        <!-- 9 Robot Karakter -->
        {% for name, data in employees.items() %}
        <div class="robot" style="left: {{ data.x }}px; top: {{ data.y }}px;" 
             onclick="showInfo('{{ name }}', '{{ data.role }}', '{{ data.status }}')">
            <div class="robot-icon" style="border-color: {{ data.color }};">🤖</div>
            <div class="robot-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}

        <div id="info-panel"></div>
    </div>

    <script>
        const panel = document.getElementById('info-panel');

        function showInfo(name, role, status) {
            panel.style.display = 'block';
            panel.innerHTML = `<strong>👤 Ajan:</strong> ${name} &nbsp;|&nbsp; <strong>💼 Görev:</strong> ${role} &nbsp;|&nbsp; <span style="color: #00ffcc;">● Durum:</span> ${status}`;
            
            // 4 saniye sonra paneli otomatik gizle
            setTimeout(() => {
                panel.style.display = 'none';
            }, 4000);
        }

        // Robotların ofis içinde hafifçe yer değiştirmesini sağlayan canlı simülasyon döngüsü
        setInterval(() => {
            const robots = document.querySelectorAll('.robot');
            robots.forEach(robot => {
                let randomX = (Math.random() - 0.5) * 12;
                let randomY = (Math.random() - 0.5) * 12;
                let currentLeft = parseFloat(robot.style.left);
                let currentTop = parseFloat(robot.style.top);
                robot.style.left = (currentLeft + randomX) + 'px';
                robot.style.top = (currentTop + randomY) + 'px';
            });
        }, 2000);
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
