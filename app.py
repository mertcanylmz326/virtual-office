import os
import time
import threading
import random
import requests
import psycopg2
from flask import Flask, render_template_string, jsonify, request
from groq import Groq

app = Flask(__name__)

DB_URL = "postgresql://postgres.prphsmgaujdwrqqdmmrd:yaheroyamero@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

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
            CREATE TABLE IF NOT EXISTS company_tasks (
                id SERIAL PRIMARY KEY,
                task_title TEXT,
                assigned_to TEXT,
                status TEXT DEFAULT 'Bekliyor',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS office_plants (
                id SERIAL PRIMARY KEY,
                plant_name TEXT,
                health_level INT DEFAULT 100,
                water_status TEXT DEFAULT 'Mükemmel'
            );
        """)
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Üs Saksısı', 100) ON CONFLICT (id) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

employees = {
    "Marco": {"role": "Destek", "home_x": 45, "home_y": 30, "x": 45, "y": 30, "target_x": 45, "target_y": 30, "color": "#3b82f6", "state": "Masada"},
    "Talisca": {"role": "Operasyon", "home_x": 255, "home_y": 30, "x": 255, "y": 30, "target_x": 255, "target_y": 30, "color": "#ef4444", "state": "Masada"},
    "Brown": {"role": "Yazılım", "home_x": 465, "home_y": 30, "x": 465, "y": 30, "target_x": 465, "target_y": 30, "color": "#10b981", "state": "Masada"},
    
    "Kante": {"role": "Pazarlama", "home_x": 45, "home_y": 175, "x": 45, "y": 175, "target_x": 45, "target_y": 175, "color": "#f59e0b", "state": "Masada"},
    "İrfan": {"role": "Finans", "home_x": 255, "home_y": 175, "x": 255, "y": 175, "target_x": 255, "target_y": 175, "color": "#8b5cf6", "state": "Masada"},
    "İsmail": {"role": "İK", "home_x": 465, "home_y": 175, "x": 465, "y": 175, "target_x": 465, "target_y": 175, "color": "#f97316", "state": "Masada"},
    
    "Alex": {"role": "Hukuk", "home_x": 45, "home_y": 320, "x": 45, "y": 320, "target_x": 45, "target_y": 320, "color": "#14b8a6", "state": "Masada"},
    "Skrinar": {"role": "Siber", "home_x": 255, "home_y": 320, "x": 255, "y": 320, "target_x": 255, "target_y": 320, "color": "#64748b", "state": "Masada"},
    "Kerem": {"role": "Başarı", "home_x": 465, "home_y": 320, "x": 465, "y": 320, "target_x": 465, "target_y": 320, "color": "#ec4899", "state": "Masada"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Detailed AgentSpace HQ</title>
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
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }
        .top-btn { 
            background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 5px 10px; 
            border-radius: 4px; font-weight: bold; cursor: pointer; 
        }
        .top-btn:hover { background: #38bdf8; color: #030712; }

        /* Harita Alanı */
        #office-floor { 
            position: relative; 
            width: 1040px; 
            height: 490px; 
            margin: 10px auto; 
            background-color: #0b0f19;
            border: 4px solid #334155; 
            border-radius: 10px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.9); 
            overflow: hidden;
        }

        /* Gerçekçi Parke Görünümlü Ana Koridorlar */
        .corridor-horizontal {
            position: absolute; left: 0; right: 0; top: 145px; height: 25px;
            background: repeating-linear-gradient(45deg, #1e1b18, #1e1b18 10px, #292524 10px, #292524 20px);
            border-top: 2px solid #44403c; border-bottom: 2px solid #44403c;
        }
        .corridor-vertical {
            position: absolute; top: 0; bottom: 0; left: 690px; width: 30px;
            background: repeating-linear-gradient(0deg, #1e1b18, #1e1b18 10px, #292524 10px, #292524 20px);
            border-left: 2px solid #44403c; border-right: 2px solid #44403c;
        }

        /* Odalar (Kalın Duvarlı, İçerisi Dolu) */
        .office-room {
            position: absolute;
            background: #111827;
            border: 4px solid #475569; /* Kalın Duvar */
            border-radius: 6px;
            width: 205px;
            height: 130px;
            box-shadow: inset 0 0 15px rgba(0,0,0,0.7);
        }
        .room-title {
            position: absolute; top: 3px; left: 5px; font-size: 7px; color: #38bdf8; font-weight: bold;
            background: #020617; padding: 1px 4px; border-radius: 2px; border: 1px solid #1e293b;
        }
        
        /* Oda İçi Detaylı Mobilyalar (Masa, PC, Koltuk, Dosya Dolabı) */
        .desk {
            position: absolute; bottom: 12px; left: 45px; width: 110px; height: 36px;
            background: #1c1917; border: 2px solid #57534e; border-radius: 4px;
            display: flex; align-items: center; justify-content: center;
        }
        .monitor {
            width: 26px; height: 14px; background: #0284c7; border: 1px solid #38bdf8; border-radius: 2px;
            box-shadow: 0 0 6px #38bdf8;
        }
        .bookshelf {
            position: absolute; top: 15px; right: 8px; width: 20px; height: 45px;
            background: #451a03; border: 1px solid #78350f; border-radius: 2px;
        }

        /* Sağ Taraf: Mutfak ve Zirve Odası (İçi Dolu) */
        .kitchen-zone {
            position: absolute; left: 735px; top: 15px; width: 290px; height: 220px;
            border: 4px solid #d97706; background: rgba(120, 53, 15, 0.2); border-radius: 8px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #fde68a;
            font-weight: bold;
        }
        .boardroom-zone {
            position: absolute; left: 735px; top: 255px; width: 290px; height: 220px;
            border: 4px solid #8b5cf6; background: rgba(109, 40, 217, 0.2); border-radius: 8px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #e9d5ff;
            font-weight: bold;
        }

        /* Saksılar */
        .plant-pot {
            position: absolute; width: 28px; height: 28px; background: #78350f; border: 2px solid #b45309;
            border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 13px; z-index: 10;
        }
        .plant-status { position: absolute; top: -12px; font-size: 6px; background: #000; color: #4ade80; padding: 1px 3px; border-radius: 3px; white-space: nowrap; border: 1px solid #4ade80; }

        /* Ayak İzleri */
        .footprint {
            position: absolute; width: 4px; height: 4px; background: rgba(56, 189, 248, 0.6);
            border-radius: 50%; pointer-events: none; z-index: 15; animation: fadeOut 1s forwards;
        }
        @keyframes fadeOut { 0% { opacity: 0.8; } 100% { opacity: 0; transform: scale(1.4); } }

        /* Ajan Kartları ve İkonlar */
        .agent { 
            position: absolute; width: 55px; height: 60px; cursor: pointer; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            transition: transform 0.2s; z-index: 40;
        }
        .agent-card {
            width: 42px; height: 32px; background-color: #0f172a; border: 2px solid; border-radius: 5px;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.9);
        }
        .agent-initials { font-size: 9px; font-weight: bold; line-height: 1; }
        .agent-badge { font-size: 5px; color: #94a3b8; margin-top: 1px; }
        .agent-name { font-size: 6px; font-weight: bold; background: rgba(15, 23, 42, 0.95); padding: 1px 3px; border-radius: 2px; margin-top: 1px; white-space: nowrap; border: 1px solid #334155; }
        .speech-bubble {
            position: absolute; top: -18px; background: #f8fafc; color: #0f172a; font-size: 6px; font-weight: bold;
            padding: 1px 5px; border-radius: 3px; white-space: nowrap; box-shadow: 0 0 6px rgba(255,255,255,0.5); pointer-events: none;
        }

        .action-bar { margin: 10px auto; width: 1040px; display: flex; justify-content: space-between; gap: 10px; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 8px; border-radius: 8px; display: flex; gap: 8px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 6px 10px; border-radius: 6px; font-family: monospace; font-size: 11px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 15px auto; width: 1040px; background: #030712; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden;
        }
        .terminal-header { background: #0f172a; padding: 6px 12px; font-size: 10px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 8px; height: 80px; overflow-y: auto; font-size: 10px; color: #4ade80; line-height: 1.3; }
        .log-line { margin-bottom: 3px; border-bottom: 1px dashed rgba(255,255,255,0.05); }

        #agent-modal {
            display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #0f172a; border: 2px solid #38bdf8; padding: 15px; border-radius: 10px; z-index: 1000;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.4); width: 260px; text-align: left;
        }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO // DETAILED TYCOON HQ</div>
        <div>
            <span class="top-btn" onclick="loadMemory()">🧠 RAG HAFIZA</span>
            <span class="top-btn" onclick="loadTasks()">📋 GÖREVLER</span>
            <span class="top-btn" onclick="triggerBoardroom()">🤝 ZİRVE</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULA</span>
        </div>
    </div>

    <!-- Detaylı 2D Oyun Ofis Haritası -->
    <div id="office-floor">
        <!-- Gerçekçi Parke Koridorlar -->
        <div class="corridor-horizontal"></div>
        <div class="corridor-vertical"></div>

        <!-- Row 1: Marco, Talisca, Brown -->
        <div class="office-room" style="left: 15px; top: 15px;">
            <div class="room-title">1. MARCO (DESTEK)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>
        <div class="office-room" style="left: 225px; top: 15px;">
            <div class="room-title">2. TALİSCA (OPERASYON)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>
        <div class="office-room" style="left: 435px; top: 15px;">
            <div class="room-title">3. BROWN (YAZILIM)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>

        <!-- Row 2: Kante, İrfan, İsmail -->
        <div class="office-room" style="left: 15px; top: 180px;">
            <div class="room-title">4. KANTE (PAZARLAMA)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>
        <div class="office-room" style="left: 225px; top: 180px;">
            <div class="room-title">5. İRFAN (FİNANS)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>
        <div class="office-room" style="left: 435px; top: 180px;">
            <div class="room-title">6. İSMAİL (İK)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>

        <!-- Row 3: Alex, Skrinar, Kerem -->
        <div class="office-room" style="left: 15px; top: 345px;">
            <div class="room-title">7. ALEX (HUKUK)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>
        <div class="office-room" style="left: 225px; top: 345px;">
            <div class="room-title">8. SKRİNAR (SİBER)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>
        <div class="office-room" style="left: 435px; top: 345px;">
            <div class="room-title">9. KEREM (BAŞARI)</div>
            <div class="bookshelf"></div>
            <div class="desk"><div class="monitor"></div></div>
        </div>

        <!-- Sağ Taraf: Mutfak ve Zirve Odası -->
        <div class="kitchen-zone">☕ MUTFAK & SEBİL ALANI</div>
        <div class="boardroom-zone">🤝 OTONOM ZİRVE MASASI</div>

        <!-- Saksılar -->
        <div class="plant-pot" style="left: 700px; top: 110px;" id="plant-1">
            <span class="plant-status" id="plant-status-1">🌿 %100</span>🌱
        </div>
        <div class="plant-pot" style="left: 700px; top: 350px;" id="plant-2">
            <span class="plant-status" id="plant-status-2">🌿 %100</span>🌵
        </div>

        <!-- Ajan Varlıkları -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" onclick="openAgentCard('{{ name }}', '{{ data.role }}')">
            <div class="speech-bubble" id="bubble-{{ name }}">{{ data.state }}</div>
            <div class="agent-card" style="border-color: {{ data.color }}; color: {{ data.color }};">
                <span class="agent-initials">{{ name[:2].upper() }}</span>
                <span class="agent-badge">AI</span>
            </div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <!-- Komuta Paneli -->
    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name, data in employees.items() %}
                <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Stratejik emir ver veya görev oluştur..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ DETAILED TYCOON OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8;">● PARQUET CORRIDORS & WALLS ACTIVE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Kalın duvarlı odalar, parke koridorlar ve iç mobilyalar başarıyla eklendi.</div>
        </div>
    </div>

    <!-- RPG Karakter Kartı -->
    <div id="agent-modal">
        <h3 id="modal-title" style="color: #38bdf8; margin-top: 0;"></h3>
        <p id="modal-role" style="font-size: 11px; color: #94a3b8;"></p>
        <p id="modal-status" style="font-size: 11px; color: #4ade80;"></p>
        <button onclick="closeModal()" class="top-btn" style="width: 100%; margin-top: 10px;">KAPAT</button>
    </div>

    <script>
        const terminalLogs = document.getElementById('terminal-logs');

        function appendLog(text) {
            const time = new Date().toLocaleTimeString();
            const logDiv = document.createElement('div');
            logDiv.className = 'log-line';
            logDiv.innerHTML = `[${time}] ${text}`;
            terminalLogs.prepend(logDiv);
        }

        function selectAgent(name) {
            document.getElementById('agent-select').value = name;
        }

        function openAgentCard(name, role) {
            selectAgent(name);
            document.getElementById('modal-title').innerText = "👤 " + name;
            document.getElementById('modal-role').innerText = "Departman: " + role;
            document.getElementById('modal-status').innerText = "Durum: Ofisinde aktif görevde.";
            document.getElementById('agent-modal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('agent-modal').style.display = 'none';
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                data.agents.forEach(agent => {
                    const el = document.getElementById('agent-' + agent.name);
                    if (!el) return;
                    
                    const oldX = parseInt(el.style.left);
                    const oldY = parseInt(el.style.top);
                    
                    el.style.left = agent.x + 'px';
                    el.style.top = agent.y + 'px';
                    document.getElementById('bubble-' + agent.name).innerText = agent.state;

                    if (Math.abs(oldX - agent.x) > 2 || Math.abs(oldY - agent.y) > 2) {
                        createFootprint(agent.x + 25, agent.y + 45);
                    }
                });
            });
        }, 1800);

        function createFootprint(x, y) {
            const floor = document.getElementById('office-floor');
            const fp = document.createElement('div');
            fp.className = 'footprint';
            fp.style.left = x + 'px';
            fp.style.top = y + 'px';
            floor.appendChild(fp);
            setTimeout(() => fp.remove(), 1200);
        }

        function sendDirectMessage() {
            const agentName = document.getElementById('agent-select').value;
            const messageInput = document.getElementById('ceo-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendLog(`> [CEO -> ${agentName}]: "${messageText}"`);
            messageInput.value = "";

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: agentName, message: messageText })
            })
            .then(res => res.json())
            .then(data => {
                appendLog(`> [<b>${agentName}</b>]: "${data.status}"`);
                if(data.task_created) {
                    appendLog(`> [GÖREV PANOSU]: Yeni görev eklendi -> "${data.task_title}"`);
                }
            })
            .catch(err => {
                appendLog(`> [HATA]: Sunucu ile iletişim kurulamadı.`);
            });
        }

        function loadMemory() {
            appendLog(`> [RAG HAFIZA SORGUSU]: Supabase geçmiş logları yükleniyor...`);
            fetch('/api/memory').then(res => res.json()).then(data => {
                appendLog(`> [HAFIZA ÖZETİ]: ${data.summary}`);
            });
        }

        function loadTasks() {
            appendLog(`> [GÖREV PANOSU (KANBAN)]: Aktif görevler listeleniyor...`);
            fetch('/api/tasks').then(res => res.json()).then(data => {
                appendLog(`> [PANODAKİ İŞLER]: ${data.tasks.join(" | ")}`);
            });
        }

        function triggerBoardroom() {
            appendLog(`> [ZİRVE ODASI]: Otonom zirve toplantısı başlatıldı...`);
            fetch('/api/boardroom', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [ORTAK ZİRVE KARARI]: "${data.decision}"`);
            });
        }

        function checkPlantStatus() {
            fetch('/api/plants').then(res => res.json()).then(data => {
                appendLog(`> [BİTKİ BİLGİSİ]: ${data.status_text}`);
            });
        }

        function triggerWatering() {
            fetch('/api/water-plants', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [SULAMA]: Saksılar sulandı, bitki sağlığı %100!`);
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
    except Exception as e:
        print(f"DB Hatası: {e}")

def query_supabase_memory(query_text):
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT agent_name, content FROM agent_logs ORDER BY id DESC LIMIT 5;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        history_summary = " | ".join([f"{r[0]}: {r[1][:40]}" for r in rows])
        return history_summary if history_summary else "Geçmiş kayıt bulunamadı."
    except:
        return "Hafızaya erişilemedi."

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    agent_list = []
    for name, data in employees.items():
        if random.random() < 0.2:
            destinations = [
                (data["home_x"], data["home_y"]),
                (random.randint(750, 980), random.randint(30, 150)),  # Mutfak
                (random.randint(750, 980), random.randint(270, 400)) # Zirve Odası
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest

        if data["x"] < data["target_x"]: data["x"] += min(12, data["target_x"] - data["x"])
        elif data["x"] > data["target_x"]: data["x"] -= min(12, data["x"] - data["target_x"])

        if data["y"] < data["target_y"]: data["y"] += min(12, data["target_y"] - data["y"])
        elif data["y"] > data["target_y"]: data["y"] -= min(12, data["y"] - data["target_y"])

        # Koordinat bazlı hatasız durum
        if data["x"] >= 720 and data["y"] <= 230:
            data["state"] = "☕ Molada"
        elif data["x"] >= 720 and data["y"] > 230:
            data["state"] = "🤝 Toplantıda"
        elif abs(data["x"] - data["home_x"]) < 15 and abs(data["y"] - data["home_y"]) < 15:
            data["state"] = "Masada"
        else:
            data["state"] = "Yürüyor..."

        agent_list.append({"name": name, "x": data["x"], "y": data["y"], "state": data["state"]})

    return jsonify({"agents": agent_list})

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, employees=employees)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    agent_name = data.get('agent', 'İrfan')
    user_message = data.get('message', '')

    if agent_name not in employees: agent_name = "İrfan"
    agent = employees[agent_name]

    task_created = False
    task_title = ""
    if "görev" in user_message.lower() or "yap" in user_message.lower():
        task_created = True
        task_title = user_message[:40]
        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("INSERT INTO company_tasks (task_title, assigned_to) VALUES (%s, %s)", (task_title, agent_name))
            conn.commit()
            cur.close()
            conn.close()
        except: pass

    try:
        memory_context = query_supabase_memory(user_message)
        system_prompt = (
            f"Sen E-Trade Pro şirketinde {agent['role']} olarak çalışan {agent_name} adında bir uzmansın. "
            f"Patronun Mertcan sana yazdı: '{user_message}'.\n"
            f"[SUPABASE GEÇMİŞ HAFIZA]: {memory_context}\n"
            f"Profesyonel, kısa ve net yanıt ver."
        )
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=150, temperature=0.7
        )
        reply = completion.choices[0].message.content.strip('"').strip()
    except:
        reply = "Emredersiniz patron, talimatınız işleme alındı."

    log_to_supabase(agent_name, "CHAT_RESPONSE", f"Soru: {user_message} | Cevap: {reply}")
    return jsonify({"status": reply, "task_created": task_created, "task_title": task_title})

@app.route('/api/memory', methods=['GET'])
def api_memory():
    summary = query_supabase_memory("genel")
    return jsonify({"summary": summary})

@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT task_title, assigned_to, status FROM company_tasks ORDER BY id DESC LIMIT 5;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tasks = [f"[{r[1]}]: {r[0]} ({r[2]})" for r in rows]
        return jsonify({"tasks": tasks if tasks else ["Aktif görev bulunmuyor."]})
    except:
        return jsonify({"tasks": ["Görevler yüklenemedi."]})

@app.route('/api/boardroom', methods=['POST'])
def api_boardroom():
    try:
        prompt = "Şirket büyümesi için İrfan (Finans) ve Brown (Yazılım) ortak bir stratejik zirve kararı alıyor. İki cümlelik ortak kararı yaz."
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120, temperature=0.7
        )
        decision = completion.choices[0].message.content.strip('"').strip()
        log_to_supabase("ZİRVE_KURULU", "BOARDROOM_DECISION", decision)
        return jsonify({"decision": decision})
    except Exception as e:
        return jsonify({"decision": f"Zirve sırasında hata oluştu."})

@app.route('/api/plants', methods=['GET'])
def api_plants():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT plant_name, health_level, water_status FROM office_plants WHERE id=1;")
        row = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"status_text": f"{row[0]} -> Sağlık: %{row[1]} ({row[2]})"})
    except:
        return jsonify({"status_text": "Bitki durumu okunamadı."})

@app.route('/api/water-plants', methods=['POST'])
def water_plants():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("UPDATE office_plants SET health_level = 100, water_status = 'Mükemmel' WHERE id=1;")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except:
        return jsonify({"success": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
