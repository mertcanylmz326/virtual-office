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
            CREATE TABLE IF NOT EXISTS office_plants (
                id SERIAL PRIMARY KEY,
                plant_name TEXT,
                health_level INT DEFAULT 100,
                water_status TEXT DEFAULT 'Çok İyi'
            );
        """)
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Cyber Saksı', 90) ON CONFLICT (id) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

employees = {
    "Marco": {"role": "Destek", "x": 100, "y": 80, "target_x": 100, "target_y": 80, "color": "#3b82f6", "state": "Çalışıyor"},
    "Talisca": {"role": "Operasyon", "x": 380, "y": 80, "target_x": 380, "target_y": 80, "color": "#ef4444", "state": "Çalışıyor"},
    "Brown": {"role": "Yazılım", "x": 660, "y": 80, "target_x": 660, "target_y": 80, "color": "#10b981", "state": "Çalışıyor"},
    "Kante": {"role": "Pazarlama", "x": 100, "y": 210, "target_x": 100, "target_y": 210, "color": "#f59e0b", "state": "Çalışıyor"},
    "İrfan": {"role": "Finans", "x": 380, "y": 210, "target_x": 380, "target_y": 210, "color": "#8b5cf6", "state": "Çalışıyor"},
    "İsmail": {"role": "İK", "x": 660, "y": 210, "target_x": 660, "target_y": 210, "color": "#f97316", "state": "Çalışıyor"},
    "Alex": {"role": "Hukuk", "x": 100, "y": 340, "target_x": 100, "target_y": 340, "color": "#14b8a6", "state": "Çalışıyor"},
    "Skrinar": {"role": "Siber", "x": 380, "y": 340, "target_x": 380, "target_y": 340, "color": "#64748b", "state": "Çalışıyor"},
    "Kerem": {"role": "Başarı", "x": 660, "y": 340, "target_x": 660, "target_y": 340, "color": "#ec4899", "state": "Çalışıyor"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Cyber 3D Strategy HQ</title>
    <style>
        body { 
            background-color: #020617; 
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
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.2);
        }
        .top-btn { 
            background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 5px 12px; 
            border-radius: 4px; font-weight: bold; cursor: pointer; transition: all 0.2s;
        }
        .top-btn:hover { background: #38bdf8; color: #020617; box-shadow: 0 0 10px #38bdf8; }

        #office-floor { 
            position: relative; 
            width: 980px; 
            height: 520px; 
            margin: 15px auto; 
            background-color: #090d16;
            background-image: 
                linear-gradient(90deg, rgba(56,189,248,0.04) 1px, transparent 1px),
                linear-gradient(rgba(56,189,248,0.04) 1px, transparent 1px);
            background-size: 40px 40px;
            border: 4px solid #38bdf8; 
            border-radius: 12px; 
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.3), inset 0 0 50px rgba(0,0,0,0.8); 
            overflow: hidden;
            transform: perspective(1000px) rotateX(2deg); /* Hafif 3D Derinlik Hissiyatı */
        }

        .room {
            position: absolute;
            border: 2px solid #334155;
            background: rgba(15, 23, 42, 0.85);
            border-radius: 6px;
            width: 270px;
            height: 120px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }
        .room-label { position: absolute; font-size: 8px; color: #38bdf8; top: 4px; left: 8px; font-weight: bold; }
        
        .kitchen-area {
            position: absolute; left: 810px; top: 15px; width: 155px; height: 230px;
            border: 2px dashed #f59e0b; background: rgba(245, 158, 11, 0.1); border-radius: 6px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #fde68a;
            box-shadow: 0 0 15px rgba(245, 158, 11, 0.2);
        }
        .boardroom-area {
            position: absolute; left: 810px; top: 260px; width: 155px; height: 245px;
            border: 2px dashed #a855f7; background: rgba(168, 85, 247, 0.1); border-radius: 6px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #e9d5ff;
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.2);
        }

        .plant-pot {
            position: absolute; width: 35px; height: 35px; background: #78350f; border: 2px solid #b45309;
            border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 16px; z-index: 10;
            box-shadow: 0 0 10px rgba(180, 83, 9, 0.5);
        }
        .plant-status { position: absolute; top: -14px; font-size: 7px; background: #000; color: #4ade80; padding: 1px 4px; border-radius: 3px; white-space: nowrap; border: 1px solid #4ade80; }

        .footprint {
            position: absolute; width: 5px; height: 5px; background: rgba(56, 189, 248, 0.5);
            border-radius: 50%; pointer-events: none; z-index: 15; animation: fadeOut 1.5s forwards;
            box-shadow: 0 0 4px #38bdf8;
        }
        @keyframes fadeOut { 0% { opacity: 0.8; } 100% { opacity: 0; transform: scale(1.8); } }

        .agent { 
            position: absolute; width: 45px; height: 55px; cursor: pointer; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            transition: transform 0.2s; z-index: 40;
        }
        .robot-sprite {
            width: 28px; height: 28px; background-color: #0f172a; border: 2px solid; border-radius: 6px;
            display: flex; align-items: center; justify-content: center; font-size: 14px; 
            box-shadow: 0 0 10px rgba(0,0,0,0.9), inset 0 0 5px rgba(255,255,255,0.2);
        }
        .agent-name { font-size: 7px; font-weight: bold; background: rgba(15, 23, 42, 0.95); padding: 1px 3px; border-radius: 3px; margin-top: 2px; white-space: nowrap; border: 1px solid #334155; }
        .speech-bubble {
            position: absolute; top: -22px; background: #f8fafc; color: #0f172a; font-size: 6px; font-weight: bold;
            padding: 2px 5px; border-radius: 3px; white-space: nowrap; box-shadow: 0 0 8px rgba(255,255,255,0.5); pointer-events: none;
        }

        .action-bar { margin: 15px auto; width: 980px; display: flex; justify-content: space-between; gap: 10px; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 10px; border-radius: 8px; display: flex; gap: 10px; align-items: center; flex-grow: 1;
            box-shadow: 0 0 15px rgba(0,0,0,0.5);
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; box-shadow: 0 0 10px rgba(2, 132, 199, 0.5); }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 20px auto; width: 980px; background: #020617; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.8);
        }
        .terminal-header { background: #0f172a; padding: 8px 15px; font-size: 11px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 10px; height: 100px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; }
        .log-line { margin-bottom: 4px; border-bottom: 1px dashed rgba(255,255,255,0.05); }

        /* RPG Karakter Modal Kartı */
        #agent-modal {
            display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #0f172a; border: 2px solid #38bdf8; padding: 20px; border-radius: 10px; z-index: 1000;
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.5); width: 300px; text-align: left;
        }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO // CYBER 3D STRATEGY HQ</div>
        <div>
            <span class="top-btn" onclick="checkPlantStatus()">🌿 BİTKİ DURUMU</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULAMA YAP</span>
        </div>
    </div>

    <!-- 3D İzometrik Hissiyatlı Ofis Haritası -->
    <div id="office-floor">
        <div class="room" style="left: 15px; top: 15px;"><div class="room-label">MARCO (DESTEK)</div></div>
        <div class="room" style="left: 300px; top: 15px;"><div class="room-label">TALİSCA (OPERASYON)</div></div>
        <div class="room" style="left: 585px; top: 15px;"><div class="room-label">BROWN (YAZILIM)</div></div>
        
        <div class="room" style="left: 15px; top: 150px;"><div class="room-label">KANTE (PAZARLAMA)</div></div>
        <div class="room" style="left: 300px; top: 150px;"><div class="room-label">İRFAN (FİNANS)</div></div>
        <div class="room" style="left: 585px; top: 150px;"><div class="room-label">İSMAİL (İK)</div></div>

        <div class="room" style="left: 15px; top: 285px;"><div class="room-label">ALEX (HUKUK)</div></div>
        <div class="room" style="left: 300px; top: 285px;"><div class="room-label">SKRİNAR (SİBER)</div></div>
        <div class="room" style="left: 585px; top: 285px;"><div class="room-label">KEREM (BAŞARI)</div></div>

        <!-- Mutfak ve Toplantı Alanı -->
        <div class="kitchen-area">☕ MUTFAK & KAHVE</div>
        <div class="boardroom-area">🤝 OTONOM ZİRVE</div>

        <!-- Saksılar -->
        <div class="plant-pot" style="left: 270px; top: 110px;" id="plant-1">
            <span class="plant-status" id="plant-status-1">🌿 %90</span>🌱
        </div>
        <div class="plant-pot" style="left: 765px; top: 110px;" id="plant-2">
            <span class="plant-status" id="plant-status-2">🌿 %90</span>🌵
        </div>

        <!-- Ajanlar -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" onclick="openAgentCard('{{ name }}', '{{ data.role }}')">
            <div class="speech-bubble" id="bubble-{{ name }}">{{ data.state }}</div>
            <div class="robot-sprite" style="border-color: {{ data.color }};">🤖</div>
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
            <input type="text" id="ceo-message" placeholder="Stratejik komut ver..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">EMİR GÖNDER</button>
        </div>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ CYBER STRATEGY OPERATIONS TERMINAL</span>
            <span style="color: #34d399;">● 3D SIMULATION ACTIVE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Cyber 3D strateji arayüzü ve otonom hareket motoru yüklendi.</div>
        </div>
    </div>

    <!-- RPG Karakter Bilgi Kartı (Modal) -->
    <div id="agent-modal">
        <h3 id="modal-title" style="color: #38bdf8; margin-top: 0;"></h3>
        <p id="modal-role" style="font-size: 12px; color: #94a3b8;"></p>
        <p id="modal-status" style="font-size: 12px; color: #4ade80;"></p>
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
            document.getElementById('modal-title').innerText = "🤖 " + name;
            document.getElementById('modal-role').innerText = "Departman: " + role;
            document.getElementById('modal-status').innerText = "Anlık Durum: Aktif ve otonom görevde.";
            document.getElementById('agent-modal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('agent-modal').style.display = 'none';
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        // Akıcı Hareket ve Ayak İzi Döngüsü
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
                        createFootprint(agent.x + 20, agent.y + 45);
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
            setTimeout(() => fp.remove(), 1500);
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
                if(data.action_type === 'kitchen') appendLog(`> [OTONOM]: ${agentName} kahve molasına çıktı.`);
                if(data.action_type === 'boardroom') appendLog(`> [OTONOM]: ${agentName} zirve odasına geçti.`);
            });
        }

        function checkPlantStatus() {
            fetch('/api/plants').then(res => res.json()).then(data => {
                appendLog(`> [SİSTEM BİTKİ BİLGİSİ]: ${data.status_text}`);
            });
        }

        function triggerWatering() {
            fetch('/api/water-plants', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [SULAMA BAŞarILI]: Saksılar sulandı, bitki sağlığı %100!`);
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

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    agent_list = []
    for name, data in employees.items():
        if random.random() < 0.2:
            destinations = [
                (data["home_x"] if "home_x" in data else data["x"], data["home_y"] if "home_y" in data else data["y"]),
                (850, random.randint(40, 180)),
                (850, random.randint(280, 420))
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest
            if dest[0] > 800:
                data["state"] = "☕ Molada" if dest[1] < 200 else "🤝 Toplantıda"
            else:
                data["state"] = "💻 Kodluyor" if name == "Brown" else ("📊 Analizde" if name == "İrfan" else "Çalışıyor")

        if data["x"] < data["target_x"]: data["x"] += min(15, data["target_x"] - data["x"])
        elif data["x"] > data["target_x"]: data["x"] -= min(15, data["x"] - data["target_x"])

        if data["y"] < data["target_y"]: data["y"] += min(15, data["target_y"] - data["y"])
        elif data["y"] > data["target_y"]: data["y"] -= min(15, data["y"] - data["target_y"])

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

    action_type = "chat"
    if "kahve" in user_message.lower() or "mola" in user_message.lower():
        agent["target_x"], agent["target_y"] = 850, 100
        agent["state"] = "Kahve Molasında"
        action_type = "kitchen"
    elif "toplantı" in user_message.lower():
        agent["target_x"], agent["target_y"] = 850, 320
        agent["state"] = "Zirvede"
        action_type = "boardroom"

    try:
        system_prompt = f"Sen E-Trade Pro şirketinde {agent['role']} olarak çalışan {agent_name} adında bir uzmansın. Patronun Mertcan sana yazdı: '{user_message}'. Kısa, stratejik ve net bir yanıt ver."
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=150, temperature=0.7
        )
        reply = completion.choices[0].message.content.strip('"').strip()
    except:
        reply = "Emredersiniz patron, görev başındayım."

    log_to_supabase(agent_name, action_type, f"Soru: {user_message} | Cevap: {reply}")
    return jsonify({"status": reply, "action_type": action_type})

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
