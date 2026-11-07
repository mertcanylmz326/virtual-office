import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Ofis İçi Hedef Konumları (Odalar ve Sosyal Alanlar)
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "x": 100, "y": 100, "target_x": 100, "target_y": 100, "status": "Müşteri Desteğinde", "color": "#3498db"},
    "Talisca": {"role": "Sipariş Takip", "x": 280, "y": 100, "target_x": 280, "target_y": 100, "status": "Veri İşliyor", "color": "#e74c3c"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "x": 460, "y": 100, "target_x": 460, "target_y": 100, "status": "Kod Yazıyor", "color": "#2ecc71"},
    "Kante": {"role": "Pazarlama & Büyüme", "x": 640, "y": 100, "target_x": 640, "target_y": 100, "status": "Kampanya Planlıyor", "color": "#f1c40f"},
    "İrfan": {"role": "Muhasebe & Finans", "x": 820, "y": 100, "target_x": 820, "target_y": 100, "status": "Bütçe İnceliyor", "color": "#9b59b6"},
    "İsmail": {"role": "İnsan Kaynakları", "x": 100, "y": 380, "target_x": 100, "target_y": 380, "status": "Mülakatta", "color": "#e67e22"},
    "Alex": {"role": "Hukuk & Mevzuat", "x": 280, "y": 380, "target_x": 280, "target_y": 380, "status": "Sözleşme İnceliyor", "color": "#1abc9c"},
    "Skrinar": {"role": "Siber Güvenlik", "x": 460, "y": 380, "target_x": 460, "target_y": 380, "status": "Sistemi Tarıyor", "color": "#34495e"},
    "Kerem": {"role": "Müşteri Başarı", "x": 640, "y": 380, "target_x": 640, "target_y": 380, "status": "Onboarding Yapıyor", "color": "#e84393"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Kuşbakışı Mimari Sanal Ofis</title>
    <style>
        body { background-color: #0d1117; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; margin: 0; padding: 10px; }
        h1 { margin-bottom: 2px; font-size: 20px; color: #58a6ff; }
        p { font-size: 12px; color: #8b949e; margin-bottom: 10px; }

        /* Kuşbakışı Ofis Katı Haritası */
        #office-map { 
            position: relative; 
            width: 960px; 
            height: 540px; 
            margin: 0 auto; 
            background: #161b22; 
            border: 4px solid #30363d; 
            border-radius: 10px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.7); 
            overflow: hidden;
        }

        /* İç Duvarlar ve Odalar */
        .wall-h { position: absolute; background: #30363d; height: 6px; width: 100%; }
        .wall-v { position: absolute; background: #30363d; width: 6px; height: 100%; }
        
        .room-label {
            position: absolute;
            font-size: 11px;
            color: #8b949e;
            font-weight: bold;
            letter-spacing: 1px;
            text-transform: uppercase;
        }

        /* Özel Alanlar (Mutfak, Dinlenme, Oyun) */
        .zone {
            position: absolute;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
            border: 2px dashed rgba(255,255,255,0.15);
        }
        .kitchen { background: rgba(210, 153, 34, 0.1); color: #d29922; width: 160px; height: 110px; right: 20px; top: 20px; }
        .chill-zone { background: rgba(56, 139, 253, 0.1); color: #58a6ff; width: 160px; height: 120px; right: 20px; bottom: 20px; }

        /* Masalar */
        .desk { 
            position: absolute; 
            width: 75px; 
            height: 45px; 
            background: #21262d; 
            border: 2px solid #30363d; 
            border-radius: 6px; 
        }

        /* Yürüyen Robot Karakterler */
        .robot { 
            position: absolute; 
            width: 60px; 
            height: 60px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: all 1.5s ease-in-out; /* Akıcı yürüme efekti */
            z-index: 10;
        }

        .robot-icon {
            font-size: 24px;
            background: #0d1117;
            border-radius: 50%;
            width: 38px;
            height: 38px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid;
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        }

        .robot-name {
            font-size: 9px;
            font-weight: bold;
            background: rgba(13, 17, 23, 0.9);
            padding: 1px 5px;
            border-radius: 3px;
            margin-top: 2px;
            white-space: nowrap;
            border: 1px solid #30363d;
        }

        .robot:hover {
            transform: scale(1.25) !important;
            z-index: 100;
        }

        /* Bilgi Paneli */
        #status-bar {
            position: absolute;
            bottom: 10px;
            left: 20px;
            background: rgba(22, 27, 34, 0.95);
            border: 1px solid #30363d;
            padding: 8px 15px;
            border-radius: 6px;
            font-size: 13px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.5);
            z-index: 50;
            text-align: left;
        }
    </style>
</head>
<body>

    <h1>🏢 E-Trade Pro - Kuşbakışı Akıllı Ofis Katı</h1>
    <p>CEO: Mertcan | Ajanlar ofis içinde odalarında çalışıyor, kahve mutfağına ve dinlenme alanına gezmeye gidiyor.</p>

    <div id="office-map">
        <!-- Mimari Duvarlar ve Bölmeler -->
        <div class="wall-h" style="top: 240px;"></div>
        <div class="wall-v" style="left: 760px; height: 100%;"></div>

        <!-- Oda Etiketleri -->
        <div class="room-label" style="top: 15px; left: 25px;">Yönetim & Operasyon Kanadı</div>
        <div class="room-label" style="top: 255px; left: 25px;">Teknoloji & Hukuk Üssü</div>
        <div class="room-label" style="top: 15px; right: 55px;">Sosyal & Mola</div>

        <!-- Sosyal Alanlar -->
        <div class="zone kitchen">☕ Kahve & Mutfak</div>
        <div class="zone chill-zone">🎮 Dinlenme & Oyun</div>

        <!-- Sabit Çalışma Masaları -->
        <div class="desk" style="left: 85px; top: 90px;"></div>
        <div class="desk" style="left: 265px; top: 90px;"></div>
        <div class="desk" style="left: 445px; top: 90px;"></div>
        <div class="desk" style="left: 625px; top: 90px;"></div>
        <div class="desk" style="left: 795px; top: 90px;"></div>
        <div class="desk" style="left: 85px; top: 370px;"></div>
        <div class="desk" style="left: 265px; top: 370px;"></div>
        <div class="desk" style="left: 445px; top: 370px;"></div>
        <div class="desk" style="left: 625px; top: 370px;"></div>

        <!-- Ajan / Robot Karakterler -->
        {% for name, data in employees.items() %}
        <div class="robot" id="robot-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" 
             onclick="inspectAgent('{{ name }}', '{{ data.role }}', '{{ data.status }}')">
            <div class="robot-icon" style="border-color: {{ data.color }};">🤖</div>
            <div class="robot-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}

        <div id="status-bar">💡 Ofisi izlemek için ajanların üzerine tıkla. Ekip kendi arasında hareket ediyor...</div>
    </div>

    <script>
        const statusBar = document.getElementById('status-bar');

        function inspectAgent(name, role, status) {
            statusBar.innerHTML = `<strong>👤 Ajan:</strong> ${name} &nbsp;|&nbsp; <strong>💼 Görev:</strong> ${role} &nbsp;|&nbsp; <span style="color: #58a6ff;">● Durum:</span> ${status}`;
        }

        // Akıllı Yürüyüş Simülasyonu: Ajanlar masaları, koridorları ve mola/kahve alanlarını turluyor
        const locations = [
            {x: 100, y: 100}, {x: 280, y: 100}, {x: 460, y: 100}, {x: 640, y: 100}, {x: 820, y: 100},
            {x: 100, y: 380}, {x: 280, y: 380}, {x: 460, y: 380}, {x: 640, y: 380},
            {x: 830, y: 60},  // Mutfak kahve alanı
            {x: 830, y: 420}, // Dinlenme / Oyun alanı
            {x: 360, y: 260}  // Orta koridor mola noktası
        ];

        setInterval(() => {
            const keys = Object.keys({{ employees | tojson }});
            // Rastgele bir ajan seçip ofis içinde başka bir noktaya yürümesini sağlıyoruz
            const randomAgentName = keys[Math.floor(Math.random() * keys.length)];
            const robotElement = document.getElementById('robot-' + randomAgentName);
            
            if (robotElement) {
                const randomLoc = locations[Math.floor(Math.random() * locations.length)];
                robotElement.style.left = randomLoc.x + 'px';
                robotElement.style.top = randomLoc.y + 'px';
            }
        }, 3500);
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
