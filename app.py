import os
from flask import Flask, render_template_string

app = Flask(__name__)

# 9 Kişilik Rüya Takımımız ve Ofis İçi Oda Konumları
employees = {
    "Marco": {"role": "Müşteri İlişkileri", "room": "Destek Odası", "x": 120, "y": 120, "color": "#3498db"},
    "Talisca": {"role": "Sipariş Takip", "room": "Operasyon", "x": 320, "y": 120, "color": "#e74c3c"},
    "Brown": {"role": "Yazılım (E-Trade Pro)", "room": "Yazılım Üssü", "x": 520, "y": 120, "color": "#2ecc71"},
    "Kante": {"role": "Pazarlama & Büyüme", "room": "Pazarlama", "x": 720, "y": 120, "color": "#f1c40f"},
    "İrfan": {"role": "Muhasebe & Finans", "room": "Finans Odası", "x": 820, "y": 380, "color": "#9b59b6"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK Departmanı", "x": 120, "y": 380, "color": "#e67e22"},
    "Alex": {"role": "Hukuk & Mevzuat", "room": "Hukuk Bürosu", "x": 320, "y": 380, "color": "#1abc9c"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik Merkezi", "x": 520, "y": 380, "color": "#34495e"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Müşteri Başarı", "x": 720, "y": 380, "color": "#e84393"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - HQ Sanal Ofis</title>
    <style>
        body { background-color: #0b0f19; color: #fff; font-family: 'Courier New', Courier, monospace; text-align: center; margin: 0; padding: 0; overflow: hidden; }
        
        /* Üst Menü Barı (Ekran görüntüsündeki gibi) */
        #top-bar {
            background: #111827;
            border-bottom: 2px solid #1f2937;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }
        .menu-items span { background: #1f2937; padding: 5px 10px; border-radius: 4px; margin-right: 5px; color: #9ca3af; border: 1px solid #374151; }
        .menu-items span.active { color: #10b981; border-color: #10b981; }

        /* Ofis Katı Haritası */
        #office-hq { 
            position: relative; 
            width: 960px; 
            height: 520px; 
            margin: 15px auto; 
            background: #111827; 
            border: 4px solid #374151; 
            border-radius: 8px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.8); 
        }

        /* Odalar ve Duvarlar */
        .room {
            position: absolute;
            border: 2px solid #374151;
            background: rgba(17, 24, 39, 0.7);
            border-radius: 6px;
        }
        .room-title {
            position: absolute;
            font-size: 10px;
            color: #6b7280;
            top: 5px;
            left: 10px;
            letter-spacing: 1px;
        }

        /* Masalar */
        .desk {
            position: absolute;
            width: 65px;
            height: 35px;
            background: #1f2937;
            border: 1px solid #4b5563;
            border-radius: 4px;
        }

        /* Karakterler / Ajanlar */
        .agent { 
            position: absolute; 
            width: 55px; 
            height: 55px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: all 0.5s ease;
            z-index: 10;
        }

        .agent-avatar {
            font-size: 20px;
            background: #1f2937;
            border-radius: 50%;
            width: 34px;
            height: 34px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid;
            box-shadow: 0 4px 6px rgba(0,0,0,0.5);
        }

        .agent-name {
            font-size: 9px;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.9);
            padding: 1px 4px;
            border-radius: 3px;
            margin-top: 2px;
            white-space: nowrap;
            border: 1px solid #4b5563;
        }

        .agent:hover {
            transform: scale(1.2);
            z-index: 100;
        }

        /* CEO (Mertcan) Karakteri */
        .ceo-avatar {
            position: absolute;
            left: 450px;
            top: 240px;
            width: 60px;
            height: 60px;
            background: #ef4444;
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: bold;
            box-shadow: 0 0 15px rgba(239, 68, 68, 0.8);
            z-index: 50;
        }

        /* Alt Durum Paneli */
        #console-log {
            margin: 10px auto;
            width: 950px;
            background: #111827;
            border: 1px solid #374151;
            padding: 10px;
            border-radius: 6px;
            font-size: 12px;
            color: #10b981;
            text-align: left;
        }
    </style>
</head>
<body>

    <!-- Üst Kontrol Paneli -->
    <div id="top-bar">
        <div style="font-weight: bold; color: #10b981;">🏢 E-TRADE PRO HQ</div>
        <div class="menu-items">
            <span class="active">Lider: Mertcan (CEO)</span>
            <span>Operasyon: 9 Aktif Ajan</span>
            <span>Sistem: Çevrimiçi</span>
        </div>
    </div>

    <!-- Ofis Haritası ve Odalar -->
    <div id="office-hq">
        <!-- Odalar -->
        <div class="room" style="left: 20px; top: 20px; width: 440px; height: 220px;">
            <div class="room-title">ÜST YÖNETİM & OPERASYON KANADI</div>
        </div>
        <div class="room" style="left: 480px; top: 20px; width: 460px; height: 220px;">
            <div class="room-title">PAZARLAMA & TEKNOLOJİ ÜSSÜ</div>
        </div>
        <div class="room" style="left: 20px; top: 280px; width: 440px; height: 220px;">
            <div class="room-title">HUKUK & İK DEPARTMANI</div>
        </div>
        <div class="room" style="left: 480px; top: 280px; width: 460px; height: 220px;">
            <div class="room-title">FİNANS & GÜVENLİK MERKEZİ</div>
        </div>

        <!-- Masalar -->
        <div class="desk" style="left: 100px; top: 100px;"></div>
        <div class="desk" style="left: 300px; top: 100px;"></div>
        <div class="desk" style="left: 500px; top: 100px;"></div>
        <div class="desk" style="left: 700px; top: 100px;"></div>
        <div class="desk" style="left: 100px; top: 360px;"></div>
        <div class="desk" style="left: 300px; top: 360px;"></div>
        <div class="desk" style="left: 500px; top: 360px;"></div>
        <div class="desk" style="left: 700px; top: 360px;"></div>
        <div class="desk" style="left: 800px; top: 360px;"></div>

        <!-- CEO (Sen) -->
        <div class="ceo-avatar" title="CEO Mertcan">SEN</div>

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
    <div id="console-log">
        > Sistem Başlatıldı. 9 kişilik rüya takım odalarında görev başında. Detay görmek için ajanlara tıklayın patron.
    </div>

    <script>
        const consoleLog = document.getElementById('console-log');

        function selectAgent(name, role, room) {
            consoleLog.innerHTML = `> [AJAN SEÇİLDİ] İsim: <b>${name}</b> | Görev: <b>${role}</b> | Konum: <b>${room}</b> - Durum: Aktif ve çalışıyor.`;
        }

        // Ajanların odalar içinde hafifçe devriye gezmesi / hareket etmesi
        setInterval(() => {
            const keys = Object.keys({{ employees | tojson }});
            const randomKey = keys[Math.floor(Math.random() * keys.length)];
            const agentEl = document.getElementById('agent-' + randomKey);
            
            if (agentEl) {
                let dx = (Math.random() - 0.5) * 16;
                let dy = (Math.random() - 0.5) * 16;
                let curX = parseFloat(agentEl.style.left);
                let curY = parseFloat(agentEl.style.top);
                
                // Sınırlar içinde tut
                agentEl.style.left = Math.max(40, Math.min(900, curX + dx)) + 'px';
                agentEl.style.top = Math.max(40, Math.min(460, curY + dy)) + 'px';
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
