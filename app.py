import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız, Başlangıç ve Gezinti Hedefleri (Ofis İçi Koordinatlar)
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek", "x": 100, "y": 100, "color": "#3498db"},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon", "x": 280, "y": 100, "color": "#e74c3c"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım", "x": 560, "y": 100, "color": "#2ecc71"},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama", "x": 750, "y": 100, "color": "#f1c40f"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans", "x": 750, "y": 380, "color": "#9b59b6"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK", "x": 100, "y": 380, "color": "#e67e22"},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk", "x": 280, "y": 380, "color": "#1abc9c"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik", "x": 500, "y": 380, "color": "#34495e"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı", "x": 640, "y": 380, "color": "#e84393"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Akıllı HQ Simülatörü</title>
    <style>
        body { background-color: #030712; color: #f8fafc; font-family: 'Courier New', Courier, monospace; text-align: center; margin: 0; padding: 10px; overflow: hidden; }
        
        #top-bar {
            background: #0f172a;
            border-bottom: 2px solid #3b82f6;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.6);
        }
        .badge { background: #1e293b; padding: 4px 8px; border-radius: 4px; color: #38bdf8; border: 1px solid #334155; }

        #office-map { 
            position: relative; 
            width: 920px; 
            height: 500px; 
            margin: 15px auto; 
            background: #090d16; 
            border: 4px solid #334155; 
            border-radius: 12px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.9); 
            overflow: hidden;
        }

        /* Odalar ve Duvarlar */
        .room {
            position: absolute;
            border: 2px solid #334155;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 8px;
        }
        .room-tag {
            position: absolute;
            font-size: 9px;
            color: #64748b;
            top: 5px;
            left: 10px;
            letter-spacing: 1px;
            font-weight: bold;
        }

        /* Ofis Eşyaları */
        .desk { position: absolute; width: 60px; height: 30px; background: #1e293b; border: 1px solid #475569; border-radius: 4px; }
        .plant { position: absolute; font-size: 15px; }
        .water-cooler { position: absolute; width: 24px; height: 32px; background: #0284c7; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 9px; border: 1px solid #bae6fd; }
        .coffee-machine { position: absolute; width: 30px; height: 30px; background: #78350f; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; border: 1px solid #fbbf24; }

        /* CEO (Mertcan) Merkezi Nokta */
        .ceo-node {
            position: absolute;
            left: 430px;
            top: 215px;
            width: 65px;
            height: 65px;
            background: linear-gradient(135deg, #dc2626, #7f1d1d);
            border: 2px solid #fff;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(220, 38, 38, 0.8);
            z-index: 50;
        }

        /* Gezinen Ajanlar */
        .agent { 
            position: absolute; 
            width: 50px; 
            height: 50px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2.5s ease-in-out, top 2.5s ease-in-out; /* Akıcı yürüme geçişi */
            z-index: 20;
        }
        .agent-avatar {
            font-size: 16px;
            background: #1e293b;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid;
            box-shadow: 0 3px 6px rgba(0,0,0,0.5);
        }
        .agent-name {
            font-size: 8px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.9);
            padding: 1px 3px;
            border-radius: 3px;
            margin-top: 1px;
            white-space: nowrap;
            border: 1px solid #475569;
        }
        .agent:hover { transform: scale(1.3); z-index: 100; }

        #footer-panel {
            margin: 10px auto;
            width: 910px;
            background: #0f172a;
            border: 1px solid #334155;
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

    <div id="top-bar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - CANLI OFİS SİMÜLASYONU</div>
        <div>
            <span class="badge">CEO: Mertcan</span>
            <span class="badge" style="color: #10b981;">Durum: Canlı Gezinti Aktif</span>
        </div>
    </div>

    <div id="office-map">
        <!-- Odalar -->
        <div class="room" style="left: 15px; top: 15px; width: 420px; height: 215px;">
            <div class="room-tag">OPERASYON & DESTEK KANADI</div>
        </div>
        <div class="room" style="left: 485px; top: 15px; width: 420px; height: 215px;">
            <div class="room-tag">YAZILIM & PAZARLAMA ÜSSÜ</div>
        </div>
        <div class="room" style="left: 15px; top: 265px; width: 420px; height: 215px;">
            <div class="room-tag">HUKUK & İK BÜROSU</div>
        </div>
        <div class="room" style="left: 485px; top: 265px; width: 420px; height: 215px;">
            <div class="room-tag">FİNANS & GÜVENLİK MERKEZİ</div>
        </div>

        <!-- Ofis Eşyaları -->
        <div class="plant" style="left: 25px; top: 30px;">🪴</div>
        <div class="plant" style="left: 870px; top: 30px;">🪴</div>
        <div class="water-cooler" style="left: 445px; top: 100px;" title="Su Sebili">💧</div>
        <div class="coffee-machine" style="left: 445px; top: 350px;" title="Kahve Makinesi">☕</div>

        <!-- Sabit Masalar -->
        <div class="desk" style="left: 80px; top: 85px;"></div>
        <div class="desk" style="left: 250px; top: 85px;"></div>
        <div class="desk" style="left: 540px; top: 85px;"></div>
        <div class="desk" style="left: 720px; top: 85px;"></div>
        <div class="desk" style="left: 80px; top: 340px;"></div>
        <div class="desk" style="left: 250px; top: 340px;"></div>
        <div class="desk" style="left: 470px; top: 340px;"></div>
        <div class="desk" style="left: 610px; top: 340px;"></div>
        <div class="desk" style="left: 720px; top: 340px;"></div>

        <!-- CEO -->
        <div class="ceo-node">
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

    <div id="footer-panel">
        > [CANLI AKIŞ]: Ajanlar odalarında çalışıyor ve ofis içinde (su sebili, kahve molası, koridorlar) geziniyor. Detay için tıklayın.
    </div>

    <script>
        const footer = document.getElementById('footer-panel');

        function inspectAgent(name, role, room) {
            footer.innerHTML = `> [AJAN İNCELENDİ] <b>${name}</b> (${role}) -> Odası: <b>${room}</b> | Durum: Ofis içinde aktif hareket halinde.`;
        }

        // Ofis İçi Gezinti Noktaları (Masalar, Su Sebili, Kahve, Koridor)
        const waypoints = [
            {x: 90, y: 80}, {x: 260, y: 80}, {x: 550, y: 80}, {x: 730, y: 80},
            {x: 90, y: 340}, {x: 260, y: 340}, {x: 480, y: 340}, {x: 620, y: 340}, {x: 730, y: 340},
            {x: 440, y: 110}, // Su sebili noktası
            {x: 440, y: 360}, // Kahve makinesi noktası
            {x: 430, y: 220}  // CEO yanı koridor
        ];

        // Her 2.5 saniyede bir rastgele bir ajan ofis içinde rastgele bir noktaya yürür
        setInterval(() => {
            const keys = Object.keys({{ employees | tojson }});
            const randomKey = keys[Math.floor(Math.random() * keys.length)];
            const agentEl = document.getElementById('agent-' + randomKey);
            
            if (agentEl) {
                const target = waypoints[Math.floor(Math.random() * waypoints.length)];
                agentEl.style.left = target.x + 'px';
                agentEl.style.top = target.y + 'px';
            }
        }, 2500);
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
