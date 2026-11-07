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
                water_status TEXT DEFAULT 'Mükemmel'
            );
        """)
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Cyber Saksı', 100) ON CONFLICT (id) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

# Her ajanın kendi odasının merkez koordinatları (Ev / Başlangıç noktası)
employees = {
    "Marco": {"role": "Destek", "home_x": 75, "home_y": 70, "x": 75, "y": 70, "target_x": 75, "target_y": 70, "color": "#3b82f6", "state": "Ofisinde"},
    "Talisca": {"role": "Operasyon", "home_x": 285, "home_y": 70, "x": 285, "y": 70, "target_x": 285, "target_y": 70, "color": "#ef4444", "state": "Ofisinde"},
    "Brown": {"role": "Yazılım", "home_x": 495, "home_y": 70, "x": 495, "y": 70, "target_x": 495, "target_y": 70, "color": "#10b981", "state": "Ofisinde"},
    
    "Kante": {"role": "Pazarlama", "home_x": 75, "home_y": 200, "x": 75, "y": 200, "target_x": 75, "target_y": 200, "color": "#f59e0b", "state": "Ofisinde"},
    "İrfan": {"role": "Finans", "home_x": 285, "home_y": 200, "x": 285, "y": 200, "target_x": 285, "target_y": 200, "color": "#8b5cf6", "state": "Ofisinde"},
    "İsmail": {"role": "İK", "home_x": 495, "home_y": 200, "x": 495, "y": 200, "target_x": 495, "target_y": 200, "color": "#f97316", "state": "Ofisinde"},
    
    "Alex": {"role": "Hukuk", "home_x": 75, "home_y": 330, "x": 75, "y": 330, "target_x": 75, "target_y": 330, "color": "#14b8a6", "state": "Ofisinde"},
    "Skrinar": {"role": "Siber", "home_x": 285, "home_y": 330, "x": 285, "y": 330, "target_x": 285, "target_y": 330, "color": "#64748b", "state": "Ofisinde"},
    "Kerem": {"role": "Başarı", "home_x": 495, "home_y": 330, "x": 495, "y": 330, "target_x": 495, "target_y": 330, "color": "#ec4899", "state": "Ofisinde"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - 3D Isometric Cyber Office</title>
    <style>
        body { 
            background-color: #010409; 
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
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.3);
        }
        .top-btn { 
            background: #1e293b; color: #38bdf8; border: 1px solid #38bdf8; padding: 6px 14px; 
            border-radius: 6px; font-weight: bold; cursor: pointer; transition: all 0.2s;
        }
        .top-btn:hover { background: #38bdf8; color: #010409; box-shadow: 0 0 12px #38bdf8; }

        /* 3D İzometrik Ofis Sahnesi */
        #office-container {
            perspective: 1200px;
            margin: 20px auto;
            width: 1020px;
            height: 520px;
        }

        #office-floor { 
            position: relative; 
            width: 1020px; 
            height: 500px; 
            background-color: #0b1120;
            /* Parke ve zemin dokusu */
            background-image: 
                linear-gradient(90deg, rgba(56,189,248,0.05) 1px, transparent 1px),
                linear-gradient(rgba(56,189,248,0.05) 1px, transparent 1px);
            background-size: 30px 30px;
            border: 4px solid #38bdf8; 
            border-radius: 12px; 
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.9), inset 0 0 60px rgba(0,0,0,0.8); 
            overflow: hidden;
            transform: rotateX(18deg); /* Gerçek 3D Oyun Görünümü */
            transform-style: preserve-3d;
        }

        /* Ana Koridor Şeridi */
        .hallway-h {
            position: absolute; left: 0; right: 0; height: 35px; background: rgba(30, 41, 59, 0.4);
            border-top: 1px dashed rgba(56,189,248,0.2); border-bottom: 1px dashed rgba(56,189,248,0.2);
        }
        .hallway-v {
            position: absolute; top: 0; bottom: 0; width: 40px; background: rgba(30, 41, 59, 0.4);
            border-left: 1px dashed rgba(56,189,248,0.2); border-right: 1px dashed rgba(56,189,248,0.2);
        }

        /* Düzenli Odalar */
        .room {
            position: absolute;
            border: 2px solid #334155;
            background: rgba(15, 23, 42, 0.9);
            border-radius: 8px;
            width: 195px;
            height: 110px;
            box-shadow: inset 0 0 12px rgba(0,0,0,0.7);
        }
        .room-label { position: absolute; font-size: 7px; color: #38bdf8; top: 4px; left: 6px; font-weight: bold; text-transform: uppercase; }

        /* Sağ Taraf: Mutfak ve Toplantı Odası */
        .kitchen-room {
            position: absolute; left: 780px; top: 15px; width: 220px; height: 220px;
            border: 2px solid #f59e0b; background: rgba(120, 53, 15, 0.2); border-radius: 8px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #fde68a;
            box-shadow: inset 0 0 15px rgba(245, 158, 11, 0.3);
        }
        .boardroom {
            position: absolute; left: 780px; top: 255px; width: 220px; height: 225px;
            border: 2px solid #a855f7; background: rgba(109, 40, 217, 0.2); border-radius: 8px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #e9d5ff;
            box-shadow: inset 0 0 15px rgba(168, 85, 247, 0.3);
        }

        /* Saksılar */
        .plant-pot {
            position: absolute; width: 30px; height: 30px; background: #78350f; border: 2px solid #b45309;
            border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 14px; z-index: 10;
        }
        .plant-status { position: absolute; top: -14px; font-size: 6px; background: #000; color: #4ade80; padding: 1px 3px; border-radius: 3px; white-space: nowrap; border: 1px solid #4ade80; }

        /* Ayak İzleri */
        .footprint {
            position: absolute; width: 4px; height: 4px; background: rgba(56, 189, 248, 0.6);
            border-radius: 50%; pointer-events: none; z-index: 15; animation: fadeOut 1.2s forwards;
        }
        @keyframes fadeOut { 0% { opacity: 0.8; } 100% { opacity: 0; transform: scale(1.5); } }

        /* Ajanlar */
        .agent { 
            position: absolute; width: 40px; height: 50px; cursor: pointer; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            transition: transform 0.2s; z-index: 40;
        }
        .robot-sprite {
            width: 26px; height: 26px; background-color: #0f172a; border: 2px solid; border-radius: 6px;
            display: flex; align-items: center; justify-content: center; font-size: 12px; 
            box-shadow: 0 0 8px rgba(0,0,0,0.9);
        }
        .agent-name { font-size: 6px; font-weight: bold; background: rgba(15, 23, 42, 0.95); padding: 1px 2px; border-radius: 2px; margin-top: 1px; white-space: nowrap; border: 1px solid #334155; }
        .speech-bubble {
            position: absolute; top: -20px; background: #f8fafc; color: #0f172a; font-size: 6px; font-weight: bold;
            padding: 2px 4px; border-radius: 3px; white-space: nowrap; box-shadow: 0 0 6px rgba(255,255,255,0.5); pointer-events: none;
        }

        .action-bar { margin: 15px auto; width: 1020px; display: flex; justify-content: space-between; gap: 10px; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 10px; border-radius: 8px; display: flex; gap: 10px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 20px auto; width: 1020px; background: #020617; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden;
        }
        .terminal-header { background: #0f172a; padding: 8px 15px; font-size: 11px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 10px; height: 90px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; }
        .log-line { margin-bottom: 4px; border-bottom: 1px dashed rgba(255,255,255,0.05); }

        #agent-modal {
            display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #0f172a; border: 2px solid #38bdf8; padding: 20px; border-radius: 10px; z-index: 1000;
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.5); width: 280px; text-align: left;
        }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO // STABLE 3D ISOMETRIC HQ</div>
        <div>
            <span class="top-btn" onclick="checkPlantStatus()">🌿 BİTKİ DURUMU</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULAMA YAP</span>
        </div>
    </div>

    <!-- 3D Sahne Konteyneri -->
    <div id="office-container">
        <div id="office-floor">
            <!-- Koridorlar -->
            <div class="hallway-h" style="top: 130px;"></div>
            <div class="hallway-h" style="top: 260px;"></div>
            <div class="hallway-v" style="left: 235px;"></div>
            <div class="hallway-v" style="left: 540px;"></div>

            <!-- Sol ve Orta Bölüm: 9 Özgün Oda -->
            <div class="room" style="left: 20px; top: 15px;"><div class="room-label">1. MARCO (DESTEK)</div></div>
            <div class="room" style="left: 245px; top: 15px;"><div class="room-label">2. TALİSCA (OPERASYON)</div></div>
            <div class="room" style="left: 475px; top: 15px;"><div class="room-label">3. BROWN (YAZILIM)</div></div>
            
            <div class="room" style="left: 20px; top: 145px;"><div class="room-label">4. KANTE (PAZARLAMA)</div></div>
            <div class="room" style="left: 245px; top: 145px;"><div class="room-label">5. İRFAN (FİNANS)</div></div>
            <div class="room" style="left: 475px; top: 145px;"><div class="room-label">6. İSMAİL (İK)</div></div>

            <div class="room" style="left: 20px; top: 275px;"><div class="room-label">7. ALEX (HUKUK)</div></div>
            <div class="room" style="left: 245px; top: 275px;"><div class="room-label">8. SKRİNAR (SİBER)</div></div>
            <div class="room" style="left: 475px; top: 275px;"><div class="room-label">9. KEREM (BAŞARI)</div></div>

            <!-- Sağ Taraf: Mutfak ve Zirve Odası -->
            <div class="kitchen-room">☕ MUTFAK & KAHVE ALANI</div>
            <div class="boardroom">🤝 OTONOM ZİRVE ODASI</div>

            <!-- Saksılar -->
            <div class="plant-pot" style="left: 215px; top: 90px;" id="plant-1">
                <span class="plant-status" id="plant-status-1">🌿 %100</span>🌱
            </div>
            <div class="plant-pot" style="left: 730px; top: 90px;" id="plant-2">
                <span class="plant-status" id="plant-status-2">🌿 %100</span>🌵
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
    </div>

    <!-- Kontrol Paneli -->
    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name, data in employees.items() %}
                <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Stratejik emir ver..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">EMİR GÖNDER</button>
        </div>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ STABLE 3D OPERATIONS TERMINAL</span>
            <span style="color: #34d399;">● GRID & CORRIDOR SYNCED</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Kararlı 3D izometrik şebeke, koridorlar ve çakışma koruması etkinleştirildi.</div>
        </div>
    </div>

    <!-- RPG Kartı -->
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
            document.getElementById('modal-status').innerText = "Anlık Durum: Kararlı odasında görevde.";
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
                        createFootprint(agent.x + 18, agent.y + 42);
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
                if(data.action_type === 'kitchen') appendLog(`> [OTONOM]: ${agentName} mutfağa geçti.`);
                if(data.action_type === 'boardroom') appendLog(`> [OTONOM]: ${agentName} zirve odasına geçti.`);
            });
        }

        function checkPlantStatus() {
            fetch('/api/plants').then(res => res.json()).then(data => {
                appendLog(`> [BİTKİ BİLGİSİ]: ${data.status_text}`);
            });
        }

        function triggerWatering() {
            fetch('/api/water-plants', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [SULAMA]: Çiçekler sulandı, sağlık %100!`);
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
            # Hedefler: Ya kendi odası (home) ya Mutfak ya da Zirve Odası
            destinations = [
                (data["home_x"], data["home_y"]),
                (random.randint(810, 930), random.randint(40, 180)),   # Mutfak içi
                (random.randint(810, 930), random.randint(280, 420))  # Toplantı odası içi
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest
            if dest[0] > 700:
                data["state"] = "☕ Molada" if dest[1] < 220 else "🤝 Toplantıda"
            else:
                data["state"] = "Ofisinde"

        # Hedefe doğru akıcı ilerleme
        if data["x"] < data["target_x"]: data["x"] += min(12, data["target_x"] - data["x"])
        elif data["x"] > data["target_x"]: data["x"] -= min(12, data["x"] - data["target_x"])

        if data["y"] < data["target_y"]: data["y"] += min(12, data["target_y"] - data["y"])
        elif data["y"] > data["target_y"]: data["y"] -= min(12, data["y"] - data["target_y"])

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
        system_prompt = f"Sen E-Trade Pro şirketinde {agent['role']} olarak çalışan {agent_name} adında bir uzmansın. Patronun Mertcan sana yazdı: '{user_message}'. Kısa ve profesyonel yanıt ver."
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=150, temperature=0.7
        )
        reply = completion.choices[0].message.content.strip('"').strip()
    except:
        reply = "Emredersiniz patron, buradayım."

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
