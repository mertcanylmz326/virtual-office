import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Odaları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek Odası", "home_x": 90, "home_y": 70, "color": "#3b82f6", "bubble": "Destek hattında..."},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon Odası", "home_x": 270, "home_y": 70, "color": "#ef4444", "bubble": "Sipariş işliyor"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım Üssü", "home_x": 560, "home_y": 70, "color": "#10b981", "bubble": "Kod derleniyor..."},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama Odası", "home_x": 740, "home_y": 70, "color": "#f59e0b", "bubble": "Kampanya kurguluyor"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans Odası", "home_x": 740, "home_y": 330, "color": "#8b5cf6", "bubble": "Bütçe kontrolü"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK Odası", "home_x": 90, "home_y": 330, "color": "#f97316", "bubble": "Mülakatta..."},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk Bürosu", "home_x": 270, "home_y": 330, "color": "#14b8a6", "bubble": "Sözleşme inceliyor"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik Odası", "home_x": 540, "home_y": 330, "color": "#64748b", "bubble": "Sistem taranıyor"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı Odası", "home_x": 710, "home_y": 330, "color": "#ec4899", "bubble": "Onboarding aktif"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Pixel Robot HQ</title>
    <style>
        body { 
            background-color: #05070b; 
            color: #fff; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
        }
        
        #game-topbar {
            background: #0f172a;
            border-bottom: 3px solid #1e293b;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }
        .top-btn { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 4px 10px; border-radius: 4px; font-weight: bold; }

        /* Harbi Parke Zemin (Ahşap Parke Görsel Dokusu) */
        #office-floor { 
            position: relative; 
            width: 920px; 
            height: 480px; 
            margin: 10px auto; 
            background-color: #2c1d11;
            background-image: 
                linear-gradient(90deg, rgba(255,255,255,0.06) 2px, transparent 2px),
                linear-gradient(rgba(0,0,0,0.35) 2px, transparent 2px),
                linear-gradient(0deg, rgba(139, 69, 19, 0.2) 0%, rgba(0,0,0,0.5) 100%);
            background-size: 60px 30px;
            border: 6px solid #1e293b; 
            border-radius: 10px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.95); 
            overflow: hidden;
        }

        /* Odalar */
        .hq-room {
            position: absolute;
            border: 4px solid #334155;
            background: rgba(30, 20, 14, 0.92);
            border-radius: 6px;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.7);
        }
        .hq-room-title {
            position: absolute;
            font-size: 7px;
            color: #94a3b8;
            top: 4px;
            left: 6px;
            font-weight: bold;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        /* Kapılar */
        .hq-door {
            position: absolute;
            background: #78350f;
            border: 2px solid #451a03;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 6px;
            color: #fde68a;
            font-weight: bold;
            box-shadow: 0 0 8px rgba(0,0,0,0.8);
        }

        /* Masalar ve Monitörler */
        .desk { position: absolute; width: 50px; height: 26px; background: #1c1917; border: 2px solid #44403c; border-radius: 3px; }
        .pc-monitor { position: absolute; width: 18px; height: 10px; background: #38bdf8; top: 4px; left: 16px; border-radius: 2px; box-shadow: 0 0 8px #38bdf8; }
        
        /* Ortak Mola Alanı */
        .lounge-area {
            position: absolute;
            left: 410px;
            top: 200px;
            width: 100px;
            height: 80px;
            background: rgba(14, 165, 233, 0.12);
            border: 2px dashed #0284c7;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            color: #38bdf8;
            font-weight: bold;
        }

        /* CEO Koltuğu */
        .ceo-hq {
            position: absolute;
            left: 425px;
            top: 105px;
            width: 70px;
            height: 70px;
            background: radial-gradient(circle, #dc2626 0%, #7f1d1d 100%);
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 25px rgba(220, 38, 38, 0.9);
            z-index: 50;
        }

        /* Piksel Robot Karakterler (Ayak Adımları / Yürüme Animasyonlu) */
        .agent { 
            position: absolute; 
            width: 45px; 
            height: 55px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2.2s cubic-bezier(0.4, 0, 0.2, 1), top 2.2s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 30;
        }
        
        .robot-sprite {
            width: 32px;
            height: 32px;
            background-color: #18181b;
            border: 2px solid;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.8);
            animation: robotStep 0.4s infinite alternate; /* Gerçek ayak adımları / yürüme efekti */
        }

        .agent-name {
            font-size: 7px;
            font-weight: bold;
            background: rgba(15, 23, 42, 0.95);
            padding: 1px 3px;
            border-radius: 3px;
            margin-top: 2px;
            white-space: nowrap;
            border: 1px solid #475569;
        }
        
        .speech-bubble {
            position: absolute;
            top: -22px;
            background: #f8fafc;
            color: #0f172a;
            font-size: 6px;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 4px;
            white-space: nowrap;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            pointer-events: none;
        }

        .agent:hover { transform: scale(1.3); z-index: 100; }

        @keyframes robotStep {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-4px) rotate(2deg); }
        }

        #game-console {
            margin: 8px auto;
            width: 910px;
            background: #0f172a;
            border: 2px solid #334155;
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

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - PIXEL ROBOT EDITION</div>
        <div>
            <span class="top-btn">CEO: MERTCAN</span>
            <span class="top-btn" style="color: #34d399;">YÜRÜYEN PİKSEL ROBOTLAR AKTİF</span>
        </div>
    </div>

    <div id="office-floor">
        <!-- Odalar -->
        <div class="hq-room" style="left: 15px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">MARCO (DESTEK)</div></div>
        <div class="hq-room" style="left: 225px; top: 15px; width: 195px; height: 215px;"><div class="hq-room-title">TALİSCA (SİPARİŞ)</div></div>
        <div class="hq-room" style="left: 495px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">BROWN (YAZILIM)</div></div>
        <div class="hq-room" style="left: 705px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">KANTE (PAZARLAMA)</div></div>
        <div class="hq-room" style="left: 15px; top: 255px; width: 200px; height: 215px;"><div class="hq-room-title">İSMAİL (İK)</div></div>
        <div class="hq-room" style="left: 225px; top: 255px; width: 195px; height: 215px;"><div class="hq-room-title">ALEX (HUKUK)</div></div>
        <div class="hq-room" style="left: 495px; top: 255px; width: 130px; height: 215px;"><div class="hq-room-title">SKRİNAR (SİBER)</div></div>
        <div class="hq-room" style="left: 635px; top: 255px; width: 130px; height: 215px;"><div class="hq-room-title">KEREM (BAŞARI)</div></div>
        <div class="hq-room" style="left: 775px; top: 255px; width: 130px; height: 215px;"><div class="hq-room-title">İRFAN (FİNANS)</div></div>

        <!-- Kapılar -->
        <div class="hq-door" style="left: 425px; top: 110px; width: 65px; height: 15px;">KAPI</div>
        <div class="hq-door" style="left: 425px; top: 350px; width: 65px; height: 15px;">KAPI</div>

        <!-- Mola Alanı -->
        <div class="lounge-area">
            ☕ ORTAK MOLA
        </div>

        <!-- Masalar -->
        <div class="desk" style="left: 90px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 295px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 570px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 770px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 90px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 295px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 535px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 675px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 815px; top: 315px;"><div class="pc-monitor"></div></div>

        <!-- CEO Makamı -->
        <div class="ceo-hq">
            <span>👑 SEN</span>
            <span style="font-size: 7px; color: #fca5a5;">CEO</span>
        </div>

        <!-- Ajanlar -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.home_x }}px; top: {{ data.home_y }}px;" 
             onclick="selectAgent('{{ name }}', '{{ data.role }}', '{{ data.room }}', '{{ data.bubble }}')">
            <div class="speech-bubble">{{ data.bubble }}</div>
            <div class="robot-sprite" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <div id="game-console">
        > [SİSTEM]: Gerçek ahşap parke zemin, piksel robot sprite'ları, yürüme animasyonları ve özel odalar tam formunda yüklendi!
    </div>

    <script>
        const consoleBox = document.getElementById('game-console');

        function selectAgent(name, role, room, bubble) {
            consoleBox.innerHTML = `> [AJAN RAPORU] <b>${name}</b> (${role}) | Oda: <b>${room}</b> | Durum: <i>"${bubble}"</i>`;
        }

        const employeesData = {{ employees | tojson }};
        const loungeSpots = [
            {x: 430, y: 225}, {x: 450, y: 245}, {x: 470, y: 225}
        ];

        setInterval(() => {
            const keys = Object.keys(employeesData);
            const randomAgentKey = keys[Math.floor(Math.random() * keys.length)];
            const agentEl = document.getElementById('agent-' + randomAgentKey);
            const data = employeesData[randomAgentKey];

            if (agentEl) {
                if (Math.random() > 0.4) {
                    agentEl.style.left = data.home_x + 'px';
                    agentEl.style.top = data.home_y + 'px';
                } else {
                    const spot = loungeSpots[Math.floor(Math.random() * loungeSpots.length)];
                    agentEl.style.left = spot.x + 'px';
                    agentEl.style.top = spot.y + 'px';
                }
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
