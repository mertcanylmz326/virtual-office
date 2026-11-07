import os
from flask import Flask, render_template_string

app = FlaskName = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Ofis İçi Konumları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek", "x": 100, "y": 90, "color": "#3498db"},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon", "x": 280, "y": 90, "color": "#e74c3c"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım", "x": 540, "y": 90, "color": "#2ecc71"},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama", "x": 730, "y": 90, "color": "#f1c40f"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans", "x": 730, "y": 340, "color": "#9b59b6"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK", "x": 100, "y": 340, "color": "#e67e22"},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk", "x": 280, "y": 340, "color": "#1abc9c"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik", "x": 460, "y": 340, "color": "#34495e"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı", "x": 600, "y": 340, "color": "#e84393"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Ultimate HQ</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: 'Courier New', Courier, monospace; text-align: center; margin: 0; padding: 5px; overflow: hidden; }
        
        /* Üst Menü Paneli (O adamınki gibi üst bar) */
        #top-bar {
            background: #161b22;
            border-bottom: 2px solid #30363d;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }
        .nav-btn { background: #21262d; padding: 4px 8px; border-radius: 4px; color: #58a6ff; border: 1px solid #30363d; font-weight: bold; }

        /* Ofis Katı Haritası (Detaylı Zemin ve Odalar) */
        #office-floor { 
            position: relative; 
            width: 920px; 
            height: 490px; 
            margin: 10px auto; 
            background: #0f141d; 
            border: 4px solid #30363d; 
            border-radius: 8px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.8); 
            overflow: hidden;
            background-image: 
                linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
            background-size: 30px 30px;
        }

        /* Odalar ve Kalın Duvarlar */
        .office-room {
            position: absolute;
            border: 2px solid #30363d;
            background: rgba(22, 27, 34, 0.75);
            border-radius: 6px;
        }
        .room-title {
            position: absolute;
            font-size: 8px;
            color: #8b949e;
            top: 4px;
            left: 8px;
            letter-spacing: 1px;
            font-weight: bold;
        }

        /* Detaylı Ofis Eşyaları (Masalar, Bilgisayarlar, Su Sebili, Bitkiler) */
        .desk { position: absolute; width: 65px; height: 35px; background: #21262d; border: 1px solid #484f58; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.4); }
        .pc-monitor { position: absolute; width: 25px; height: 15px; background: #58a6ff; border-radius: 2px; top: 5px; left: 20px; box-shadow: 0 0 5px #58a6ff; }
        .plant { position: absolute; font-size: 14px; }
        .water-cooler { position: absolute; width: 20px; height: 30px; background: #0366d6; border-radius: 3px; display: flex; align-items: center; justify-content: center; font-size: 8px; border: 1px solid #79c0ff; }
        .coffee-corner { position: absolute; width: 35px; height: 35px; background: #b08800; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 11px; }

        /* CEO Karakteri (Sen - Ortada) */
        .ceo-avatar {
            position: absolute;
            left: 425px;
            top: 205px;
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #f85149, #b62324);
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 20px rgba(248, 81, 73, 0.9);
            z-index: 50;
        }

        /* Ajanlar / Piksel Robot Karakterler */
        .agent { 
            position: absolute; 
            width: 50px; 
            height: 50px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2s ease-in-out, top 2s ease-in-out;
            z-index: 20;
        }
        .agent-avatar {
            font-size: 16px;
            background: #21262d;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid;
            box-shadow: 0 3px 6px rgba(0,0,0,0.6);
        }
        .agent-name {
            font-size: 8px;
            font-weight: bold;
            background: rgba(13, 17, 23, 0.95);
            padding: 1px 4px;
            border-radius: 3px;
            margin-top: 1px;
            white-space: nowrap;
            border: 1px solid #30363d;
        }
        .agent:hover { transform: scale(1.3); z-index: 100; }

        /* Alt Durum Ekranı */
        #status-console {
            margin: 8px auto;
            width: 910px;
            background: #161b22;
            border: 1px solid #30363d;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            color: #38bdf8;
            text-align: left;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
    </style>
</head>
<body>

    <!-- Üst Bar -->
    <div id="top-bar">
        <div style="font-weight: bold; color: #58a6ff;">⚡ E-TRADE PRO HQ v3.0</div>
        <div>
            <span class="nav-btn">LİDER: MERTCAN (CEO)</span>
            <span class="nav-btn" style="color: #2ea043;">9/9 AJAN AKTİF</span>
        </div>
    </div>

    <!-- Ofis Haritası -->
    <div id="office-floor">
        <!-- Odalar -->
        <div class="office-room" style="left: 15px; top: 15px; width: 420px; height: 210px;">
            <div class="room-title">OPERASYON & DESTEK KANADI</div>
        </div>
        <div class="office-room" style="left: 485px; top: 15px; width: 420px; height: 210px;">
            <div class="room-title">YAZILIM & PAZARLAMA ÜSSÜ</div>
        </div>
        <div class="office-room" style="left: 15px; top: 255px; width: 420px; height: 210px;">
            <div class="room-title">HUKUK & İK BÜROSU</div>
        </div>
        <div class="office-room" style="left: 485px; top: 255px; width: 420px; height: 210px;">
            <div class="room-title">FİNANS & SİBER GÜVENLİK MERKEZİ</div>
        </div>

        <!-- Dekoratif Eşyalar ve Detaylar -->
        <div class="plant" style="left: 25px; top: 30px;">🪴</div>
        <div class="plant" style="left: 870px; top: 30px;">🪴</div>
        <div class="water-cooler" style="left: 445px; top: 95px;" title="Su Sebili">💧</div>
        <div class="coffee-corner" style="left: 445px; top: 320px;" title="Kahve Alanı">☕</div>

        <!-- Masalar ve Bilgisayar Ekranları -->
        <div class="desk" style="left: 85px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 265px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 525px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 715px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 85px; top: 320px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 265px; top: 320px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 445px; top: 320px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 580px; top: 320px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 715px; top: 320px;"><div class="pc-monitor"></div></div>

        <!-- CEO (Sen) -->
        <div class="ceo-avatar">
            <span>👑 SEN</span>
            <span style="font-size: 7px; color: #fca5a5;">CEO</span>
        </div>

        <!-- Ajanlar -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" 
             onclick="inspectAgent('{{ name }}', '{{ data.role }}', '{{ data.room }}')">
            <div class="agent-avatar" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <!-- Alt Konsol -->
    <div id="status-console">
        > [SİSTEM]: Detaylı HQ ofis haritası yüklendi. Ajanlar odalarında ve koridorlarda aktif devriye geziyor. Detay için tıklayın patron.
    </div>

    <script>
        const consoleBox = document.getElementById('status-console');

        function inspectAgent(name, role, room) {
            consoleBox.innerHTML = `> [AJAN SEÇİLDİ] İsim: <b>${name}</b> | Görev: <b>${role}</b> | Konum: <b>${room} Odası</b> - Aktif Çalışıyor.`;
        }

        // Akıllı Gezinti Rotaları
        const patrolPoints = [
            {x: 85, y: 75}, {x: 265, y: 75}, {x: 525, y: 75}, {x: 715, y: 75},
            {x: 85, y: 320}, {x: 265, y: 320}, {x: 445, y: 320}, {x: 580, y: 320}, {x: 715, y: 320},
            {x: 445, y: 100}, // Su sebili
            {x: 445, y: 280}, // Koridor arası
            {x: 420, y: 210}  // CEO çevresi
        ];

        setInterval(() => {
            const keys = Object.keys({{ employees | tojson }});
            const randomAgent = keys[Math.floor(Math.random() * keys.length)];
            const el = document.getElementById('agent-' + randomAgent);
            
            if (el) {
                const target = patrolPoints[Math.floor(Math.random() * patrolPoints.length)];
                el.style.left = target.x + 'px';
                el.style.top = target.y + 'px';
            }
        }, 2200);
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
