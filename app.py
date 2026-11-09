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
    "active_clients": 6
}

def init_db():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agents_state (
                name TEXT PRIMARY KEY,
                role TEXT,
                hunger INT DEFAULT 85,
                thirst INT DEFAULT 90,
                caffeine INT DEFAULT 80,
                energy INT DEFAULT 100,
                location TEXT DEFAULT 'Ofiste',
                speech TEXT DEFAULT 'Masada Çalışıyor',
                plant_health INT DEFAULT 95
            );
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
        
        default_agents = [
            ("Marco", "Destek"), ("Talisca", "Operasyon"), ("Brown", "Yazılım"),
            ("Kante", "Pazarlama"), ("İrfan", "Finans"), ("İsmail", "İK & Sistem"),
            ("Alex", "Hukuk"), ("Skrinar", "Siber"), ("Kerem", "Başarı"), ("Mutfak_Chef", "Mutfak")
        ]
        for name, role in default_agents:
            cur.execute("INSERT INTO agents_state (name, role) VALUES (%s, %s) ON CONFLICT (name) DO NOTHING;", (name, role))
        
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

employees_meta = {
    "Marco": {"room_x": 15, "room_y": 15, "color": "#3b82f6"},
    "Talisca": {"room_x": 195, "room_y": 15, "color": "#ef4444"},
    "Brown": {"room_x": 375, "room_y": 15, "color": "#10b981"},
    "Kante": {"room_x": 15, "room_y": 155, "color": "#f59e0b"},
    "İrfan": {"room_x": 195, "room_y": 155, "color": "#8b5cf6"},
    "İsmail": {"room_x": 375, "room_y": 155, "color": "#f97316"},
    "Alex": {"room_x": 15, "room_y": 295, "color": "#14b8a6"},
    "Skrinar": {"room_x": 195, "room_y": 295, "color": "#64748b"},
    "Kerem": {"room_x": 375, "room_y": 295, "color": "#ec4899"},
    "Mutfak_Chef": {"room_x": 580, "room_y": 15, "color": "#f43f5e"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - Living AI Agency HQ</title>
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
        .terminal-body { padding: 10px; height: 140px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; word-break: break-word; overflow-wrap: break-word; font-family: monospace; }
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
        <div style="font-weight: bold; color: #38bdf8; font-size: 13px;">🏢 E-TRADE PRO // LİVİNG HQ (OTONOM SİMÜLASYON)</div>
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
        <span style="color: #fbbf24;">🚀 İHTİYAÇ VE MOLA SİSTEMİ AKTİF</span>
    </div>

    <div id="game-container">
        <canvas id="officeCanvas" width="1080" height="440"></canvas>
    </div>

    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name in meta.keys() %}
                <option value="{{ name }}">{{ name }}</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Brown'a site yazdır, Kante'ye pazarlama sor..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ SİMÜLASYON OPERASYON TERMİNALİ</span>
            <span style="color: #38bdf8; font-weight: bold;">● DB PERSISTENT</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SİSTEM]: Odalar, gerçekçi koridorlar, saksılar ve otonom barlar aktif!</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const terminalLogs = document.getElementById('terminal-logs');

        let agentsData = [];

        function appendLog(text) {
            const time = new Date().toLocaleTimeString();
            const logDiv = document.createElement('div');
            logDiv.className = 'log-line';
            logDiv.innerHTML = `[${time}] ${text}`;
            terminalLogs.prepend(logDiv);
            terminalLogs.scrollTop = 0;
        }

        function checkEnter(e) {
            if (e.key === 'Enter') sendDirectMessage();
        }

        function drawOffice() {
            const w = 1080;
            const h = 440;
            ctx.clearRect(0, 0, w, h);

            // Zemin Tasarımı
            ctx.fillStyle = "#1e1b18";
            ctx.fillRect(0, 0, w, h);
            
            ctx.strokeStyle = "#292524";
            ctx.lineWidth = 1;
            for (let i = 0; i < w; i += 30) {
                ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, h); ctx.stroke();
            }

            // Gerçekçi Koridor Ağları (Yatay & Dikey)
            ctx.fillStyle = "#111827";
            ctx.fillRect(0, 130, w, 35);
            ctx.fillRect(0, 270, w, 35);
            ctx.fillRect(530, 0, 35, h);

            // Odaları ve Üzerindeki Barları Çiz
            agentsData.forEach(ag => {
                let rx = ag.room_x;
                let ry = ag.room_y;
                let rw = 160;
                let rh = 105;

                // Oda Dış Çerçevesi
                ctx.fillStyle = "rgba(17, 24, 39, 0.9)";
                ctx.fillRect(rx, ry, rw, rh);
                ctx.strokeStyle = ag.color;
                ctx.lineWidth = 2;
                ctx.strokeRect(rx, ry, rw, rh);

                // Oda Başlığı
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(`${ag.name} (${ag.role})`, rx + 8, ry + 12);

                // Saksı & Sağlık
                ctx.fillStyle = "#78350f";
                ctx.fillRect(rx + 10, ry + 22, 14, 16);
                ctx.fillStyle = "#4ade80"; ctx.font = "10px sans-serif";
                ctx.fillText("🌿", rx + 8, ry + 34);
                ctx.fillStyle = "#4ade80"; ctx.font = "8px 'Courier New'";
                ctx.fillText(`${ag.plant_health}%`, rx + 26, ry + 32);

                // AÇLIK, SUSUZLUK, KAFEİN, ENERJİ Barlarları Odasının Üstünde/İçinde
                let bars = [
                    {label: "Açlık", val: ag.hunger, y: 44, col: "#f59e0b", thresh: 50},
                    {label: "Susuz", val: ag.thirst, y: 56, col: "#38bdf8", thresh: 65},
                    {label: "Kafein", val: ag.caffeine, y: 68, col: "#ec4899", thresh: 55},
                    {label: "Enerji", val: ag.energy, y: 80, col: "#10b981", thresh: 30}
                ];

                bars.forEach(b => {
                    ctx.fillStyle = "#1e293b"; ctx.fillRect(rx + 50, ry + b.y, 65, 8);
                    ctx.fillStyle = b.val < b.thresh ? "#ef4444" : b.col; 
                    ctx.fillRect(rx + 50, ry + b.y, (b.val / 100) * 65, 8);
                    ctx.fillStyle = "#fff"; ctx.font = "7px 'Courier New'";
                    ctx.fillText(`${b.label}:${b.val}%`, rx + 118, ry + b.y + 7);
                });

                // Ajan Durum Kutusu / Konuşma
                ctx.fillStyle = ag.color;
                ctx.fillRect(rx + 8, ry + 91, 144, 12);
                ctx.fillStyle = "#030712"; ctx.font = "bold 7px 'Courier New'";
                ctx.fillText(ag.speech.substring(0, 26), rx + 10, ry + 99);
            });

            // Sağ Taraf Özel Odalar (Mutfak, CEO, Onay Odası)
            ctx.fillStyle = "rgba(120, 53, 15, 0.45)";
            ctx.fillRect(580, 15, 485, 110);
            ctx.strokeStyle = "#d97706"; ctx.lineWidth = 2; ctx.strokeRect(580, 15, 485, 110);
            ctx.fillStyle = "#fde68a"; ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("☕ MUTFAK & KAHVE İSTASYONU (Mola Alanı)", 595, 30);

            ctx.fillStyle = "rgba(2, 132, 199, 0.25)";
            ctx.fillRect(580, 135, 485, 30);
            ctx.strokeStyle = "#38bdf8"; ctx.strokeRect(580, 135, 485, 30);
            ctx.fillStyle = "#38bdf8"; ctx.fillText("👑 CEO KONTROL MERKEZİ", 600, 153);

            ctx.fillStyle = "rgba(109, 40, 217, 0.35)";
            ctx.fillRect(580, 175, 485, 250);
            ctx.strokeStyle = "#8b5cf6"; ctx.strokeRect(580, 175, 485, 250);
            ctx.fillStyle = "#e9d5ff"; ctx.fillText("🤝 OTONOM PROJE ONAY ODASI & SUNUCU LABI", 600, 195);

            // Sunucu Kabinleri Görseli
            ctx.fillStyle = "#1e1b4b"; ctx.fillRect(600, 220, 70, 180);
            ctx.strokeStyle = "#38bdf8"; ctx.strokeRect(600, 220, 70, 180);
            for(let sy=230; sy<390; sy+=25) {
                ctx.fillStyle = "#38bdf8"; ctx.fillRect(610, sy, 10, 8);
                ctx.fillStyle = "#4ade80"; ctx.fillRect(630, sy, 8, 8);
                ctx.fillStyle = "#ef4444"; ctx.fillRect(650, sy, 6, 6);
            }
        }

        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                document.getElementById('stat-budget').innerText = data.budget;
                document.getElementById('stat-clients').innerText = data.active_clients;
                agentsData = data.agents;
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
            appendLog(`> [SİSTEM]: ${agentName} odasına koşuyor ve talimatı işliyor...`);

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
            appendLog(`> [SİSTEM UPTIME]: Sorgulanıyor...`);
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
    tick_counter += 1

    if tick_counter % 10 == 0:
        company_state["budget"] += random.randint(1500, 3500)
        company_state["active_clients"] = random.randint(4, 9)

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        # Otonom ihtiyaç mekanizması (Açlık<%50, Susuzluk<%65, Kafein<%55, Yorgunluk/Enerji<%30)
        for name in employees_meta:
            h_delta = random.randint(-4, 2)
            t_delta = random.randint(-5, 2)
            c_delta = random.randint(-4, 2)
            e_delta = random.randint(-3, 2)

            cur.execute("""
                UPDATE agents_state 
                SET hunger = GREATEST(10, LEAST(100, hunger + %s)),
                    thirst = GREATEST(10, LEAST(100, thirst + %s)),
                    caffeine = GREATEST(10, LEAST(100, caffeine + %s)),
                    energy = GREATEST(10, LEAST(100, energy + %s))
                WHERE name = %s RETURNING hunger, thirst, caffeine, energy;
            """, (h_delta, t_delta, c_delta, e_delta, name))
            
            row = cur.fetchone()
            if row:
                h, t, c, e = row
                speech = "Masada Çalışıyor"
                location = "Ofiste"

                if h < 50:
                    speech = "Acıktım! Mutfağa gidiyorum..."
                    location = "Mutfakta"
                elif t < 65:
                    speech = "Çok susadım! Su içiyorum..."
                    location = "Mutfakta"
                elif c < 55:
                    speech = "Kafein azaldı! Kahve alıyorum..."
                    location = "Mutfakta"
                elif e < 35:
                    speech = "Yorgunluk %95! Dinleniyorum..."
                    location = "Dinlenme Alanında"
                else:
                    speech = "Projeler kodlanıyor..."

                cur.execute("UPDATE agents_state SET speech = %s, location = %s WHERE name = %s", (speech, location, name))

        conn.commit()

        cur.execute("SELECT name, role, hunger, thirst, caffeine, energy, location, speech, plant_health FROM agents_state;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        agents_list = []
        for r in rows:
            name = r[0]
            meta = employees_meta.get(name, {"room_x": 15, "room_y": 15, "color": "#38bdf8"})
            agents_list.append({
                "name": name, "role": r[1], "hunger": r[2], "thirst": r[3],
                "caffeine": r[4], "energy": r[5], "location": r[6], "speech": r[7],
                "plant_health": r[8], "color": meta["color"],
                "room_x": meta["room_x"], "room_y": meta["room_y"]
            })

        return jsonify({"agents": agents_list, "budget": company_state["budget"], "active_clients": company_state["active_clients"]})
    except Exception as e:
        print(f"Tick Hatası: {e}")
        return jsonify({"agents": [], "budget": company_state["budget"], "active_clients": company_state["active_clients"]})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, meta=employees_meta)

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
    except:
        return "Proje bulunamadı.", 404

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    agent_name = data.get('agent', 'Brown')
    user_message = data.get('message', '')

    html_code = ""
    reply = ""
    preview_url = None

    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("UPDATE agents_state SET speech = 'Odasına koştu, talimatı işliyor!' WHERE name = %s", (agent_name,))
        conn.commit()
        cur.close()
        conn.close()
    except: pass

    if agent_name != "Brown":
        try:
            if groq_client:
                prompt = f"Sen ofiste çalışan bir uzmansın. Patronun sana şu mesajı gönderdi: '{user_message}'. Kısa ve profesyonel bir iş yanıtı ver."
                comp = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300, temperature=0.7
                )
                reply = comp.choices[0].message.content.strip()
        except:
            reply = f"Patron, talimatınız işleme alındı."
        if not reply: reply = "Notumuzu aldık patron!"
    else:
        reply = "Patron, GPT-OSS 120B motoru ile site kodlandı!"
        try:
            if groq_client:
                code_prompt = f"Sadece eksiksiz bir HTML/CSS web sitesi yaz. Asla markdown veya açıklama kullanma. İstek: {user_message}"
                comp = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": code_prompt}],
                    max_tokens=4000, temperature=0.7
                )
                raw_code = comp.choices[0].message.content.strip()
                clean_code = re.sub(r'```[a-zA-Z]*', '', raw_code).replace('```', '')
                
                s_idx = clean_code.lower().find("<html")
                e_idx = clean_code.lower().rfind("</html>")
                html_code = clean_code[s_idx:e_idx+7] if s_idx != -1 and e_idx != -1 else clean_code
        except:
            pass

        if not html_code or "<html" not in html_code.lower():
            html_code = "<!DOCTYPE html><html><head><title>Proje</title></head><body><h1>Özel Konsept</h1></body></html>"

        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("INSERT INTO client_orders (client_name, project_type, repo_url, html_code) VALUES (%s, %s, %s, %s) RETURNING id", 
                        ("Brown (Yazılımcı)", user_message[:40], "Canlı Web Servis", html_code))
            project_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            preview_url = f"{request.host_url.rstrip('/')}/preview/{project_id}"
        except: pass

    log_to_supabase(agent_name, "CHAT", f"Talimat: {user_message}")
    return jsonify({"status": reply, "preview_url": preview_url})

@app.route('/api/uptime', methods=['GET'])
def api_uptime():
    return jsonify({"status": check_system_uptime()})

@app.route('/api/memory', methods=['GET'])
def api_memory():
    return jsonify({"summary": "Supabase veritabanı ve otonom ihtiyaç simülasyonu aktif."})

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
    return jsonify({"decision": "Yönetim kurulu canlı otonom ofis simülasyonunu onayladı."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
