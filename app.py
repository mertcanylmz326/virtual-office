import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Her Birine Ait Tamamen Ayrı Özel Odalar
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
    <title>E-Trade Pro - Separate Rooms HQ</title>
    <style>
        body { 
            background-color: #06090f; 
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

        /* Parke Zeminli Ofis Katı */
        #office-floor { 
            position: relative; 
            width: 920px; 
            height: 480px; 
            margin: 10px auto; 
            background-color: #20150f;
            background-image: 
                linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px),
                linear-gradient(rgba(0,0,0,0.3) 1px, transparent 1px);
            background-size: 45px 22px;
            border: 5px solid #334155; 
            border-radius: 10px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.9); 
            overflow: hidden;
        }

        /* Herkesin Ayrı Odaları */
        .hq-room {
            position: absolute;
            border: 3px solid #475569;
            background: rgba(24, 18, 14, 0.9);
            border-radius: 6px;
        }
        .hq-room-title {
            position: absolute;
            font-size: 7px;
            color: #94a3b8;
            top: 3px;
            left: 6px;
            font-weight: bold;
            letter-spacing: 0.5px;
        }

        /* Kapılar */
        .hq-door {
            position: absolute;
            background: #92400e;
            border: 1px solid #78350f;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 6px;
            color: #fde68a;
            font-weight: bold;
        }

        /* Çalışma Masaları */
        .desk { position: absolute; width: 50px; height: 26px; background: #27272a; border: 1px solid #52525b; border-radius: 3px; }
        .pc-monitor { position: absolute; width: 18px; height: 10px; background: #38bdf8; top: 4px; left: 16px; border-radius: 2px; box-shadow: 0 0 5px #38bdf8; }
        
        /* Ortak Mola Alanı */
        .lounge-area {
            position: absolute;
            left: 410px;
            top: 200px;
            width: 100px;
            height: 80px;
            background: rgba(14, 165, 233, 0.1);
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
            background: radial-gradient(circle, #ef4444 0%, #991b1b 100%);
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.9);
            z-index: 50;
        }

        /* Ajanlar */
        .agent { 
            position: absolute; 
            width: 45px; 
            height: 50px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2s cubic-bezier(0.4, 0, 0.2, 1), top 2s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 30;
        }
        .agent-avatar {
            font-size: 14px;
            background: #18181b;
            border-radius: 50%;
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid;
            box-shadow: 0 3px 6px rgba(0,0,0,0.6);
            animation: bounceWalk 0.5s infinite alternate;
        }
        .agent-name {
            font-size: 7px;
            font-weight: bold;
            background: rgba(15, 23, 42, 0.95);
            padding: 1px 3px;
            border-radius: 3px;
            margin-top: 1px;
            white-space: nowrap;
            border: 1px solid #475569;
        }
        
        .speech-bubble {
            position: absolute;
            top: -20px;
            background: #f8fafc;
            color: #0f172a;
            font-size: 6px;
            font-weight: bold;
            padding: 2px 4px;
            border-radius: 4px;
            white-space: nowrap;
            box-shadow: 0 2px 5px rgba(0,0,0,0.4);
            pointer-events: none;
        }

        .agent:hover { transform: scale(1.3); z-index: 100; }

        @keyframes bounceWalk {
            0% { transform: translateY(0px); }
            100% { transform: translateY(-3px); }
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
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - SEPARATE ROOMS EDITION</div>
        <div>
            <span class="top-btn">CEO: MERTCAN</span>
            <span class="top-btn" style="color: #34d399;">HERKESİN AYRI ODASI VAR</span>
        </div>
    </div>

    <div id="office-floor">
        <!-- Sol Üst: Marco & Talisca -->
        <div class="hq-room" style="left: 15px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">MARCO (DESTEK)</div></div>
        <div class="hq-room" style="left: 225px; top: 15px; width: 195px; height: 215px;"><div class="hq-room-title">TALİSCA (SİPARİŞ)</div></div>

        <!-- Sağ Üst: Brown & Kante -->
        <div class="hq-room" style="left: 495px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">BROWN (YAZILIM)</div></div>
        <div class="hq-room" style="left: 705px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">KANTE (PAZARLAMA)</div></div>

        <!-- Sol Alt: İsmail & Alex -->
        <div class="hq-room" style="left: 15px; top: 255px; width: 200px; height: 215px;"><div class="hq-room-title">İSMAİL (İK)</div></div>
        <div class="hq-room" style="left: 225px; top: 255px; width: 195px; height: 215px;"><div class="hq-room-title">ALEX (HUKUK)</div></div>

        <!-- Sağ Alt: Skrinar, Kerem & İrfan -->
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
            <div class="agent-avatar" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <div id="game-console">
        > [SİSTEM]: Herkesin kendine ait özel odası tanımlandı. Asla birbirlerinin odasına girmiyorlar, sadece mola alanında buluşuyorlar.
    </div>

    <script>
        const consoleBox = document.getElementById('game-console');

        function selectAgent(name, role, room, bubble) {
            consoleBox.innerHTML = `> [AJAN RAPORU] <b>${name}</b> (${role}) | Özel Odası: <b>${room}</b> | Durum: <i>"${bubble}"</i>`;
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
