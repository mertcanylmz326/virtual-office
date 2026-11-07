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
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Üs Saksısı', 100) ON CONFLICT (id) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

# Ajanların ofis içi tam koordinatları (Odalardaki masalarının başı)
employees = {
    "Marco": {"role": "Destek", "home_x": 90, "home_y": 70, "x": 90, "y": 70, "target_x": 90, "target_y": 70, "color": "#3b82f6", "state": "Masada"},
    "Talisca": {"role": "Operasyon", "home_x": 310, "home_y": 70, "x": 310, "y": 70, "target_x": 310, "target_y": 70, "color": "#ef4444", "state": "Masada"},
    "Brown": {"role": "Yazılım", "home_x": 530, "home_y": 70, "x": 530, "y": 70, "target_x": 530, "target_y": 530, "color": "#10b981", "state": "Masada"},
    
    "Kante": {"role": "Pazarlama", "home_x": 90, "home_y": 200, "x": 90, "y": 200, "target_x": 90, "target_y": 200, "color": "#f59e0b", "state": "Masada"},
    "İrfan": {"role": "Finans", "home_x": 310, "home_y": 200, "x": 310, "y": 200, "target_x": 310, "target_y": 200, "color": "#8b5cf6", "state": "Masada"},
    "İsmail": {"role": "İK", "home_x": 530, "home_y": 200, "x": 530, "y": 200, "target_x": 530, "target_y": 200, "color": "#f97316", "state": "Masada"},
    
    "Alex": {"role": "Hukuk", "home_x": 90, "home_y": 330, "x": 90, "y": 330, "target_x": 90, "target_y": 330, "color": "#14b8a6", "state": "Masada"},
    "Skrinar": {"role": "Siber", "home_x": 310, "home_y": 330, "x": 310, "y": 330, "target_x": 310, "target_y": 330, "color": "#64748b", "state": "Masada"},
    "Kerem": {"role": "Başarı", "home_x": 530, "home_y": 330, "x": 530, "y": 330, "target_x": 530, "target_y": 330, "color": "#ec4899", "state": "Masada"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - AgentSpace HQ</title>
    <style>
        body { 
            background-color: #0b0f19; 
            color: #f8fafc; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow-x: hidden; 
        }
        #game-topbar {
            background: #111827;
            border-bottom: 2px solid #ef4444;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
        }
        .top-btn { 
            background: #1f2937; color: #f8fafc; border: 1px solid #374151; padding: 5px 12px; 
            border-radius: 4px; font-weight: bold; cursor: pointer; 
        }
        .top-btn:hover { border-color: #ef4444; }

        /* Üstten Görünüm (Top-Down) Oyun Haritası */
        #office-floor { 
            position: relative; 
            width: 1000px; 
            height: 480px; 
            margin: 15px auto; 
            background-color: #1a2234;
            /* Harita Zemin Dokusu */
            background-image: radial-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px);
            background-size: 20px 20px;
            border: 4px solid #374151; 
            border-radius: 8px; 
            box-shadow: 0 15px 35px rgba(0,0,0,0.8); 
            overflow: hidden;
        }

        /* Ortadaki Ana Koridor */
        .central-hallway {
            position: absolute; left: 0; right: 0; top: 130px; height: 160px;
            background: #151c2c; border-top: 3px solid #27354f; border-bottom: 3px solid #27354f;
        }

        /* Odalar (Üstten Görünüm / Duvarlı Plan) */
        .office-room {
            position: absolute;
            background: #1e293b;
            border: 3px solid #64748b; /* Duvar Rengi */
            border-radius: 4px;
            width: 200px;
            height: 110px;
        }
        .room-title {
            position: absolute; top: 3px; left: 5px; font-size: 7px; color: #38bdf8; font-weight: bold;
            background: #0f172a; padding: 1px 4px; border-radius: 2px; border: 1px solid #334155;
        }
        /* Oda İçi Çalışma Masası */
        .office-desk {
            position: absolute; bottom: 15px; left: 50px; width: 100px; height: 35px;
            background: #292524; border: 2px solid #57534e; border-radius: 4px;
            display: flex; align-items: center; justify-content: center; font-size: 8px; color: #a8a29e;
        }
        .pc-screen {
            width: 24px; height: 14px; background: #0284c7; border: 1px solid #38bdf8; border-radius: 2px;
            box-shadow: 0 0 5px #38bdf8;
        }

        /* Sağ Taraf: Mutfak ve Toplantı Odası */
        .kitchen-zone {
            position: absolute; left: 780px; top: 15px; width: 205px; height: 210px;
            border: 3px solid #d97706; background: rgba(120, 53, 15, 0.2); border-radius: 6px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 9px; color: #fde68a;
        }
        .boardroom-zone {
            position: absolute; left: 780px; top: 255px; width: 205px; height: 210px;
            border: 3px solid #8b5cf6; background: rgba(109, 40, 217, 0.2); border-radius: 6px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 9px; color: #e9d5ff;
        }

        /* Saksılar & Çiçekler */
        .plant-pot {
            position: absolute; width: 28px; height: 28px; background: #78350f; border: 2px solid #b45309;
            border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 12px; z-index: 10;
        }
        .plant-status { position: absolute; top: -12px; font-size: 6px; background: #000; color: #4ade80; padding: 1px 3px; border-radius: 3px; white-space: nowrap; }

        /* Ayak İzleri */
        .footprint {
            position: absolute; width: 4px; height: 4px; background: rgba(56, 189, 248, 0.6);
            border-radius: 50%; pointer-events: none; z-index: 15; animation: fadeOut 1s forwards;
        }
        @keyframes fadeOut { 0% { opacity: 0.8; } 100% { opacity: 0; transform: scale(1.4); } }

        /* Ajanlar */
        .agent { 
            position: absolute; width: 40px; height: 50px; cursor: pointer; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            transition: transform 0.2s; z-index: 40;
        }
        .robot-sprite {
            width: 26px; height: 26px; background-color: #0f172a; border: 2px solid; border-radius: 6px;
            display: flex; align-items: center; justify-content: center; font-size: 12px; 
            box-shadow: 0 3px 6px rgba(0,0,0,0.9);
        }
        .agent-name { font-size: 6px; font-weight: bold; background: rgba(15, 23, 42, 0.95); padding: 1px 2px; border-radius: 2px; margin-top: 1px; white-space: nowrap; border: 1px solid #334155; }
        .speech-bubble {
            position: absolute; top: -18px; background: #f8fafc; color: #0f172a; font-size: 6px; font-weight: bold;
            padding: 2px 4px; border-radius: 3px; white-space: nowrap; box-shadow: 0 0 5px rgba(255,255,255,0.5); pointer-events: none;
        }

        .action-bar { margin: 15px auto; width: 1000px; display: flex; justify-content: space-between; gap: 10px; }
        #command-panel {
            background: #111827; border: 2px solid #374151; padding: 10px; border-radius: 8px; display: flex; gap: 10px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1f2937; color: #fff; border: 1px solid #4b5563; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #ef4444; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #dc2626; }

        #activity-terminal {
            margin: 0 auto 20px auto; width: 1000px; background: #0b0f19; border: 2px solid #374151; border-radius: 8px; text-align: left; overflow: hidden;
        }
        .terminal-header { background: #111827; padding: 8px 15px; font-size: 11px; color: #ef4444; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 10px; height: 90px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; }
        .log-line { margin-bottom: 4px; border-bottom: 1px dashed rgba(255,255,255,0.05); }

        #agent-modal {
            display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #111827; border: 2px solid #ef4444; padding: 20px; border-radius: 10px; z-index: 1000;
            box-shadow: 0 0 25px rgba(239, 68, 68, 0.4); width: 280px; text-align: left;
        }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #ef4444;">🏢 E-TRADE PRO // AGENTSPACE 2D HQ</div>
        <div>
            <span class="top-btn" onclick="checkPlantStatus()">🌿 BİTKİLER</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULA</span>
        </div>
    </div>

    <!-- Üstten Görünüm Oyun Haritası -->
    <div id="office-floor">
        <!-- Ortadaki Ana Geniş Koridor -->
        <div class="central-hallway"></div>

        <!-- Üst Sıra Odalar -->
        <div class="office-room" style="left: 20px; top: 15px;">
            <div class="room-title">1. MARCO (DESTEK)</div>
            <div class="office-desk"><div class="pc-screen"></div></div>
        </div>
        <div class="office-room" style="left: 275px; top: 15px;">
            <div class="room-title">2. TALİSCA (OPERASYON)</div>
            <div class="office-desk"><div class="pc-screen"></div></div>
        </div>
        <div class="office-room" style="left: 530px; top: 15px;">
            <div class="room-title">3. BROWN (YAZILIM)</div>
            <div class="office-desk"><div class="pc-screen"></div></div>
        </div>

        <!-- Alt Sıra Odalar -->
        <div class="office-room" style="left: 20px; top: 315px;">
            <div class="room-title">4. KANTE (PAZARLAMA)</div>
            <div class="office-desk"><div class="pc-screen"></div></div>
        </div>
        <div class="office-room" style="left: 275px; top: 315px;">
            <div class="room-title">5. İRFAN (FİNANS)</div>
            <div class="office-desk"><div class="pc-screen"></div></div>
        </div>
        <div class="office-room" style="left: 530px; top: 315px;">
            <div class="room-title">6. İSMAİL (İK)</div>
            <div class="office-desk"><div class="pc-screen"></div></div>
        </div>

        <!-- Sağ Taraf: Mutfak ve Zirve Toplantı Odası -->
        <div class="kitchen-zone">☕ MUTFAK & KAHVE</div>
        <div class="boardroom-zone">🤝 OTONOM ZİRVE</div>

        <!-- Saksılar -->
        <div class="plant-pot" style="left: 235px; top: 145px;" id="plant-1">
            <span class="plant-status" id="plant-status-1">🌿 %100</span>🌱
        </div>
        <div class="plant-pot" style="left: 740px; top: 145px;" id="plant-2">
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

    <!-- Kontrol Paneli -->
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
            <span>⚡ AGENTSPACE 2D OPERATIONS TERMINAL</span>
            <span style="color: #4ade80;">● TOP-DOWN MAP ACTIVE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Gönderdiğin örnek görseldeki gibi üstten görünüm (top-down) oyun haritası mimarisi yüklendi.</div>
        </div>
    </div>

    <!-- RPG Kartı -->
    <div id="agent-modal">
        <h3 id="modal-title" style="color: #ef4444; margin-top: 0;"></h3>
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
            document.getElementById('modal-status').innerText = "Durum: Kendi ofis odasında görevde.";
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
                if(data.action_type === 'kitchen') appendLog(`> [OTONOM]: ${agentName} koridordan mutfağa yürüdü.`);
                if(data.action_type === 'boardroom') appendLog(`> [OTONOM]: ${agentName} toplantı salonuna geçti.`);
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

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    agent_list = []
    for name, data in employees.items():
        if random.random() < 0.2:
            # Hedefler: Odası, Ortadaki Koridor, Mutfak veya Toplantı Odası
            destinations = [
                (data["home_x"], data["home_y"]),
                (random.randint(810, 950), random.randint(30, 160)),  # Mutfak
                (random.randint(810, 950), random.randint(270, 400)) # Toplantı Odası
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest
            if dest[0] > 750:
                data["state"] = "☕ Molada" if dest[1] < 220 else "🤝 Toplantıda"
            else:
                data["state"] = "Masada"

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
