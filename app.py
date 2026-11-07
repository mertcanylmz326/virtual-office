import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız, Konumları ve Canlı Konuşma Balonları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek", "home_x": 75, "home_y": 70, "color": "#3b82f6", "bubble": "Destek hattında..."},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon", "home_x": 250, "home_y": 70, "color": "#ef4444", "bubble": "Sipariş işliyor"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım", "home_x": 550, "home_y": 70, "color": "#10b981", "bubble": "Kod derleniyor..."},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama", "home_x": 730, "home_y": 70, "color": "#f59e0b", "bubble": "Kampanya kurguluyor"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans", "home_x": 730, "home_y": 320, "color": "#8b5cf6", "bubble": "Bütçe kontrolü"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK", "home_x": 75, "home_y": 320, "color": "#f97316", "bubble": "Mülarette..."},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk", "home_x": 250, "home_y": 320, "color": "#14b8a6", "bubble": "Sözleşme inceliyor"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik", "home_x": 530, "home_y": 320, "color": "#64748b", "bubble": "Sistem taranıyor"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı", "home_x": 700, "home_y": 320, "color": "#ec4899", "bubble": "Onboarding aktif"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Ultimate RPG HQ</title>
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

        /* Harbi Parke Zeminli Ofis Katı */
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

        /* Neon Odalar */
        .hq-room {
            position: absolute;
            border: 3px solid #475569;
            background: rgba(24, 18, 14, 0.9);
            border-radius: 6px;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
        }
        .hq-room-title {
            position: absolute;
            font-size: 8px;
            color: #94a3b8;
            top: 4px;
            left: 8px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        /* Kapılar */
        .hq-door {
            position: absolute;
            background: #92400e;
            border: 1px solid #78350f;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 7px;
            color: #fde68a;
            font-weight: bold;
        }

        /* Masalar ve Monitörler */
        .desk { position: absolute; width: 55px; height: 28px; background: #27272a; border: 1px solid #52525b; border-radius: 3px; }
        .pc-monitor { position: absolute; width: 20px; height: 12px; background: #38bdf8; top: 4px; left: 17px; border-radius: 2px; box-shadow: 0 0 6px #38bdf8; }
        
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

        /* Ajan Karakterler ve Konuşma Balonları */
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
            font-size: 15px;
            background: #18181b;
            border-radius: 50%;
            width: 30px;
            height: 30px;
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
        
        /* Canlı Konuşma Balonu */
        .speech-bubble {
            position: absolute;
            top: -22px;
            background: #f8fafc;
            color: #0f172a;
            font-size: 6px;
            font-weight: bold;
            padding: 2px 5px;
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

        /* Yönetim Paneli / Konsol */
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
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - ULTIMATE RPG EDITION</div>
        <div>
            <span class="top-btn">CEO: MERTCAN</span>
            <span class="top-btn" style="color: #34d399;">KONUŞMA BALONLARI AKTİF</span>
        </div>
    </div>

    <div id="office-floor">
        <!-- Odalar -->
        <div class="hq-room" style="left: 15px; top: 15px; width: 410px; height: 215px;">
            <div class="hq-room-title">DESTEK & OPERASYON ODASI</div>
        </div>
        <div class="hq-room" style="left: 495px; top: 15px; width: 410px; height: 215px;">
            <div class="hq-room-title">YAZILIM & PAZARLAMA ODASI</div>
        </div>
        <div class="hq-room" style="left: 15px; top: 265px; width: 410px; height: 215px;">
            <div class="hq-room-title">HUKUK & İK BÜROSU</div>
        </div>
        <div class="hq-room" style="left: 495px; top: 265px; width: 410px; height: 215px;">
            <div class="hq-room-title">FİNANS & GÜVENLİK ODASI</div>
        </div>

        <!-- Kapılar -->
        <div class="hq-door" style="left: 430px; top: 110px; width: 60px; height: 15px;">KAPI</div>
        <div class="hq-door" style="left: 430px; top: 360px; width: 60px; height: 15px;">KAPI</div>

        <!-- Mola Alanı -->
        <div class="lounge-area">
            ☕ ORTAK MOLA
        </div>

        <!-- Masalar -->
        <div class="desk" style="left: 60px; top: 65px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 240px; top: 65px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 540px; top: 65px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 720px; top: 65px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 60px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 240px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 520px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 700px; top: 315px;"><div class="pc-monitor"></div></div>

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
        > [YÖNETİM PANELİ]: Konuşma balonları eklendi. Ajanlar kendi odalarında çalışıp sadece mola alanında buluşuyor. Detay için tıklayın.
    </div>

    <script>
        const consoleBox = document.getElementById('game-console');

        function selectAgent(name, role, room, bubble) {
            consoleBox.innerHTML = `> [AJAN RAPORU] <b>${name}</b> (${role}) | Oda: <b>${room}</b> | Anlık Durum: <i>"${bubble}"</i> -> Sistem Verimliliği: %98.4`;
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
                if (Math.random() > 0.5) {
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
