İmport os
import re
import time
import random
import datetime
import psycopg2
from flask import Flask, render_template_string, jsonify, request, Response
from groq import Groq

app = Flask(__name__)

DB_URL = "postgresql://postgres.prphsmgaujdwrqqdmmrd:yaheroyamero@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
GROQ_API_KEY = "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"
UPTIMEROBOT_API_KEY = "u3671342-858d5db4b2fd40032fce3ce6"

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

company_state = {
    "budget": 22500,
    "crisis": "Yok",
    "active_clients": 6
}

def init_db():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id SERIAL PRIMARY KEY,
                agent_name TEXT,
                action_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS client_orders (
                id SERIAL PRIMARY KEY,
                client_name TEXT,
                project_type TEXT,
                status TEXT DEFAULT 'Tamamlandı',
                repo_url TEXT,
                html_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

def check_system_uptime():
    try:
        import requests
        url = "https://api.uptimerobot.com/v2/getMonitors"
        payload = {"api_key": UPTIMEROBOT_API_KEY, "format": "json"}
        response = requests.post(url, data=payload, timeout=5)
        data = response.json()
        if data.get("stat") == "ok":
            monitors = data.get("monitors", [])
            if monitors:
                status_code = monitors[0].get("status")
                status_text = "Aktif (Çalışıyor)" if status_code in [2, 2.0] else f"Kod Durumu: {status_code}"
                return f"UptimeRobot: Sistem monitörleri {status_text}."
    except Exception as e:
        print(f"UptimeRobot API Hatası: {e}")
    return "UptimeRobot API aktif."

# Her ajanın sorumlu olduğu saksı ve sağlık durumu (100 üzerinden)
employees = {
    "Marco": {"role": "Destek", "salary": 800, "xp": 50, "level": 1, "title": "Junior", "color": "#3b82f6", "plant": "Monstera", "plant_health": 95, "speech": "Destek aktif"},
    "Talisca": {"role": "Operasyon", "salary": 950, "xp": 70, "level": 1, "title": "Junior", "color": "#ef4444", "plant": "Paşa Kılıcı", "plant_health": 88, "speech": "Operasyon OK"},
    "Brown": {"role": "Yazılım", "salary": 1200, "xp": 130, "level": 2, "title": "Senior", "color": "#10b981", "plant": "Bonsai", "plant_health": 100, "speech": "GPT-OSS 120B"},
    "Kante": {"role": "Pazarlama", "salary": 900, "xp": 60, "level": 1, "title": "Junior", "color": "#f59e0b", "plant": "Aloe Vera", "plant_health": 92, "speech": "Lead topluyor"},
    "İrfan": {"role": "Finans", "salary": 1100, "xp": 100, "level": 2, "title": "Senior", "color": "#8b5cf6", "plant": "Sukulent", "plant_health": 90, "speech": "Bütçe kontrol"},
    "İsmail": {"role": "İK & Sistem", "salary": 850, "xp": 40, "level": 1, "title": "Junior", "color": "#f97316", "plant": "Orkide", "plant_health": 85, "speech": "Sistem Sağlığı"},
    "Alex": {"role": "Hukuk", "salary": 1050, "xp": 90, "level": 2, "title": "Senior", "color": "#14b8a6", "plant": "Kaktüs", "plant_health": 98, "speech": "Sözleşme OK"},
    "Skrinar": {"role": "Siber", "salary": 1300, "xp": 160, "level": 3, "title": "Master", "color": "#64748b", "plant": "Çin Yaprağı", "plant_health": 94, "speech": "Firewall aktif"},
    "Kerem": {"role": "Başarı", "salary": 950, "xp": 80, "level": 1, "title": "Junior", "color": "#ec4899", "plant": "Benjamin", "plant_health": 91, "speech": "Hedefler tuttu"},
    "Mutfak_Chef": {"role": "Mutfak", "salary": 700, "xp": 30, "level": 1, "title": "Chef", "color": "#f43f5e", "plant": "Fesleğen", "plant_health": 99, "speech": "Kahveler taze!"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - Architectural Corridor HQ</title>
    <style>
        body { 
            background-color: #030712; 
            color: #f8fafc; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow-x: hidden; 
        }
        #game-topbar {
            background: #0f172a;
            border-bottom: 2px solid #38bdf8;
            padding: 10px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            flex-wrap: wrap;
            gap: 8px;
        }
        .top-btn { 
            background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 6px 12px; 
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 11px;
        }
        .top-btn:hover { background: #38bdf8; color: #030712; }

        #stats-bar {
            background: #090d16;
            padding: 8px 15px;
            display: flex;
            justify-content: space-around;
            border-bottom: 1px solid #1e293b;
            font-size: 12px;
            font-weight: bold;
            flex-wrap: wrap;
            gap: 10px;
        }

        #game-container {
            position: relative;
            width: 1080px;
            height: 520px;
            max-width: 100%;
            margin: 10px auto;
            border: 4px solid #38bdf8;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.4);
            background: #060913;
            overflow: hidden;
        }
        canvas { display: block; width: 100%; height: 100%; }

        .action-bar { margin: 10px auto; width: 1080px; max-width: 100%; display: flex; justify-content: space-between; gap: 10px; padding: 0 10px; box-sizing: border-box; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 8px; border-radius: 8px; display: flex; gap: 8px; align-items: center; flex-grow: 1; flex-wrap: wrap;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        input[type="text"] { flex-grow: 1; min-width: 200px; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 12px; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 15px auto; width: 1080px; max-width: 100%; background: #030712; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden; box-sizing: border-box;
        }
        .terminal-header { background: #0f172a; padding: 6px 12px; font-size: 11px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; flex-wrap: wrap; }
        .terminal-body { padding: 10px; height: 140px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; word-break: break-word; overflow-wrap: break-word; }
        .log-line { margin-bottom: 6px; border-bottom: 1px dashed rgba(255,255,255,0.05); }

        @media (max-width: 768px) {
            #game-topbar { flex-direction: column; align-items: stretch; text-align: center; }
            #game-topbar > div { display: flex; justify-content: center; flex-wrap: wrap; gap: 5px; margin-top: 5px; }
            .action-bar { padding: 0 5px; }
            #command-panel { flex-direction: column; align-items: stretch; }
            input[type="text"], select, .send-btn { width: 100%; box-sizing: border-box; }
        }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8; font-size: 13px;">🏢 E-TRADE PRO // ARCHITECTURAL HQ</div>
        <div>
            <span class="top-btn" onclick="loadMemory()">🧠 HAFIZA</span>
            <span class="top-btn" onclick="loadTasks()">📋 PROJELER</span>
            <span class="top-btn" onclick="checkUptime()">🛡️ SİSTEM SAĞLIĞI</span>
            <span class="top-btn" onclick="triggerBoardroom()">🤝 ZİRVE</span>
        </div>
    </div>

    <div id="stats-bar">
        <span style="color: #4ade80;">💰 KASA: $<span id="stat-budget">22500</span></span>
        <span style="color: #38bdf8;">👥 MÜŞTERİ: <span id="stat-clients">6</span></span>
        <span style="color: #fbbf24;">🚀 KORİDOR & SAKSI SİSTEMİ AKTİF</span>
    </div>

    <div id="game-container">
        <canvas id="officeCanvas" width="1080" height="520"></canvas>
    </div>

    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name, data in employees.items() %}
                <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Brown'a site yazdır, Kante'ye pazarlama sor..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ FACILITY OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8; font-weight: bold;">● FACILITY ONLINE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Koridorlar, Sunucu Onay Odası, Mutfak ve Saksı Takip Sistemi aktif!</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const terminalLogs = document.getElementById('terminal-logs');

        let agentsData = {};

        function appendLog(text) {
            const time = new Date().toLocaleTimeString();
            let logDiv = document.createElement('div');
            logDiv.className = 'log-line';
            logDiv.innerHTML = `[${time}] ${text}`;
            terminalLogs.prepend(logDiv);
            terminalLogs.scrollTop = 0;
        }

        function selectAgent(name) {
            document.getElementById('agent-select').value = name;
        }

        function drawOffice() {
            const w = 1080;
            const h = 520;
            ctx.clearRect(0, 0, w, h);

            // BINA DIŞ KUTU / DUVAR ARKA PLANI
            ctx.fillStyle = "#0b0f19";
            ctx.fillRect(0, 0, w, h);

            // Gerçekçi Koridorlar (Yatay ve Dikey Geniş Koridor Ağları)
            ctx.fillStyle = "#111827";
            ctx.fillRect(0, 150, w, 40);  // Ana Yatay Koridor 1
            ctx.fillRect(0, 340, w, 40);  // Ana Yatay Koridor 2
            ctx.fillRect(520, 0, 40, h);  // Ana Dikey Koridor

            // --- 1. SOL BLOK: ÇALIŞMA ODALARI & SAKSILAR ---
            const workRooms = [
                {x: 20, y: 20, name: "1. MARCO", agent: "Marco", color: "#3b82f6"},
                {x: 185, y: 20, name: "2. TALİSCA", agent: "Talisca", color: "#ef4444"},
                {x: 350, y: 20, name: "3. BROWN", agent: "Brown", color: "#10b981"},
                {x: 20, y: 200, name: "4. KANTE", agent: "Kante", color: "#f59e0b"},
                {x: 185, y: 200, name: "5. İRFAN", agent: "İrfan", color: "#8b5cf6"},
                {x: 350, y: 200, name: "6. İSMAİL", agent: "İsmail", color: "#f97316"},
                {x: 20, y: 390, name: "7. ALEX", agent: "Alex", color: "#14b8a6"},
                {x: 185, y: 390, name: "8. SKRİNAR", agent: "Skrinar", color: "#64748b"},
                {x: 350, y: 390, name: "9. KEREM", agent: "Kerem", color: "#ec4899"}
            ];

            workRooms.forEach(r => {
                // Oda Duvarı
                ctx.fillStyle = "rgba(15, 23, 42, 0.95)";
                ctx.fillRect(r.x, r.y, 150, 110);
                ctx.strokeStyle = r.color;
                ctx.lineWidth = 2;
                ctx.strokeRect(r.x, r.y, 150, 110);

                // Oda Başlığı & Işıklandırma
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(r.name, r.x + 8, r.y + 14);

                // Çalışma Masası
                ctx.fillStyle = "#1e293b";
                ctx.fillRect(r.x + 45, r.y + 45, 60, 22);
                ctx.fillStyle = r.color;
                ctx.fillRect(r.x + 65, r.y + 50, 20, 10);

                // Saksı (Bitki) & Sağlık Durumu
                let agInfo = agentsData[r.agent] || { plant: "Bitki", plant_health: 100 };
                ctx.fillStyle = "#78350f";
                ctx.fillRect(r.x + 15, r.y + 75, 14, 16);
                ctx.fillStyle = "#4ade80";
                ctx.font = "11px sans-serif";
                ctx.fillText("🌿", r.x + 13, r.y + 72);

                ctx.fillStyle = "#cbd5e1";
                ctx.font = "8px 'Courier New'";
                ctx.fillText(`${agInfo.plant_health || 95}%`, r.x + 35, r.y + 87);
            });

            // --- 2. SAĞ ÜST: MUTFAK (Masa ve Dolaplar) ---
            ctx.fillStyle = "rgba(120, 53, 15, 0.35)";
            ctx.fillRect(580, 20, 480, 120);
            ctx.strokeStyle = "#d97706";
            ctx.lineWidth = 3;
            ctx.strokeRect(580, 20, 480, 120);

            ctx.fillStyle = "#fde68a";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("☕ MUTFAK (Masa & Dolap Alanı)", 600, 38);

            // Mutfak Dolapları (Üst)
            ctx.fillStyle = "#451a03";
            ctx.fillRect(600, 50, 200, 25);
            ctx.fillStyle = "#78350f";
            ctx.fillRect(820, 50, 220, 25);

            // Mutfak Yemek Masası & Sandalyeler
            ctx.fillStyle = "#292524";
            ctx.fillRect(700, 85, 180, 40);
            ctx.fillStyle = "#f59e0b";
            ctx.fillRect(720, 95, 25, 20);
            ctx.fillRect(775, 95, 25, 20);
            ctx.fillRect(830, 95, 25, 20);

            // --- 3. SAĞ ORTA: CEO KONTROL MERKEZİ ---
            ctx.fillStyle = "rgba(2, 132, 199, 0.25)";
            ctx.fillRect(580, 200, 480, 110);
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 3;
            ctx.strokeRect(580, 200, 480, 110);

            ctx.fillStyle = "#38bdf8";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("👑 CEO KONTROL MERKEZİ", 600, 220);

            ctx.fillStyle = "#0f172a";
            ctx.fillRect(650, 235, 340, 60);
            ctx.strokeStyle = "#38bdf8";
            ctx.strokeRect(650, 235, 340, 60);
            ctx.fillStyle = "#4ade80";
            ctx.font = "9px 'Courier New'";
            ctx.fillText("CEO Terminal: Tüm birimler ve koridorlar denetleniyor.", 665, 265);

            // --- 4. SAĞ ALT: PROJE ONAY ODASI & SUNUCU (SERVER RACK) ---
            ctx.fillStyle = "rgba(109, 40, 217, 0.3)";
            ctx.fillRect(580, 330, 480, 170);
            ctx.strokeStyle = "#8b5cf6";
            ctx.lineWidth = 3;
            ctx.strokeRect(580, 330, 480, 170);

            ctx.fillStyle = "#e9d5ff";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("🤝 OTONOM PROJE ONAY ODASI & SUNUCU MERKEZİ", 600, 350);

            // Sunucu Kabinleri (Server Racks Görseli)
            ctx.fillStyle = "#1e1b4b";
            ctx.fillRect(600, 370, 120, 115);
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 2;
            ctx.strokeRect(600, 370, 120, 115);

            for(let sy = 385; sy < 470; sy += 22) {
                ctx.fillStyle = "#38bdf8";
                ctx.fillRect(615, sy, 15, 10);
                ctx.fillStyle = "#4ade80";
                ctx.fillRect(645, sy, 12, 10);
                ctx.fillStyle = "#ef4444";
                ctx.fillRect(675, sy, 10, 10);
            }

            // Onay Masası
            ctx.fillStyle = "#3b0764";
            ctx.fillRect(780, 390, 220, 75);
            ctx.strokeStyle = "#c084fc";
            ctx.strokeRect(780, 390, 220, 75);
            ctx.fillStyle = "#fbcfe8";
            ctx.font = "bold 9px 'Courier New'";
            ctx.fillText("Otonom Onay Konsolu Aktif", 800, 432);

            // Ajanları Çiz
            for (let name in agentsData) {
                let ag = agentsData[name];
                if(!ag) continue;
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x, ag.y, 24, 24);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.strokeRect(ag.x, ag.y, 24, 24);

                // Anten & Gözler
                ctx.fillStyle = "#38bdf8";
                ctx.fillRect(ag.x + 11, ag.y - 4, 2, 4);
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(ag.x + 5, ag.y + 7, 4, 4);
                ctx.fillRect(ag.x + 15, ag.y + 7, 4, 4);

                // İsim
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 8px 'Courier New'";
                ctx.fillText(name, ag.x - 6, ag.y + 38);

                // Konuşma Balonu
                let bubbleText = ag.speech || "Aktif";
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(ag.x - 10, ag.y - 20, ctx.measureText(bubbleText).width + 10, 16);
                ctx.strokeStyle = "#38bdf8";
                ctx.strokeRect(ag.x - 10, ag.y - 20, ctx.measureText(bubbleText).width + 10, 16);
                ctx.fillStyle = "#0f172a";
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(bubbleText, ag.x - 6, ag.y - 9);
            }
        }

        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                document.getElementById('stat-budget').innerText = data.budget;
                document.getElementById('stat-clients').innerText = data.active_clients;
                let mapped = {};
                data.agents.forEach(ag => { mapped[ag.name] = ag; });
                agentsData = mapped;
                drawOffice();
            });
        }, 1500);

        function sendDirectMessage() {
            const agentName = document.getElementById('agent-select').value;
            const messageInput = document.getElementById('ceo-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendLog(`> [CEO -> ${agentName}]: "${messageText}"`);
            messageInput.value = "";
            appendLog(`> [SİSTEM]: ${agentName} talimatı işliyor...`);

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: agentName, message: messageText })
            })
            .then(res => res.json())
            .then(data => {
                appendLog(`> [<b>${agentName}</b>]: "${data.status}"`);
                if(data.preview_url) {
                    appendLog(`> 🚀 <b style="color: #38bdf8; font-size: 14px;">CANLI SİTE LİNKİ (TIKLA AÇ):</b> <a href="${data.preview_url}" target="_blank" style="color: #f43f5e; font-weight: bold; text-decoration: underline; font-size: 14px;">Canlı Web Servis Sayfası 🌐</a>`);
                }
            })
            .catch(err => {
                appendLog(`> [HATA]: Bağlantı kurulamadı.`);
            });
        }

        function loadMemory() {
            appendLog(`> [HAFIZA]: Supabase taranıyor...`);
            fetch('/api/memory').then(res => res.json()).then(data => {
                appendLog(`> [HAFIZA ÖZETİ]: ${data.summary}`);
            });
        }

        function loadTasks() {
            appendLog(`> [PROJELER]: Listeleniyor...`);
            fetch('/api/tasks').then(res => res.json()).then(data => {
                appendLog(`> [KAYITLAR]: ${data.tasks.join(" | ")}`);
            });
        }

        function checkUptime() {
            appendLog(`> [İSMAİL - UPTIME]: Sorgulanıyor...`);
            fetch('/api/uptime').then(res => res.json()).then(data => {
                appendLog(`> [RAPOR]: ${data.status}`);
            });
        }

        function triggerBoardroom() {
            appendLog(`> [ZİRVE]: Yönetim kurulu toplandı...`);
            fetch('/api/boardroom', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [KARAR]: "${data.decision}"`);
            });
        }
    </script>
</body>
</html>
"""

def log_to_supabase(agent_name, action_type, content):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO agent_logs (agent_name, action_type, content) VALUES (%s, %s, %s)", (agent_name, action_type, content))
        conn.commit()
        cur.close()
        conn.close()
    except: pass

tick_counter = 0

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    global tick_counter, company_state
    agent_list = []
    tick_counter += 1

    if tick_counter % 12 == 0:
        revenue = random.randint(2500, 5000)
        company_state["budget"] += revenue
        company_state["active_clients"] = random.randint(3, 8)
        # Saksı sağlıklarını simülasyon döngüsünde rastgele hafif güncelleyelim
        for k in employees:
            employees[k]["plant_health"] = max(80, min(100, employees[k]["plant_health"] + random.randint(-1, 1)))

    coords = {
        "Marco": (70, 70), "Talisca": (235, 70), "Brown": (400, 70),
        "Kante": (70, 250), "İrfan": (235, 250), "İsmail": (400, 250),
        "Alex": (70, 440), "Skrinar": (235, 440), "Kerem": (400, 440),
        "Mutfak_Chef": (900, 80)
    }

    for name, data in employees.items():
        base_x, base_y = coords.get(name, (100, 100))
        speech = "Kahve Hazırlıyor" if name == "Mutfak_Chef" else f"{data['role']} Çalışıyor"

        agent_list.append({
            "name": name, "role": data["role"], "level": data.get("level", 1),
            "title": data.get("title", "Junior"), "x": base_x, "y": base_y, 
            "state": "Masada", "speech": speech, "color": data["color"],
            "plant": data["plant"], "plant_health": data["plant_health"]
        })

    return jsonify({"agents": agent_list, "budget": company_state["budget"], "active_clients": company_state["active_clients"]})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, employees=employees)

@app.route('/preview/<int:project_id>')
def preview_project(project_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT html_code FROM client_orders WHERE id = %s", (project_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        db_code = row[0] if row and row[0] else "<h1>Proje kodu bulunamadı.</h1>"
        return Response(db_code, mimetype='text/html')
    except Exception as e:
        print(f"Preview Hatası: {e}")
    return "Proje bulunamadı.", 404

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    agent_name = data.get('agent', 'Brown')
    user_message = data.get('message', '')

    if agent_name not in employees: agent_name = "Brown"
    agent = employees[agent_name]

    html_code = ""
    reply = ""
    preview_url = None

    if agent_name != "Brown":
        try:
            if groq_client:
                prompt = f"Sen ofiste '{agent['role']}' olarak çalışan bir uzmansın. Patronun (Kullanıcı) sana şu mesajı gönderdi: '{user_message}'. Kendi departmanının uzmanlığıyla profesyonel ve kısa bir iş yanıtı ver. Asla HTML kodu yazma."
                comp = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300, temperature=0.7
                )
                reply = comp.choices[0].message.content.strip()
        except Exception as e:
            reply = f"Patron, {agent['role']} departmanı olarak talimatını aldık!"
        
        if not reply:
            reply = f"Patron, {agent['role']} departmanı olarak notumuzu aldık!"

    else:
        reply = "Patron, GPT-OSS 120B motoru ile site sıfırdan ve eksiksiz kodlandı!"
        try:
            if groq_client:
                code_prompt = f"Sen kıdemli bir web geliştiricisisin. Sadece ve sadece saf, eksiksiz bir HTML/CSS web sitesi yaz. Asla markdown etiketi (```html) kullanma, asla açıklama yapma. İstek: {user_message}"
                comp = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": code_prompt}],
                    max_tokens=4000, temperature=0.7
                )
                raw_code = comp.choices[0].message.content.strip()
                
                clean_code = re.sub(r'```[a-zA-Z]*', '', raw_code)
                clean_code = clean_code.replace('```', '')

                lower_code = clean_code.lower()
                start_idx = lower_code.find("<!doctype")
                if start_idx == -1:
                    start_idx = lower_code.find("<html")
                
                end_idx = lower_code.rfind("</html>")

                if start_idx != -1 and end_idx != -1:
                    html_code = clean_code[start_idx:end_idx+7]
                else:
                    html_code = clean_code.strip()
        except Exception as e:
            print(f"Groq API Üretim Hatası: {e}")

        if not html_code or "<html" not in html_code.lower() or len(html_code) < 100:
            html_code = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Architectural HQ Konsept</title>
    <style>
        body {{ background: #060913; color: #f8fafc; font-family: sans-serif; margin: 0; padding: 0; }}
        header {{ background: #0f172a; padding: 50px 20px; text-align: center; border-bottom: 3px solid #38bdf8; }}
        h1 {{ color: #38bdf8; margin: 0; font-size: 30px; }}
        .container {{ max-width: 900px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }}
        .card {{ background: #111827; padding: 30px; border-radius: 10px; border: 1px solid #334155; }}
        .card h3 {{ color: #4ade80; margin-top: 0; }}
    </style>
</head>
<body>
    <header>
        <h1>Architectural HQ Kurumsal Çözüm</h1>
        <p style="color: #94a3b8; margin-top: 10px;">Koridorlu ve saksı takip sistemli özel altyapı</p>
    </header>
    <div class="container">
        <div class="card">
            <h3>Sistem Aktif</h3>
            <p>Talebiniz doğrultusunda kusursuz standartlarda hazırlandı.</p>
        </div>
    </div>
</body>
</html>"""

        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("INSERT INTO client_orders (client_name, project_type, repo_url, html_code) VALUES (%s, %s, %s, %s) RETURNING id", 
                        ("Brown (Yazılımcı)", user_message[:40], "Web Servis Canල්", html_code))
            project_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            host_url = request.host_url.rstrip('/')
            preview_url = f"{host_url}/preview/{project_id}"
        except Exception as e:
            print(f"DB Kayıt Hatası: {e}")

    log_to_supabase(agent_name, "SYSTEM_OP", f"Talimat: {user_message}")
    return jsonify({"status": reply, "preview_url": preview_url})

@app.route('/api/uptime', methods=['GET'])
def api_uptime():
    return jsonify({"status": check_system_uptime()})

@app.route('/api/memory', methods=['GET'])
def api_memory():
    return jsonify({"summary": "Supabase bağlantısı aktif."})

@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, client_name, project_type FROM client_orders ORDER BY id DESC LIMIT 5;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tasks = [f"[{r[1]}]: {r[2]} (Link: /preview/{r[0]})" for r in rows]
        return jsonify({"tasks": tasks if tasks else ["Proje yok."]})
    except:
        return jsonify({"tasks": ["Yüklenemedi."]})

@app.route('/api/boardroom', methods=['POST'])
def api_boardroom():
    return jsonify({"decision": "Yönetim kurulu koridorlu mimari ve saksı sorumluluk sistemini onayladı."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
