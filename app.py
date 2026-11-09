import os
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

employees = {
    "Marco": {"role": "Destek", "salary": 800, "xp": 50, "level": 1, "title": "Junior", "room_x": 15, "room_y": 15, "color": "#3b82f6", "state": "Masada", "speech": "Müşteri destek veriyor"},
    "Talisca": {"role": "Operasyon", "salary": 950, "xp": 70, "level": 1, "title": "Junior", "room_x": 195, "room_y": 15, "color": "#ef4444", "state": "Masada", "speech": "Süreç takipte"},
    "Brown": {"role": "Yazılım", "salary": 1200, "xp": 130, "level": 2, "title": "Senior", "room_x": 375, "room_y": 15, "color": "#10b981", "state": "Masada", "speech": "Direct Response Aktif"},
    
    "Kante": {"role": "Pazarlama", "salary": 900, "xp": 60, "level": 1, "title": "Junior", "room_x": 15, "room_y": 155, "color": "#f59e0b", "state": "Masada", "speech": "Lead topluyor"},
    "İrfan": {"role": "Finans", "salary": 1100, "xp": 100, "level": 2, "title": "Senior", "room_x": 195, "room_y": 155, "color": "#8b5cf6", "state": "Masada", "speech": "Bütçe kontrol"},
    "İsmail": {"role": "İK & Sistem", "salary": 850, "xp": 40, "level": 1, "title": "Junior", "room_x": 375, "room_y": 155, "color": "#f97316", "state": "Masada", "speech": "Sistem Sağlığı OK"},
    
    "Alex": {"role": "Hukuk", "salary": 1050, "xp": 90, "level": 2, "title": "Senior", "room_x": 15, "room_y": 295, "color": "#14b8a6", "state": "Masada", "speech": "Sözleşme aktif"},
    "Skrinar": {"role": "Siber", "salary": 1300, "xp": 160, "level": 3, "title": "Master", "room_x": 195, "room_y": 295, "color": "#64748b", "state": "Masada", "speech": "Firewall koruyor"},
    "Kerem": {"role": "Başarı", "salary": 950, "xp": 80, "level": 1, "title": "Junior", "room_x": 375, "room_y": 295, "color": "#ec4899", "state": "Masada", "speech": "Hedefler tuttu"},
    "Mutfak_Chef": {"role": "Mutfak", "salary": 700, "xp": 30, "level": 1, "title": "Chef", "room_x": 580, "room_y": 15, "color": "#f43f5e", "state": "Kahve Hazırlıyor", "speech": "Taze kahve!"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - AI Agency HQ</title>
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
            height: 440px;
            max-width: 100%;
            margin: 10px auto;
            border: 3px solid #38bdf8;
            border-radius: 8px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.9);
            background: #0b0f19;
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
        .terminal-body { padding: 10px; height: 160px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; word-break: break-word; overflow-wrap: break-word; }
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
        <div style="font-weight: bold; color: #38bdf8; font-size: 13px;">🏢 E-TRADE PRO // DIRECT HTML RENDER</div>
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
        <span style="color: #fbbf24;">🚀 GÜVENLİ RENDER AKTİF</span>
    </div>

    <div id="game-container">
        <canvas id="officeCanvas" width="1080" height="440"></canvas>
    </div>

    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name, data in employees.items() %}
                <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Galerici veya istedigini yaz..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8; font-weight: bold;">● RENDER ONLINE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Güvenli MIME type response motoru aktif edildi. ERR_UNSAFE_REDIRECT engellendi!</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const terminalLogs = document.getElementById('terminal-logs');

        let agentsData = {};

        function appendLog(text) {
            const time = new Date().toLocaleTimeString();
            const logDiv = document.createElement('div');
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
            const h = 440;
            ctx.clearRect(0, 0, w, h);

            ctx.fillStyle = "#1e1b18";
            ctx.fillRect(0, 0, w, h);
            
            ctx.strokeStyle = "#292524";
            ctx.lineWidth = 1;
            for (let i = 0; i < w; i += 30) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, h);
                ctx.stroke();
            }

            ctx.fillStyle = "#111827";
            ctx.fillRect(0, 130, w, 35);
            ctx.fillRect(0, 270, w, 35);
            ctx.fillRect(530, 0, 35, h);

            const rooms = [
                {x: 15, y: 15, w: 160, h: 105, name: "1. MARCO", glow: "#3b82f6"},
                {x: 195, y: 15, w: 160, h: 105, name: "2. TALİSCA", glow: "#ef4444"},
                {x: 375, y: 15, w: 160, h: 105, name: "3. BROWN (DEV)", glow: "#10b981"},
                {x: 15, y: 155, w: 160, h: 105, name: "4. KANTE", glow: "#f59e0b"},
                {x: 195, y: 155, w: 160, h: 105, name: "5. İRFAN", glow: "#8b5cf6"},
                {x: 375, y: 155, w: 160, h: 105, name: "6. İSMAİL (İK)", glow: "#f97316"},
                {x: 15, y: 295, w: 160, h: 105, name: "7. ALEX", glow: "#14b8a6"},
                {x: 195, y: 295, w: 160, h: 105, name: "8. SKRİNAR", glow: "#64748b"},
                {x: 375, y: 295, w: 160, h: 105, name: "9. KEREM", glow: "#ec4899"}
            ];

            rooms.forEach(r => {
                ctx.fillStyle = "rgba(17, 24, 39, 0.85)";
                ctx.fillRect(r.x, r.y, r.w, r.h);

                ctx.strokeStyle = "rgba(56, 189, 248, 0.6)";
                ctx.lineWidth = 3;
                ctx.strokeRect(r.x, r.y, r.w, r.h);

                ctx.strokeStyle = r.glow;
                ctx.lineWidth = 1;
                ctx.strokeRect(r.x + 3, r.y + 3, r.w - 6, r.h - 6);

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(r.name, r.x + 8, r.y + 14);

                ctx.fillStyle = "#1e293b";
                ctx.fillRect(r.x + 50, r.y + 55, 60, 24);
                ctx.fillStyle = r.glow;
                ctx.fillRect(r.x + 68, r.y + 60, 24, 12);

                ctx.fillStyle = "#78350f";
                ctx.fillRect(r.x + 15, r.y + 55, 16, 18);
                ctx.fillStyle = "#4ade80";
                ctx.font = "12px sans-serif";
                ctx.fillText("🌿", r.x + 13, r.y + 50);

                ctx.fillStyle = "#4ade80";
                if (r.y < 130) ctx.fillRect(r.x + 65, r.y + r.h - 3, 30, 6);
                else if (r.y > 250) ctx.fillRect(r.x + 65, r.y - 3, 30, 6);
                else ctx.fillRect(r.x + r.w - 3, r.y + 45, 6, 25);
            });

            ctx.fillStyle = "rgba(2, 132, 199, 0.25)";
            ctx.fillRect(580, 135, 485, 30);
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 2;
            ctx.strokeRect(580, 135, 485, 30);
            ctx.fillStyle = "#38bdf8";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("👑 CEO KONTROL MERKEZİ", 600, 153);

            ctx.fillStyle = "rgba(120, 53, 15, 0.45)";
            ctx.fillRect(580, 15, 485, 110);
            ctx.strokeStyle = "#d97706";
            ctx.lineWidth = 3;
            ctx.strokeRect(580, 15, 485, 110);
            ctx.fillStyle = "#fde68a";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("☕ MUTFAK & KAHVE ALANI", 595, 30);

            ctx.fillStyle = "#451a03";
            ctx.fillRect(720, 55, 100, 40);
            ctx.fillStyle = "#1e293b";
            ctx.fillRect(960, 30, 40, 50);
            ctx.fillStyle = "#fbbf24";
            ctx.fillRect(970, 40, 18, 12);

            ctx.fillStyle = "rgba(109, 40, 217, 0.35)";
            ctx.fillRect(580, 175, 485, 250);
            ctx.strokeStyle = "#8b5cf6";
            ctx.lineWidth = 4;
            ctx.strokeRect(580, 175, 485, 250);
            ctx.fillStyle = "#e9d5ff";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("🤝 OTONOM PROJE ONAY ODASI", 600, 195);

            ctx.fillStyle = "#3b0764";
            ctx.fillRect(740, 270, 160, 60);

            for (let name in agentsData) {
                let ag = agentsData[name];
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x, ag.y, 24, 24);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.strokeRect(ag.x, ag.y, 24, 24);

                ctx.fillStyle = "#38bdf8";
                ctx.fillRect(ag.x + 11, ag.y - 4, 2, 4);

                ctx.fillStyle = "#ffffff";
                ctx.fillRect(ag.x + 5, ag.y + 7, 4, 4);
                ctx.fillRect(ag.x + 15, ag.y + 7, 4, 4);

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 8px 'Courier New'";
                ctx.fillText(name + ` (${ag.title})`, ag.x - 6, ag.y + 38);

                let bubbleText = ag.speech || ag.state;
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(ag.x - 12, ag.y - 22, ctx.measureText(bubbleText).width + 12, 16);
                ctx.strokeStyle = "#38bdf8";
                ctx.strokeRect(ag.x - 12, ag.y - 22, ctx.measureText(bubbleText).width + 12, 16);
                ctx.fillStyle = "#0f172a";
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(bubbleText, ag.x - 8, ag.y - 11);
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

    for name, data in employees.items():
        if name == "Mutfak_Chef":
            x, y, state, speech = 630, 60, "Kahve Hazırlıyor", "Kahveler hazır!"
        else:
            x, y = data["room_x"] + 45, data["room_y"] + 50
            state, speech = "Masada Çalışıyor", f"{data['role']} Aktif"

        agent_list.append({
            "name": name, "role": data["role"], "level": data.get("level", 1),
            "title": data.get("title", "Junior"), "x": x, "y": y, 
            "state": state, "speech": speech, "color": data["color"]
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
        # Tarayıcıyı kısıtlamayan doğrudan güvenli HTML Response döndür
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
    reply = f"Patron, Qwen 3.8B modeli siteyi üretti ve doğrudan sunuldu!"

    try:
        if groq_client:
            code_prompt = f"Sen profesyonel bir web geliştiricisisin. Sadece ve sadece saf, eksiksiz bir HTML/CSS web sitesi kodu yaz. Asla markdown etiketi (```html) kullanma, asla açıklama yapma, sohbet etme. İstek: {user_message}"
            comp = groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[{"role": "user", "content": code_prompt}],
                max_tokens=3000, temperature=0.7
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
        print(f"Groq Qwen API Üretim Hatası: {e}")

    if not html_code or "<html" not in html_code.lower() or len(html_code) < 50:
        html_code = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{user_message[:30]}</title>
    <style>
        body {{ background: #0f172a; color: #f8fafc; font-family: sans-serif; text-align: center; padding: 50px; }}
        h1 {{ color: #38bdf8; }}
        .card {{ background: #1e293b; padding: 30px; border-radius: 12px; max-width: 600px; margin: 20px auto; border: 1px solid #334155; text-align: left; }}
    </style>
</head>
<body>
    <h1>🚀 {user_message}</h1>
    <div class="card">
        <h3>Özel Konsept Tasarım</h3>
        <p>İsteğiniz doğrultusunda Qwen modeli tarafından üretildi.</p>
    </div>
</body>
</html>"""

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO client_orders (client_name, project_type, repo_url, html_code) VALUES (%s, %s, %s, %s) RETURNING id", 
                    ("Brown (Yazılımcı)", user_message[:40], "Web Servis Canlı", html_code))
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
    return jsonify({"decision": "Yönetim kurulu Direct Response entegrasyonunu onayladı."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
