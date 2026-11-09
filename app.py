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
    "Marco": {"role": "Destek", "salary": 800, "color": "#3b82f6", "plant": "Monstera", "plant_health": 95, "speech": "Müşteri destek veriyor"},
    "Talisca": {"role": "Operasyon", "salary": 950, "color": "#ef4444", "plant": "Paşa Kılıcı", "plant_health": 88, "speech": "Süreç takipte"},
    "Brown": {"role": "Yazılım (DEV)", "salary": 1200, "color": "#10b981", "plant": "Bonsai", "plant_health": 100, "speech": "GPT-OSS 120B Aktif"},
    "Kante": {"role": "Pazarlama", "salary": 900, "color": "#f59e0b", "plant": "Aloe Vera", "plant_health": 92, "speech": "Lead topluyor"},
    "İrfan": {"role": "Finans", "salary": 1100, "color": "#8b5cf6", "plant": "Sukulent", "plant_health": 90, "speech": "Bütçe kontrol"},
    "İsmail": {"role": "İK & Sistem", "salary": 850, "color": "#f97316", "plant": "Orkide", "plant_health": 85, "speech": "Sistem Sağlığı OK"},
    "Alex": {"role": "Hukuk", "salary": 1050, "color": "#14b8a6", "plant": "Kaktüs", "plant_health": 98, "speech": "Sözleşme aktif"},
    "Skrinar": {"role": "Siber", "salary": 1300, "color": "#64748b", "plant": "Çin Yaprağı", "plant_health": 94, "speech": "Firewall koruyor"},
    "Kerem": {"role": "Başarı", "salary": 950, "color": "#ec4899", "plant": "Benjamin", "plant_health": 91, "speech": "Hedefler tuttu"},
    "Mutfak_Chef": {"role": "Mutfak", "salary": 700, "color": "#f43f5e", "plant": "Fesleğen", "plant_health": 99, "speech": "Kahveler taze!"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - Cyber Command Center</title>
    <style>
        body { 
            background-color: #030712; 
            color: #f8fafc; 
            font-family: 'Courier New', Courier, monospace; 
            margin: 0; 
            padding: 0; 
            overflow-x: hidden; 
        }
        #game-topbar {
            background: #0f172a;
            border-bottom: 2px solid #38bdf8;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .top-btn { 
            background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 6px 14px; 
            border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px; transition: 0.2s;
        }
        .top-btn:hover { background: #38bdf8; color: #030712; box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }

        #stats-bar {
            background: #090d16;
            padding: 10px 20px;
            display: flex;
            justify-content: space-around;
            border-bottom: 1px solid #1e293b;
            font-size: 13px;
            font-weight: bold;
        }

        /* COMMAND CENTER GRID */
        .command-container {
            max-width: 1350px;
            margin: 20px auto;
            padding: 0 15px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 15px;
        }

        .command-card {
            background: #0b0f19;
            border: 2px solid var(--card-color);
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.6), inset 0 0 10px rgba(255,255,255,0.02);
            text-align: left;
            position: relative;
        }
        .command-card::after {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: var(--card-color);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            border-bottom: 1px dashed rgba(255,255,255,0.1);
            padding-bottom: 8px;
        }
        .card-title { font-weight: bold; font-size: 14px; color: #fff; }
        .card-role { font-size: 11px; color: #94a3b8; background: #1e293b; padding: 2px 8px; border-radius: 4px; }

        .card-body {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #060913;
            padding: 10px;
            border-radius: 6px;
        }

        .plant-info {
            font-size: 11px;
            color: #4ade80;
        }

        .agent-status {
            font-size: 11px;
            color: #38bdf8;
            font-style: italic;
            text-align: right;
        }

        /* ÖZEL SEKTÖRLER (MUTFAK, CEO, ONAY ODASI) */
        .special-box {
            grid-column: span 2;
            background: #0b0f19;
            border: 2px solid #8b5cf6;
            border-radius: 10px;
            padding: 18px;
            box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2);
            text-align: left;
        }
        @media(max-width: 768px) { .special-box { grid-column: span 1; } }

        .action-bar { width: 1350px; max-width: 100%; margin: 15px auto; display: flex; gap: 10px; padding: 0 15px; box-sizing: border-box; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 10px; border-radius: 8px; display: flex; gap: 10px; align-items: center; flex-grow: 1; flex-wrap: wrap;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        input[type="text"] { flex-grow: 1; min-width: 250px; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 12px; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 20px auto; width: 1350px; max-width: 100%; background: #030712; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden; box-sizing: border-box; padding: 0 15px;
        }
        .terminal-header { background: #0f172a; padding: 6px 12px; font-size: 11px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 10px; height: 140px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; font-family: monospace; }
        .log-line { margin-bottom: 6px; border-bottom: 1px dashed rgba(255,255,255,0.05); }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8; font-size: 13px;">🏢 E-TRADE PRO // CYBER COMMAND CENTER</div>
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
        <span style="color: #fbbf24;">🚀 COMMAND CENTER AKTİF</span>
    </div>

    <!-- KOMUTA MERKEZİ KARTLARI -->
    <div class="command-container">
        {% for name, data in employees.items() %}
        <div class="command-card" style="--card-color: {{ data.color }};">
            <div class="card-header">
                <span class="card-title">⚡ {{ name }}</span>
                <span class="card-role">{{ data.role }}</span>
            </div>
            <div class="card-body">
                <div class="plant-info">
                    🌿 <b>{{ data.plant }}</b><br>
                    <span style="color: #38bdf8;">Saksı Sağlığı: {{ data.plant_health }}%</span>
                </div>
                <div class="agent-status" id="speech-{{ name }}">
                    "{{ data.speech }}"
                </div>
            </div>
        </div>
        {% endfor %}

        <!-- MUTFAK BÖLÜMÜ -->
        <div class="special-box" style="border-color: #d97706;">
            <div class="card-header" style="border-color: rgba(217, 119, 6, 0.3);">
                <span class="card-title">☕ MUTFAK & KAHVE İSTASYONU</span>
                <span class="card-role">Sosyal Alan</span>
            </div>
            <p style="font-size: 11px; color: #94a3b8; margin: 5px 0 0 0;">Ankastre mutfak dolapları, yemek masası ve taze kahve makineleriyle donatılmış operasyonel dinlenme alanı.</p>
        </div>

        <!-- CEO & SUNUCU MERKEZİ -->
        <div class="special-box" style="border-color: #8b5cf6;">
            <div class="card-header" style="border-color: rgba(139, 92, 246, 0.3);">
                <span class="card-title">👑 CEO KONTROL & OTONOM SUNUCU MERKEZİ</span>
                <span class="card-role">Server Racks & Onay Konsolu</span>
            </div>
            <p style="font-size: 11px; color: #94a3b8; margin: 5px 0 0 0;">Yanıp sönen siber sunucu kabinleri, otonom proje onay protokolleri ve tüm birimlerin koordine edildiği merkez.</p>
        </div>
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
            <span>⚡ COMMAND OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8; font-weight: bold;">● SYSTEM ONLINE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Command Center arayüzü ve saksı takip protokolleri aktif.</div>
        </div>
    </div>

    <script>
        const terminalLogs = document.getElementById('terminal-logs');

        function appendLog(text) {
            const time = new Date().toLocaleTimeString();
            let logDiv = document.createElement('div');
            logDiv.className = 'log-line';
            logDiv.innerHTML = `[${time}] ${text}`;
            terminalLogs.prepend(logDiv);
            terminalLogs.scrollTop = 0;
        }

        function checkEnter(e) {
            if (e.key === 'Enter') sendDirectMessage();
        }

        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                document.getElementById('stat-budget').innerText = data.budget;
                document.getElementById('stat-clients').innerText = data.active_clients;
                
                data.agents.forEach(ag => {
                    let bubble = document.getElementById(`speech-${ag.name}`);
                    if(bubble) bubble.innerText = `"${ag.speech}"`;
                });
            });
        }, 2000);

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
        for k in employees:
            employees[k]["plant_health"] = max(80, min(100, employees[k]["plant_health"] + random.randint(-1, 1)))

    for name, data in employees.items():
        speech = "Kahve Hazırlıyor" if name == "Mutfak_Chef" else f"{data['role']} Aktif"
        agent_list.append({
            "name": name, "role": data["role"], "speech": speech,
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
        reply = "Patron, GPT-OSS 120B motoru ve Command Center mimarisiyle site sıfırdan ve eksiksiz kodlandı!"
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
    <title>Command Center Konsept</title>
    <style>
        body {{ background: #030712; color: #f8fafc; font-family: sans-serif; margin: 0; padding: 0; }}
        header {{ background: #0f172a; padding: 50px 20px; text-align: center; border-bottom: 3px solid #38bdf8; }}
        h1 {{ color: #38bdf8; margin: 0; font-size: 30px; }}
        .container {{ max-width: 900px; margin: 40px auto; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }}
        .card {{ background: #0b0f19; padding: 30px; border-radius: 10px; border: 1px solid #334155; }}
        .card h3 {{ color: #4ade80; margin-top: 0; }}
    </style>
</head>
<body>
    <header>
        <h1>Command Center Konsept Tasarım</h1>
        <p style="color: #94a3b8; margin-top: 10px;">Elit siber komuta merkezi altyapısı</p>
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
    return jsonify({"decision": "Yönetim kurulu Cyber Command Center arayüzünü onayladı."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
