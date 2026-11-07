import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız, Kendi Odaları ve Mola Konumları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek", "x": 90, "y": 80, "home_x": 90, "home_y": 80, "color": "#3b82f6"},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon", "x": 260, "y": 80, "home_x": 260, "home_y": 80, "color": "#ef4444"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım", "x": 560, "y": 80, "home_x": 560, "home_y": 80, "color": "#10b981"},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama", "x": 730, "y": 80, "home_x": 730, "home_y": 80, "color": "#f59e0b"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans", "x": 730, "y": 340, "home_x": 730, "home_y": 340, "color": "#8b5cf6"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK", "x": 90, "y": 340, "home_x": 90, "home_y": 340, "color": "#f97316"},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk", "x": 260, "y": 340, "home_x": 260, "home_y": 340, "color": "#14b8a6"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik", "x": 530, "y": 340, "home_x": 530, "home_y": 340, "color": "#64748b"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı", "x": 700, "y": 340, "home_x": 700, "home_y": 340, "color": "#ec4899"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Strict Rooms & Lounge HQ</title>
    <style>
        body { 
            background-color: #0b0f17; 
            color: #fff; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
        }
        
        #game-topbar {
            background: #111827;
            border-bottom: 3px solid #1f2937;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }
        .top-btn { background: #1f2937; color: #38bdf8; border: 1px solid #374151; padding: 4px 10px; border-radius: 4px; font-weight: bold; }

        /* Harbi Parke Zeminli Ofis Katı */
        #office-floor { 
            position: relative; 
            width: 920px; 
            height: 490px; 
            margin: 10px auto; 
            background-color: #271c14; /* Gerçek ahşap parke baz rengi */
            background-image: 
                linear-gradient(90deg, rgba(255,255,255,0.04) 1px, transparent 1px),
                linear-gradient(rgba(0,0,0,0.25) 1px, transparent 1px);
            background-size: 50px 25px; /* Parke tahta deseni */
            border: 5px solid #374151; 
            border-radius: 8px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.9); 
            overflow: hidden;
        }

        /* Kalın Duvarlı Odalar */
        .hq-room {
            position: absolute;
            border: 3px solid #4b5563;
            background: rgba(30, 24, 19, 0.85);
            border-radius: 6px;
        }
        .hq-room-title {
            position: absolute;
            font-size: 8px;
            color: #9ca3af;
            top: 4px;
            left: 8px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        /* Açılır Kapanır Kapılar */
        .hq-door {
            position: absolute;
            background: #b45309;
            border: 1px solid #78350f;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 7px;
            color: #fde68a;
            font-weight: bold;
            box-shadow: 0 0 5px rgba(0,0,0,0.6);
        }

        /* Çalışma Masaları ve Monitörler */
        .desk { position: absolute; width: 65px; height: 35px; background: #3f3f46; border: 1px solid #71717a; border-radius: 4px; }
        .pc-monitor { position: absolute; width: 25px; height: 15px; background: #38bdf8; top: 5px; left: 20px; border-radius: 2px; box-shadow: 0 0 6px #38bdf8; }
        
        /* Ortak Dinlenme & Mola Alanı (Su Sebili / Kahve) */
        .lounge-area {
            position: absolute;
            left: 410px;
            top: 200px;
            width: 100px;
            height: 90px;
            background: rgba(2, 132, 199, 0.15);
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

        /* CEO (Sen) */
        .ceo-hq {
            position: absolute;
            left: 425px;
            top: 105px;
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #dc2626, #7f1d1d);
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 20px rgba(220, 38, 38, 0.9);
            z-index: 50;
        }

        /* Ajan Karakterler */
        .agent { 
            position: absolute; 
            width: 50px; 
            height: 55px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2s cubic-bezier(0.4, 0, 0.2, 1), top 2s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 30;
        }
        .agent-avatar {
            font-size: 16px;
            background: #18181b;
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid;
            box-shadow: 0 3px 6px rgba(0,0,0,0.6);
            animation: bounceWalk 0.5s infinite alternate;
        }
        .agent-name {
            font-size: 8px;
            font-weight: bold;
            background: rgba(11, 15, 23, 0.95);
            padding: 1px 4px;
            border-radius: 3px;
            margin-top: 1px;
            white-space: nowrap;
            border: 1px solid #4b5563;
        }
        .agent:hover { transform: scale(1.3); z-index: 100; }

        @keyframes bounceWalk {
            0% { transform: translateY(0px); }
            100% { transform: translateY(-3px); }
        }

        #game-console {
            margin: 8px auto;
            width: 910px;
            background: #111827;
            border: 2px solid #1f2937;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            color: #10b981;
            text-align: left;
        }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - PARKE ZEMİN & STRICT ROOMS</div>
        <div>
            <span class="top-btn">CEO: MERTCAN</span>
            <span class="top-btn" style="color: #34d399;">9/9 AJAN KENDİ ODASINDA</span>
        </div>
    </div>

    <div id="office-floor">
        <!-- Odalar -->
        <div class="hq-room" style="left: 15px; top: 15px; width: 420px; height: 215px;">
            <div class="hq-room-title">DESTEK & OPERASYON ODASI</div>
        </div>
        <div class="hq-room" style="left: 485px; top: 15px; width: 420px; height: 215px;">
            <div class="hq-room-title">YAZILIM & PAZARLAMA ODASI</div>
        </div>
        <div class="hq-room" style="left: 15px; top: 265px; width: 420px; height: 215px;">
            <div class="hq-room-title">HUKUK & İK BÜROSU</div>
        </div>
        <div class="hq-room" style="left: 485px; top: 265px; width: 420px; height: 215px;">
            <div class="hq-room-title">FİNANS & GÜVENLİK ODASI</div>
        </div>

        <!-- Odaların Açılır Kapanır Kapıları -->
        <div class="hq-door" style="left: 435px; top: 110px; width: 50px; height: 15px;">KAPI</div>
        <div class="hq-door" style="left: 435px; top: 360px; width: 50px; height: 15px;">KAPI</div>

        <!-- Ortak Dinlenme & Mola Alanı (Sadece burada bir araya geliyorlar) -->
        <div class="lounge-area">
            ☕ DİNLENME & MOLA
        </div>

        <!-- Masalar -->
        <div class="desk" style="left: 70px; top: 70px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 240px; top: 70px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 540px; top: 70px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 710px; top: 70px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 70px; top: 325px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 240px; top: 325px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 510px; top: 325px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 610px; top: 325px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 710px; top: 325px;"><div class="pc-monitor"></div></div>

        <!-- CEO Makamı -->
        <div class="ceo-hq">
            <span>👑 SEN</span>
            <span style="font-size: 7px; color: #fca5a5;">CEO</span>
        </div>

        <!-- Ajanlar -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" 
             onclick="selectAgent('{{ name }}', '{{ data.role }}', '{{ data.room }}')">
            <div class="agent-avatar" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <div id="game-console">
        > [SİSTEM]: Herkes kendi odasında çalışıyor. Sadece orta alandaki Dinlenme/Mola köşesinde bir araya geliyorlar. Parke zemin ve kapılar aktif!
    </div>

    <script>
        const consoleBox = document.getElementById('game-console');

        function selectAgent(name, role, room) {
            consoleBox.innerHTML = `> [AJAN SEÇİLDİ]: <b>${name}</b> (${role}) -> Kendi Odası: <b>${room}</b>`;
        }

        // Ajanların kendi odaları ve ortak dinlenme alanı arasındaki rotaları
        // (Asla birbirlerinin özel odalarına girmiyorlar, ya kendi masalarındalar ya da mola alanındalar)
        const employeesData = {{ employees | tojson }};
        const loungeSpots = [
            {x: 430, y: 220}, {x: 450, y: 240}, {x: 470, y: 220} // Dinlenme alanı koordinatları
        ];

        setInterval(() => {
            const keys = Object.keys(employeesData);
            const randomAgentKey = keys[Math.floor(Math.random() * keys.length)];
            const agentEl = document.getElementById('agent-' + randomAgentKey);
            const data = employeesData[randomAgentKey];

            if (agentEl) {
                // %50 ihtimalle kendi masasında, %50 ihtimalle mola alanında
                if (Math.random() > 0.5) {
                    agentEl.style.left = data.home_x + 'px';
                    agentEl.style.top = data.home_y + 'px';
                } else {
                    const spot = loungeSpots[Math.floor(Math.random() * loungeSpots.length)];
                    agentEl.style.left = spot.x + 'px';
                    agentEl.style.top = spot.y + 'px';
                }
            }
        }, 3000);
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
