import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Ofis Konumları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek", "x": 120, "y": 110, "color": "#3b82f6"},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon", "x": 300, "y": 110, "color": "#ef4444"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım Üssü", "x": 580, "y": 110, "color": "#10b981"},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama", "x": 760, "y": 110, "color": "#f59e0b"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans", "x": 760, "y": 360, "color": "#8b5cf6"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK Odası", "x": 120, "y": 360, "color": "#f97316"},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk Bürosu", "x": 300, "y": 360, "color": "#14b8a6"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik", "x": 490, "y": 360, "color": "#64748b"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı", "x": 630, "y": 360, "color": "#ec4899"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Pixel HQ Simulator</title>
    <style>
        body { 
            background-color: #1a1e24; 
            color: #fff; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow: hidden; 
        }
        
        /* O adamınki gibi üst oyun/yönetim menü barı */
        #game-topbar {
            background: #11151c;
            border-bottom: 3px solid #2d3748;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }
        .top-menu-btn {
            background: #252a34;
            color: #60a5fa;
            border: 1px solid #4a5568;
            padding: 4px 10px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
        }

        /* Piksel Ofis Katı (Açık renkli oyun zemini) */
        #pixel-hq-map { 
            position: relative; 
            width: 940px; 
            height: 500px; 
            margin: 12px auto; 
            background-color: #e2e8f0; /* Oyunlardaki gibi açık zemin */
            /* Zemin parke/karo döşeme çizgileri */
            background-image: 
                linear-gradient(rgba(0,0,0,0.06) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,0,0,0.06) 1px, transparent 1px);
            background-size: 35px 35px;
            border: 5px solid #2d3748; 
            border-radius: 8px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.8); 
            overflow: hidden;
        }

        /* Odalar ve Ahşap/Gri Bölmeler */
        .hq-room {
            position: absolute;
            border: 3px solid #cbd5e1;
            background: rgba(241, 245, 249, 0.9);
            border-radius: 6px;
        }
        .hq-room-title {
            position: absolute;
            font-size: 8px;
            color: #475569;
            top: 4px;
            left: 8px;
            font-weight: bold;
            letter-spacing: 1px;
        }

        /* Detaylı Piksel Ofis Eşyaları (Çalışma Masaları, PC'ler, Çiçekler) */
        .pixel-desk { 
            position: absolute; 
            width: 70px; 
            height: 40px; 
            background: #cbd5e1; 
            border: 2px solid #94a3b8; 
            border-radius: 4px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        }
        .pixel-pc { 
            position: absolute; 
            width: 26px; 
            height: 16px; 
            background: #0284c7; 
            top: 6px; 
            left: 22px; 
            border-radius: 2px;
            box-shadow: 0 0 5px #0284c7;
        }
        .pixel-plant { position: absolute; font-size: 16px; }
        .pixel-water { position: absolute; width: 24px; height: 34px; background: #0284c7; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #fff; border: 1px solid #bae6fd; }

        /* Ortadaki CEO (Mertcan) Karakteri */
        .ceo-character {
            position: absolute;
            left: 430px;
            top: 210px;
            width: 75px;
            height: 75px;
            background: linear-gradient(135deg, #ef4444, #991b1b);
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 10px;
            font-weight: bold;
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.9);
            z-index: 50;
            color: #fff;
        }

        /* Yürüyen Piksel Ajan Karakterler */
        .pixel-agent { 
            position: absolute; 
            width: 55px; 
            height: 60px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2s cubic-bezier(0.4, 0, 0.2, 1), top 2s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 30;
        }
        .agent-sprite {
            font-size: 18px;
            background: #fff;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 3px solid;
            box-shadow: 0 4px 8px rgba(0,0,0,0.25);
            animation: spriteWalk 0.5s infinite alternate;
        }
        .agent-tag {
            font-size: 8px;
            font-weight: bold;
            background: #1e293b;
            color: #fff;
            padding: 1px 5px;
            border-radius: 3px;
            margin-top: 2px;
            white-space: nowrap;
            border: 1px solid #475569;
        }
        .pixel-agent:hover { transform: scale(1.3); z-index: 100; }

        @keyframes spriteWalk {
            0% { transform: translateY(0px); }
            100% { transform: translateY(-4px); }
        }

        /* Alt Durum Ekranı */
        #game-console {
            margin: 10px auto;
            width: 930px;
            background: #11151c;
            border: 2px solid #2d3748;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            color: #38bdf8;
            text-align: left;
        }
    </style>
