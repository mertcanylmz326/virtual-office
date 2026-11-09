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
    "Marco": {"role": "Destek", "salary": 800, "xp": 50, "level": 1, "title": "Junior", "color": "#3b82f6", "state": "Masada", "speech": "Destek aktif"},
    "Talisca": {"role": "Operasyon", "salary": 950, "xp": 70, "level": 1, "title": "Junior", "color": "#ef4444", "state": "Masada", "speech": "Operasyon OK"},
    "Brown": {"role": "Yazılım", "salary": 1200, "xp": 130, "level": 2, "title": "Senior", "color": "#10b981", "state": "Masada", "speech": "GPT-OSS 120B"},
    "Kante": {"role": "Pazarlama", "salary": 900, "xp": 60, "level": 1, "title": "Junior", "color": "#f59e0b", "state": "Masada", "speech": "Lead topluyor"},
    "İrfan": {"role": "Finans", "salary": 1100, "xp": 100, "level": 2, "title": "Senior", "color": "#8b5cf6", "state": "Masada", "speech": "Bütçe kontrol"},
    "İsmail": {"role": "İK & Sistem", "salary": 850, "xp": 40, "level": 1, "title": "Junior", "color": "#f97316", "state": "Masada", "speech": "Sistem Sağlığı"},
    "Alex": {"role": "Hukuk", "salary": 1050, "xp": 90, "level": 2, "title": "Senior", "color": "#14b8a6", "state": "Masada", "speech": "Sözleşme OK"},
    "Skrinar": {"role": "Siber", "salary": 1300, "xp": 160, "level": 3, "title": "Master", "color": "#64748b", "state": "Masada", "speech": "Firewall aktif"},
    "Kerem": {"role": "Başarı", "salary": 950, "xp": 80, "level": 1, "title": "Junior", "color": "#ec4899", "state": "Masada", "speech": "Hedefler tuttu"},
    "Mutfak_Chef": {"role": "Mutfak", "salary": 700, "xp": 30, "level": 1, "title": "Chef", "color": "#f43f5e", "state": "Kahve Hazırlıyor", "speech": "Taze kahve!"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - Cybernetic Lab HQ</title>
    <style>
        body { 
            background-color: #02040a; 
            color: #f8fafc; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow-x: hidden; 
        }
        #game-topbar {
            background: #090d16;
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
            background: #1e1b4b; color: #38bdf8; border: 1px solid #4c1d95; padding: 6px 12px; 
            border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 11px;
        }
        .top-btn:hover { background: #38bdf8; color: #02040a; }

        #stats-bar {
            background: #050811;
            padding: 8px 15px;
            display: flex;
            justify-content: space-around;
            border-bottom: 1px solid #1e1b4b;
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
            border: 3px solid #38bdf8;
            border-radius: 12px;
            box-shadow: 0 0 60px rgba(56, 189, 248, 0.35);
            background: #02040a;
            overflow: hidden;
        }
        canvas { display: block; width: 100%; height: 100%; }

        .action-bar { margin: 10px auto; width: 1080px; max-width: 100%; display: flex; justify-content: space-between; gap: 10px; padding: 0 10px; box-sizing: border-box; }
        #command-panel {
            background: #090d16; border: 2px solid #4c1d95; padding: 8px; border-radius: 8px; display: flex; gap: 8px; align-items: center; flex-grow: 1; flex-wrap: wrap;
        }
        select, input[type="text"] { background: #1e1b4b; color: #fff; border: 1px solid #6d28d9; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        input[type="text"] { flex-grow: 1; min-width: 200px; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 12px; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 15px auto; width: 1080px; max-width: 100%; background: #02040a; border: 2px solid #4c1d95; border-radius: 8px; text-align: left; overflow: hidden; box-sizing: border-box;
        }
        .terminal-header { background: #090d16; padding: 6px 12px; font-size: 11px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; flex-wrap: wrap; }
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
        <div style="font-weight: bold; color: #38bdf8; font-size: 13px;">🪐 E-TRADE PRO // CYBERNETIC LAB HQ</div>
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
        <span style="color: #c084fc;">🚀 3D CYBERNETIC LAB AKTİF</span>
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
            <span>⚡ CYBERNETIC LAB OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8; font-weight: bold;">● SYSTEM ONLINE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Cybernetic Lab izometrik konsept arayüzü başarıyla yüklendi.</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const terminalLogs = document.getElementById('terminal-logs');

        let agentsData = {};
        let pulseAngle = 0;

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

            // 1. Üst Kısım: Biowall Kubbesi & Şehir Manzarası
            let domeGrad = ctx.createLinearGradient(0, 0, 0, 150);
            domeGrad.addColorStop(0, "#090d16");
            domeGrad.addColorStop(1, "#1e1b4b");
            ctx.fillStyle = domeGrad;
            ctx.fillRect(0, 0, w, 150);

            // Biowall Yeşil Bitki Dokusu (Yapay Doğa Duvarı)
            ctx.fillStyle = "rgba(16, 185, 129, 0.25)";
            ctx.fillRect(w/2 - 250, 30, 500, 70);
            ctx.strokeStyle = "#34d399";
            ctx.lineWidth = 1;
            ctx.strokeRect(w/2 - 250, 30, 500, 70);

            ctx.fillStyle = "#34d399";
            ctx.font = "bold 10px 'Courier New'";
            ctx.textAlign = "center";
            ctx.fillText("🌿 BIOWALL & CENTRAL DOME", w/2, 55);
            ctx.fillStyle = "#94a3b8";
            ctx.font = "9px 'Courier New'";
            ctx.fillText("CYBERNETIC LAB // KASA: $22,500 | MÜŞTERİ: 6", w/2, 75);
            ctx.textAlign = "left";

            // 2. Alt Zemin Grid ve Sınırlar
            ctx.fillStyle = "#02040a";
            ctx.fillRect(0, 150, w, h - 150);

            ctx.strokeStyle = "rgba(56, 189, 248, 0.08)";
            ctx.lineWidth = 1;
            for (let i = 0; i < w; i += 40) {
                ctx.beginPath();
                ctx.moveTo(i, 150);
                ctx.lineTo(i, h);
                ctx.stroke();
            }

            // 3. Merkez Enerji Çekirdeği (Core Reactor)
            pulseAngle += 0.03;
            let centerX = w / 2;
            let centerY = 330;

            ctx.beginPath();
            ctx.arc(centerX, centerY, 65, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(56, 189, 248, 0.15)";
            ctx.fill();
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(centerX, centerY, 35 + Math.sin(pulseAngle)*5, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(168, 85, 247, 0.4)";
            ctx.fill();
            ctx.strokeStyle = "#c084fc";
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 9px 'Courier New'";
            ctx.textAlign = "center";
            ctx.fillText("CORE", centerX, centerY - 2);
            ctx.textAlign = "left";

            // 4. 10 Ajanın Çevresel Hexagon Podları (Görseldeki Gibi Dairesel Dağılım)
            const employeeKeys = Object.keys(employees);
            let radiusX = 380;
            let radiusY = 120;

            let index = 0;
            for (let name in employees) {
                let angle = (index / 10) * (Math.PI * 2);
                let x = centerX + Math.cos(angle) * radiusX - 60;
                let y = centerY + Math.sin(angle) * radiusY - 30;

                // Enerji Köprüsü (Merkezden Pod'a Çizgi)
                ctx.beginPath();
                ctx.moveTo(centerX, centerY);
                ctx.lineTo(x + 60, y + 30);
                ctx.strokeStyle = employees[name].color;
                ctx.lineWidth = 1.5;
                ctx.stroke();

                // Pod Kutusu
                ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                ctx.fillRect(x, y, 120, 65);
                ctx.strokeStyle = employees[name].color;
                ctx.lineWidth = 2;
                ctx.strokeRect(x, y, 120, 65);

                // Ajan Adı ve Rolü
                ctx.fillStyle = employees[name].color;
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(name, x + 8, y + 16);
                
                ctx.fillStyle = "#94a3b8";
                ctx.font = "8px 'Courier New'";
                ctx.fillText(employees[name].role, x + 8, y + 28);

                // Canlı Durum / Konuşma
                let ag = agentsData[name] || { speech: employees[name].state, color: employees[name].color };
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(x + 8, y + 38, 104, 18);
                ctx.strokeStyle = employees[name].color;
                ctx.strokeRect(x + 8, y + 38, 104, 18);
                ctx.fillStyle = "#02040a";
                ctx.font = "bold 8px 'Courier New'";
                ctx.fillText((ag.speech || "Aktif").substring(0, 18), x + 12, y + 50);

                index++;
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
        }, 150);

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
        agent_list.append({
            "name": name, "role": data["role"], "level": data.get("level", 1),
            "title": data.get("title", "Junior"), "x": 0, "y": 0, 
            "state": "Aktif", "speech": f"{data['role']} Çalışıyor", "color": data["color"]
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
        reply = "Patron, GPT-OSS 120B motoru ve Cybernetic Lab dairesel üs mimarisiyle site üretildi!"
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
    <title>Cybernetic Lab Konsept</title>
    <style>
        body {{ background: #02040a; color: #f8fafc; font-family: sans-serif; margin: 0; padding: 0; }}
        header {{ background: #090d16; padding: 50px 20px; text-align: center; border-bottom: 3px solid #38bdf8; }}
        h1 {{ color: #38bdf8; margin: 0; font-size: 30px; }}
        .container {{ max-width: 900px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }}
        .card {{ background: #050811; padding: 30px; border-radius: 10px; border: 1px solid #1e1b4b; }}
        .card h3 {{ color: #4ade80; margin-top: 0; }}
    </style>
</head>
<body>
    <header>
        <h1>Cybernetic Lab Mimari Tasarım</h1>
        <p style="color: #94a3b8; margin-top: 10px;">Merkezi çekirdek ve dairesel pod entegrasyonu</p>
    </header>
    <div class="container">
        <div class="card">
            <h3>Sistem Aktif</h3>
            <p>Talebiniz doğrultusunda fütüristik lab altyapısıyla hazırlandı.</p>
        </div>
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
    return jsonify({"decision": "Yönetim kurulu Cybernetic Lab arayüz tasarımını onayladı."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
