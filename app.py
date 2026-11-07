import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Ofis İçi Odaları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek", "x": 100, "y": 100, "color": "#3498db"},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon", "x": 280, "y": 100, "color": "#e74c3c"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım", "x": 560, "y": 100, "color": "#2ecc71"},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama", "x": 750, "y": 100, "color": "#f1c40f"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans", "x": 750, "y": 380, "color": "#9b59b6"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK", "x": 100, "y": 380, "color": "#e67e22"},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk", "x": 280, "y": 380, "color": "#1abc9c"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik", "x": 460, "y": 380, "color": "#34495e"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı", "x": 640, "y": 380, "color": "#e84393"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Ultimate RPG Office HQ</title>
    <style>
        body { background-color: #090d16; color: #f8fafc; font-family: 'Courier New', Courier, monospace; text-align: center; margin: 0; padding: 5px; overflow: hidden; }
        
        /* Üst Menü Paneli */
        #top-bar {
            background: #111827;
            border-bottom: 2px solid #374151;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }
        .nav-badge { background: #1f2937; padding: 4px 8px; border-radius: 4px; color: #10b981; border: 1px solid #4b5563; font-weight: bold; }

        /* Ofis Katı (Parke Zemin Doku Efekti) */
        #office-map { 
            position: relative; 
            width: 940px; 
            height: 500px; 
            margin: 10px auto; 
            background-color: #1a1512;
            /* Parke tahta çizgileri deseni */
            background-image: 
                linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px),
                linear-gradient(rgba(0,0,0,0.15) 1px, transparent 1px);
            background-size: 40px 20px;
            border: 4px solid #374151; 
            border-radius: 10px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.9); 
            overflow: hidden;
        }

        /* Odalar ve Cam/Ahşap Bölmeler */
        .room {
            position: absolute;
            border: 3px solid #4b5563;
            background: rgba(26, 22, 18, 0.85);
            border-radius: 6px;
        }
        .room-title {
            position: absolute;
            font-size: 8px;
            color: #9ca3af;
            top: 4px;
            left: 8px;
            letter-spacing: 1px;
            font-weight: bold;
        }

        /* Açılır Kapanır Oda Kapıları */
        .door {
            position: absolute;
            background: #b45309;
            border: 1px solid #78350f;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 7px;
            color: #fde68a;
            font-weight: bold;
            box-shadow: 0 0 5px rgba(0,0,0,0.5);
        }

        /* Detaylı Ofis Eşyaları */
        .desk { position: absolute; width: 65px; height: 35px; background: #27272a; border: 1px solid #52525b; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.4); }
        .pc-monitor { position: absolute; width: 25px; height: 15px; background: #38bdf8; border-radius: 2px; top: 5px; left: 20px; box-shadow: 0 0 6px #38bdf8; }
        .plant { position: absolute; font-size: 15px; }
        .water-cooler { position: absolute; width: 22px; height: 32px; background: #0284c7; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 9px; border: 1px solid #bae6fd; }
        .meeting-table { position: absolute; width: 120px; height: 50px; background: #292524; border: 2px solid #57534e; border-radius: 6px; left: 410px; top: 225px; display: flex; align-items: center; justify-content: center; font-size: 9px; color: #a8a29e; font-weight: bold; }

        /* CEO Makam Odası (Sen - Ortada Kral Koltuğu) */
        .ceo-hq {
            position: absolute;
            left: 430px;
            top: 215px;
            width: 80px;
            height: 80px;
            background: radial-gradient(circle, #dc2626 0%, #7f1d1d 100%);
            border: 3px solid #f87171;
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

        /* Yürüyen Ajanlar (Ayak hareket hissiyatlı zıplama/yürüme animasyonu) */
        .agent { 
            position: absolute; 
            width: 50px; 
            height: 55px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2.2s cubic-bezier(0.4, 0, 0.2, 1), top 2.2s cubic-bezier(0.4, 0, 0.2, 1);
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
            box-shadow: 0 4px 8px rgba(0,0,0,0.7);
            animation: walkBounce 0.6s infinite alternate; /* Ayak basma / yürüyüş hissiyatı */
        }
        .agent-name {
            font-size: 8px;
            font-weight: bold;
            background: rgba(9, 13, 22, 0.95);
            padding: 1px 4px;
            border-radius: 3px;
            margin-top: 2px;
            white-space: nowrap;
            border: 1px solid #52525b;
        }
        .agent:hover { transform: scale(1.35); z-index: 100; }

        @keyframes walkBounce {
            0% { transform: translateY(0px); }
            100% { transform: translateY(-3px); }
        }

        /* Alt Durum Paneli */
        #console-panel {
            margin: 8px auto;
            width: 930px;
            background: #111827;
            border: 1px solid #374151;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 11px;
            color: #10b981;
            text-align: left;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
    </style>
</head>
<body>

    <!-- Üst Bar -->
    <div id="top-bar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - PARKET ZEMİN & RPG SİMÜLATÖRÜ</div>
        <div>
            <span class="nav-badge">CEO: MERTCAN</span>
            <span class="nav-badge" style="color: #34d399;">9/9 AJAN SAHADA</span>
        </div>
    </div>

    <!-- Parke Zeminli Ofis Haritası -->
    <div id="office-map">
        <!-- Odalar -->
        <div class="room" style="left: 15px; top: 15px; width: 425px; height: 215px;">
            <div class="room-title">DESTEK & OPERASYON ODASI</div>
        </div>
        <div class="room" style="left: 500px; top: 15px; width: 425px; height: 215px;">
            <div class="room-title">YAZILIM & PAZARLAMA ÜSSÜ</div>
        </div>
        <div class="room" style="left: 15px; top: 265px; width: 425px; height: 215px;">
            <div class="room-title">HUKUK & İK BÜROsu</div>
        </div>
        <div class="room" style="left: 500px; top: 265px; width: 425px; height: 215px;">
            <div class="room-title">FİNANS & GÜVENLİK MERKEZİ</div>
        </div>

        <!-- Odaların Açılır Kapanır Kapıları -->
        <div class="door" style="left: 440px; top: 105px; width: 60px; height: 15px;">KAPI AÇIK</div>
        <div class="door" style="left: 440px; top: 355px; width: 60px; height: 15px;">KAPI AÇIK</div>

        <!-- Dekoratif Eşyalar & Bitkiler -->
        <div class="plant" style="left: 25px; top: 30px;">🪴</div>
        <div class="plant" style="left: 895px; top: 30px;">🪴</div>
        <div class="plant" style="left: 25px; top: 440px;">🪴</div>
        <div class="water-cooler" style="left: 460px; top: 40px;" title="Su Sebili">💧</div>
        
        <!-- Ortada Toplantı Masası -->
        <div class="meeting-table">STRATEJİ MASASI</div>

        <!-- Sabit Çalışma Masaları ve PC Monitörleri -->
        <div class="desk" style="left: 80px; top: 85px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 260px; top: 85px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 570px; top: 85px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 750px; top: 85px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 80px; top: 340px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 260px; top: 340px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 500px; top: 340px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 630px; top: 340px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 750px; top: 340px;"><div class="pc-monitor"></div></div>

        <!-- CEO Makam Yeri -->
        <div class="ceo-hq">
            <span>👑 SEN</span>
            <span style="font-size: 7px; color: #fca5a5;">CEO</span>
        </div>

        <!-- 9 Ajan / Karakter -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" 
             onclick="selectAgent('{{ name }}', '{{ data.role }}', '{{ data.room }}')">
            <div class="agent-avatar" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <!-- Alt Konsol -->
    <div id="console-panel">
        > [SİSTEM BAŞARILI]: Parke zemin, açılır kapanır oda kapıları ve yürüyüş animasyonlu ajanlar aktif edildi. İncelemek için karakterlere tıklayın patron.
    </div>

    <script>
        const consoleBox = document.getElementById('console-panel');

        function selectAgent(name, role, room) {
            consoleBox.innerHTML = `> [AJAN DETAYI] İsim: <b>${name}</b> | Görev: <b>${role}</b> | Oda: <b>${room}</b> - Koridorda ve odalar arasında geziniyor.`;
        }

        /* Ajanların odalar arası kapılardan geçerek koridora, toplantı masasına ve diğer odalara yürüme rotaları */
        const officeRoutes = [
            {x: 80, y: 85},   {x: 260, y: 85},   {x: 570, y: 85},   {x: 750, y: 85},
            {x: 80, y: 340},  {x: 260, y: 340},  {x: 500, y: 340},  {x: 630, y: 340},  {x: 750, y: 340},
            {x: 440, y: 190}, // Üst koridor geçişi
            {x: 440, y: 290}, // Alt koridor geçişi
            {x: 450, y: 230}, // Strateji masası çevresi
            {x: 460, y: 40}   // Su sebili noktası
        ];

        setInterval(() => {
            const keys = Object.keys({{ employees | tojson }});
            const randomAgent = keys[Math.floor(Math.random() * keys.length)];
            const agentNode = document.getElementById('agent-' + randomAgent);
            
            if (agentNode) {
                const step = officeRoutes[Math.floor(Math.random() * officeRoutes.length)];
                agentNode.style.left = step.x + 'px';
                agentNode.style.top = step.y + 'px';
            }
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