</head>
<body>

    <!-- Üst Oyun Menüsü -->
    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🎮 E-TRADE PRO AGENTS HQ v3.5</div>
        <div>
            <span class="top-menu-btn">CEO: MERTCAN</span>
            <span class="top-menu-btn" style="background: #065f46; color: #34d399;">9/9 AKTİF AJAN</span>
        </div>
    </div>

    <!-- Piksel Ofis Haritası -->
    <div id="pixel-hq-map">
        <!-- Odalar -->
        <div class="hq-room" style="left: 15px; top: 15px; width: 430px; height: 215px;">
            <div class="hq-room-title">DESTEK & OPERASYON BÖLGESİ</div>
        </div>
        <div class="hq-room" style="left: 495px; top: 15px; width: 430px; height: 215px;">
            <div class="hq-room-title">YAZILIM & PAZARLAMA MERKEZİ</div>
        </div>
        <div class="hq-room" style="left: 15px; top: 270px; width: 430px; height: 215px;">
            <div class="hq-room-title">HUKUK & İK BÜROSU</div>
        </div>
        <div class="hq-room" style="left: 495px; top: 270px; width: 430px; height: 215px;">
            <div class="hq-room-title">FİNANS & SİBER GÜVENLİK</div>
        </div>

        <!-- Dekoratif Eşyalar (Bitki, Su Sebili) -->
        <div class="pixel-plant" style="left: 25px; top: 30px;">🪴</div>
        <div class="pixel-plant" style="left: 890px; top: 30px;">🪴</div>
        <div class="pixel-water" style="left: 452px; top: 95px;" title="Su Sebili">💧</div>

        <!-- Çalışma Masaları ve Bilgisayarlar -->
        <div class="pixel-desk" style="left: 80px; top: 80px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 260px; top: 80px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 560px; top: 80px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 740px; top: 80px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 80px; top: 335px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 260px; top: 335px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 480px; top: 335px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 610px; top: 335px;"><div class="pixel-pc"></div></div>
        <div class="pixel-desk" style="left: 740px; top: 335px;"><div class="pixel-pc"></div></div>

        <!-- CEO (Sen) -->
        <div class="ceo-character">
            <span>👑 SEN</span>
            <span style="font-size: 7px; color: #fca5a5;">CEO</span>
        </div>

        <!-- Ajan Karakterler -->
        {% for name, data in employees.items() %}
        <div class="pixel-agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" 
             onclick="selectAgent('{{ name }}', '{{ data.role }}', '{{ data.room }}')">
            <div class="agent-sprite" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-tag" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <!-- Alt Konsol -->
    <div id="game-console">
        > [PİKSEL SİMÜLATÖRÜ]: Oyun tarzı renkli zemin, detaylı çalışma masaları ve yürüyüş animasyonlu ajanlar aktif edildi. İncelemek için tıkla patron.
    </div>

    <script>
        const consoleBox = document.getElementById('game-console');

        function selectAgent(name, role, room) {
            consoleBox.innerHTML = `> [AJAN SEÇİLDİ] İsim: <b>${name}</b> | Görev: <b>${role}</b> | Oda: <b>${room}</b> - Aktif olarak ofiste devriye geziyor.`;
        }

        // Ajanların ofis içinde odalar arası yürüme noktaları
        const waypoints = [
            {x: 80, y: 80},   {x: 260, y: 80},   {x: 560, y: 80},   {x: 740, y: 80},
            {x: 80, y: 335},  {x: 260, y: 335},  {x: 480, y: 335},  {x: 610, y: 335},  {x: 740, y: 335},
            {x: 450, y: 190}, // Orta koridor 1
            {x: 450, y: 290}, // Orta koridor 2
            {x: 450, y: 100}  // Su sebili yanı
        ];

        setInterval(() => {
            const keys = Object.keys({{ employees | tojson }});
            const randomAgent = keys[Math.floor(Math.random() * keys.length)];
            const agentNode = document.getElementById('agent-' + randomAgent);
            
            if (agentNode) {
                const target = waypoints[Math.floor(Math.random() * waypoints.length)];
                agentNode.style.left = target.x + 'px';
                agentNode.style.top = target.y + 'px';
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
