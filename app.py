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

# 9 Ajanın tam oda koordinatları (Ev konumları)
employees = {
    "Marco": {"role": "Destek", "home_x": 75, "home_y": 70, "x": 75, "y": 70, "target_x": 75, "target_y": 70, "color": "#3b82f6", "state": "Masada"},
    "Talisca": {"role": "Operasyon", "home_x": 285, "home_y": 70, "x": 285, "y": 70, "target_x": 285, "target_y": 70, "color": "#ef4444", "state": "Masada"},
    "Brown": {"role": "Yazılım", "home_x": 495, "home_y": 70, "x": 495, "y": 70, "target_x": 495, "target_y": 70, "color": "#10b981", "state": "Masada"},
    
    "Kante": {"role": "Pazarlama", "home_x": 75, "home_y": 200, "x": 75, "y": 200, "target_x": 75, "target_y": 200, "color": "#f59e0b", "state": "Masada"},
    "İrfan": {"role": "Finans", "home_x": 285, "home_y": 200, "x": 285, "y": 200, "target_x": 285, "target_y": 200, "color": "#8b5cf6", "state": "Masada"},
    "İsmail": {"role": "İK", "home_x": 495, "home_y": 200, "x": 495, "y": 200, "target_x": 495, "target_y": 200, "color": "#f97316", "state": "Masada"},
    
    "Alex": {"role": "Hukuk", "home_x": 75, "home_y": 330, "x": 75, "y": 330, "target_x": 75, "target_y": 330, "color": "#14b8a6", "state": "Masada"},
    "Skrinar": {"role": "Siber", "home_x": 285, "home_y": 330, "x": 285, "y": 330, "target_x": 285, "target_y": 330, "color": "#64748b", "state": "Masada"},
    "Kerem": {"role": "Başarı", "home_x": 495, "home_y": 330, "x": 495, "y": 330, "target_x": 495, "target_y": 330, "color": "#ec4899", "state": "Masada"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - AgentSpace 2D HQ</title>
    <style>
        body { 
            background-color: #07090e; 
            color: #f8fafc; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow-x: hidden; 
        }
        #game-topbar {
            background: #0f172a;
            border-bottom: 2px solid #ef4444;
            padding: 10px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 12px;
        }
        .top-btn { 
            background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 6px 14px; 
            border-radius: 6px; font-weight: bold; cursor: pointer; 
        }
        .top-btn:hover { border-color: #ef4444; color: #fff; }

        /* Oyun Sahnesi (Top-Down 2D Grid) */
        #office-floor { 
            position: relative; 
            width: 1020px; 
            height: 480px; 
            margin: 15px auto; 
            background-color: #111827;
            background-image: radial-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px);
            background-size: 24px 24px;
            border: 4px solid #374151; 
            border-radius: 10px; 
            box-shadow: 0 20px 40px rgba(0,0,0,0.9); 
            overflow: hidden;
        }

        /* Düzenli 9 Oda */
        .office-room {
            position: absolute;
            background: #1e293b;
            border: 2px solid #475569;
            border-radius: 6px;
            width: 195px;
            height: 115px;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
        }
        .room-title {
            position: absolute; top: 4px; left: 6px; font-size: 7px; color: #38bdf8; font-weight: bold;
            background: #0f172a; padding: 1px 5px; border-radius: 3px; border: 1px solid #334155;
        }
        .office-desk {
            position: absolute; bottom: 12px; left: 47px; width: 100px; height: 32px;
            background: #292524; border: 2px solid #57534e; border-radius: 4px;
            display: flex; align-items: center; justify-content: center;
        }
        .pc-screen {
            width: 22px; height: 12px; background: #0284c7; border: 1px solid #38bdf8; border-radius: 2px;
            box-shadow: 0 0 6px #38bdf8;
        }

        /* Sağ Taraf: Mutfak ve Zirve Odası */
        .kitchen-zone {
            position: absolute; left: 795px; top: 15px; width: 210px; height: 215px;
            border: 3px solid #d97706; background: rgba(120, 53, 15, 0.25); border-radius: 8px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #fde68a;
            font-weight: bold;
        }
        .boardroom-zone {
            position: absolute; left: 795px; top: 250px; width: 210px; height: 215px;
            border: 3px solid #8b5cf6; background: rgba(109, 40, 217, 0.25); border-radius: 8px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 10px; color: #e9d5ff;
            font-weight: bold;
        }

        /* Saksılar */
        .plant-pot {
            position: absolute; width: 30px; height: 30px; background: #78350f; border: 2px solid #b45309;
            border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 14px; z-index: 10;
        }
        .plant-status { position: absolute; top: -13px; font-size: 6px; background: #000; color: #4ade80; padding: 1px 3px; border-radius: 3px; white-space: nowrap; border: 1px solid #4ade80; }

        /* Ayak İzleri */
        .footprint {
            position: absolute; width: 4px; height: 4px; background: rgba(56, 189, 248, 0.6);
            border-radius: 50%; pointer-events: none; z-index: 15; animation: fadeOut 1s forwards;
        }
        @keyframes fadeOut { 0% { opacity: 0.8; } 100% { opacity: 0; transform: scale(1.5); } }

        /* Ajan Sprite (Pixel Oyunu Hissiyatı) */
        .agent { 
            position: absolute; width: 45px; height: 55px; cursor: pointer; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            transition: transform 0.2s; z-index: 40;
        }
        .agent-avatar {
            width: 28px; height: 28px; background-color: #0f172a; border: 2px solid; border-radius: 6px;
            display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;
            box-shadow: 0 4px 8px rgba(0,0,0,0.9);
        }
        .agent-name { font-size: 6px; font-weight: bold; background: rgba(15, 23, 42, 0.95); padding: 1px 3px; border-radius: 2px; margin-top: 1px; white-space: nowrap; border: 1px solid #334155; }
        .speech-bubble {
            position: absolute; top: -20px; background: #f8fafc; color: #0f172a; font-size: 6px; font-weight: bold;
            padding: 2px 5px; border-radius: 3px; white-space: nowrap; box-shadow: 0 0 6px rgba(255,255,255,0.5); pointer-events: none;
        }

        .action-bar { margin: 15px auto; width: 1020px; display: flex; justify-content: space-between; gap: 10px; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 10px; border-radius: 8px; display: flex; gap: 10px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 8px 12px; border-radius: 6px; font-family: monospace; font-size: 12px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #ef4444; color: #fff; border: none; padding: 8px 18px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #dc2626; }

        #activity-terminal {
            margin: 0 auto 20px auto; width: 1020px; background: #07090e; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden;
        }
        .terminal-header { background: #0f172a; padding: 8px 15px; font-size: 11px; color: #ef4444; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 10px; height: 90px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; }
        .log-line { margin-bottom: 4px; border-bottom: 1px dashed rgba(255,255,255,0.05); }

        #agent-modal {
            display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #0f172a; border: 2px solid #ef4444; padding: 20px; border-radius: 10px; z-index: 1000;
            box-shadow: 0 0 30px rgba(239, 68, 68, 0.4); width: 280px; text-align: left;
        }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #ef4444;">🏢 E-TRADE PRO // 9-AGENT STRUCTURED HQ</div>
        <div>
            <span class="top-btn" onclick="checkPlantStatus()">🌿 BİTKİLER</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULA</span>
        </div>
    </div>

    <!-- Kusursuz 9 Odalı Harita -->
    <div id="office-floor">
        <!-- Row 1 (Üst Sıra) -->
        <div class="office-room" style="left: 15px; top: 15px;"><div class="room-title">1. MARCO (DESTEK)</div><div class="office-desk"><div class="pc-screen"></div></div></div>
        <div class="office-room" style="left: 225px; top: 15px;"><div class="room-title">2. TALİSCA (OPERASYON)</div><div class="office-desk"><div class="pc-screen"></div></div></div>
        <div class="office-room" style="left: 435px; top: 15px;"><div class="room-title">3. BROWN (YAZILIM)</div><div class="office-desk"><div class="pc-screen"></div></div></div>

        <!-- Row 2 (Orta Sıra) -->
        <div class="office-room" style="left: 15px; top: 145px;"><div class="room-title">4. KANTE (PAZARLAMA)</div><div class="office-desk"><div class="pc-screen"></div></div></div>
        <div class="office-room" style="left: 225px; top: 145px;"><div class="room-title">5. İRFAN (FİNANS)</div><div class="office-desk"><div class="pc-screen"></div></div></div>
        <div class="office-room" style="left: 435px; top: 145px;"><div class="room-title">6. İSMAİL (İK)</div><div class="office-desk"><div class="pc-screen"></div></div></div>

        <!-- Row 3 (Alt Sıra) -->
        <div class="office-room" style="left: 15px; top: 275px;"><div class="room-title">7. ALEX (HUKUK)</div><div class="office-desk"><div class="pc-screen"></div></div></div>
        <div class="office-room" style="left: 225px; top: 275px;"><div class="room-title">8. SKRİNAR (SİBER)</div><div class="office-desk"><div class="pc-screen"></div></div></div>
        <div class="office-room" style="left: 435px; top: 275px;"><div class="room-title">9. KEREM (BAŞARI)</div><div class="office-desk"><div class="pc-screen"></div></div></div>

        <!-- Sağ Taraf: Mutfak ve Zirve Odası -->
        <div class="kitchen-zone">☕ MUTFAK & KAHVE</div>
        <div class="boardroom-zone">🤝 OTONOM ZİRVE</div>

        <!-- Saksılar -->
        <div class="plant-pot" style="left: 685px; top: 90px;" id="plant-1">
            <span class="plant-status" id="plant-status-1">🌿 %100</span>🌱
        </div>
        <div class="plant-pot" style="left: 685px; top: 320px;" id="plant-2">
            <span class="plant-status" id="plant-status-2">🌿 %100</span>🌵
        </div>

        <!-- 9 Ajan Karakteri -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" onclick="openAgentCard('{{ name }}', '{{ data.role }}')">
            <div class="speech-bubble" id="bubble-{{ name }}">{{ data.state }}</div>
            <div class="agent-avatar" style="border-color: {{ data.color }}; color: {{ data.color }};">{{ name[:2].upper() }}</div>
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
            <input type="text" id="ceo-message" placeholder="Stratejik emir ver..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ 9-AGENT STRUCTURED OPERATIONS TERMINAL</span>
            <span style="color: #4ade80;">● STABLE GRID ACTIVE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Tüm 9 ajanın kendine ait özel odası ve kararlı koordinat matrisi yüklendi.</div>
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
            document.getElementById('modal-title'].innerText = "👤 " + name;
            document.getElementById('modal-role').innerText = "Departman: " + role;
            document.getElementById('modal-status').innerText = "Durum: Kendi odasında aktif görevde.";
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
            destinations = [
                (data["home_x"], data["home_y"]),
                (random.randint(810, 970), random.randint(30, 160)),   # Mutfak içi
                (random.randint(810, 970), random.randint(270, 400))  # Toplantı odası içi
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest

        if data["x"] < data["target_x"]: data["x"] += min(12, data["target_x"] - data["x"])
        elif data["x"] > data["target_x"]: data["x"] -= min(12, data["x"] - data["target_x"])

        if data["y"] < data["target_y"]: data["y"] += min(12, data["target_y"] - data["y"])
        elif data["y"] > data["target_y"]: data["y"] -= min(12, data["y"] - data["target_y"])

        # Kesin konum bazlı durum etiketleme
        if data["x"] >= 780 and data["y"] <= 230:
            data["state"] = "☕ Molada"
        elif data["x"] >= 780 and data["y"] > 230:
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

    action_type = "chat"
    if "kahve" in user_message.lower() or "mola" in user_message.lower():
        agent["target_x"], agent["target_y"] = 850, 100
        agent["state"] = "☕ Molada"
        action_type = "kitchen"
    elif "toplantı" in user_message.lower():
        agent["target_x"], agent["target_y"] = 850, 320
        agent["state"] = "🤝 Toplantıda"
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
