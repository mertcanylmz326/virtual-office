import os
import time
import threading
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
                water_status TEXT DEFAULT 'İyi',
                last_watered_by TEXT
            );
        """)
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Ana Salon Çiçeği', 80) ON CONFLICT (id) DO NOTHING;")
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
    <title>E-Trade Pro - Living Autonomous HQ</title>
    <style>
        body { 
            background-color: #030712; 
            color: #fff; 
            font-family: 'Courier New', Courier, monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow-x: hidden; 
        }
        #game-topbar {
            background: #0f172a;
            border-bottom: 3px solid #1e293b;
            padding: 8px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 11px;
        }
        .top-btn { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 4px 10px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .top-btn:hover { border-color: #38bdf8; }

        #office-floor { 
            position: relative; 
            width: 980px; 
            height: 500px; 
            margin: 10px auto; 
            background-color: #1a120b;
            background-image: 
                linear-gradient(90deg, rgba(255,255,255,0.03) 2px, transparent 2px),
                linear-gradient(rgba(0,0,0,0.3) 2px, transparent 2px);
            background-size: 50px 50px;
            border: 6px solid #1e293b; 
            border-radius: 10px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.95); 
            overflow: hidden;
        }

        /* Odalar ve Alanlar */
        .room {
            position: absolute;
            border: 2px solid #475569;
            background: rgba(30, 41, 59, 0.65);
            border-radius: 6px;
            width: 270px;
            height: 115px;
        }
        .room-label { position: absolute; font-size: 7px; color: #38bdf8; top: 3px; left: 6px; font-weight: bold; }
        
        /* Mutfak ve Toplantı Odası */
        .kitchen-area {
            position: absolute; left: 810px; top: 15px; width: 155px; height: 220px;
            border: 3px dashed #d97706; background: rgba(120, 53, 15, 0.2); border-radius: 6px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 9px; color: #fde68a;
        }
        .boardroom-area {
            position: absolute; left: 810px; top: 250px; width: 155px; height: 230px;
            border: 3px dashed #8b5cf6; background: rgba(109, 40, 217, 0.2); border-radius: 6px;
            display: flex; flex-direction: column; align-items: center; justify-content: center; font-size: 9px; color: #e9d5ff;
        }

        /* Saksılar & Çiçekler */
        .plant-pot {
            position: absolute; width: 30px; height: 30px; background: #78350f; border: 2px solid #451a03;
            border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 14px; z-index: 10;
        }
        .plant-status { position: absolute; top: -12px; font-size: 6px; background: #000; padding: 1px 3px; border-radius: 3px; white-space: nowrap; }

        /* Ayak İzleri Efekti */
        .footprint {
            position: absolute; width: 6px; height: 6px; background: rgba(255, 255, 255, 0.3);
            border-radius: 50%; pointer-events: none; z-index: 15; animation: fadeOut 2s forwards;
        }
        @keyframes fadeOut { 0% { opacity: 0.6; } 100% { opacity: 0; transform: scale(1.5); } }

        /* Ajan Spritelaarı */
        .agent { 
            position: absolute; width: 40px; height: 50px; cursor: pointer; 
            display: flex; flex-direction: column; align-items: center; justify-content: center; 
            transition: transform 0.2s; z-index: 40;
        }
        .robot-sprite {
            width: 26px; height: 26px; background-color: #18181b; border: 2px solid; border-radius: 6px;
            display: flex; align-items: center; justify-content: center; font-size: 12px; box-shadow: 0 3px 6px rgba(0,0,0,0.8);
        }
        .agent-name { font-size: 6px; font-weight: bold; background: rgba(15, 23, 42, 0.9); padding: 1px 2px; border-radius: 2px; margin-top: 1px; white-space: nowrap; }
        .speech-bubble {
            position: absolute; top: -20px; background: #f8fafc; color: #0f172a; font-size: 6px; font-weight: bold;
            padding: 2px 4px; border-radius: 3px; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.5); pointer-events: none;
        }

        .action-bar { margin: 10px auto; width: 970px; display: flex; justify-content: space-between; gap: 10px; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 10px; border-radius: 6px; display: flex; gap: 10px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 6px 10px; border-radius: 4px; font-family: monospace; font-size: 11px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 6px 14px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 20px auto; width: 970px; background: #020617; border: 2px solid #334155; border-radius: 6px; text-align: left; overflow: hidden;
        }
        .terminal-header { background: #0f172a; padding: 6px 12px; font-size: 10px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 8px; height: 90px; overflow-y: auto; font-size: 10px; color: #4ade80; line-height: 1.3; }
        .log-line { margin-bottom: 3px; border-bottom: 1px dashed rgba(255,255,255,0.05); }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO - LIVING SIMULATION HQ</div>
        <div>
            <span class="top-btn" onclick="checkPlantStatus()">🌿 ÇİÇEK DURUMU</span>
            <span class="top-btn" onclick="triggerWatering()">💧 ÇİÇEKLERİ SULA</span>
        </div>
    </div>

    <!-- Canlı Ofis Haritası -->
    <div id="office-floor" id="floor-container">
        <!-- 9 Oda -->
        <div class="room" style="left: 15px; top: 15px;"><div class="room-label">MARCO (DESTEK)</div></div>
        <div class="room" style="left: 300px; top: 15px;"><div class="room-label">TALİSCA (OPERASYON)</div></div>
        <div class="room" style="left: 585px; top: 15px;"><div class="room-label">BROWN (YAZILIM)</div></div>
        
        <div class="room" style="left: 15px; top: 145px;"><div class="room-label">KANTE (PAZARLAMA)</div></div>
        <div class="room" style="left: 300px; top: 145px;"><div class="room-label">İRFAN (FİNANS)</div></div>
        <div class="room" style="left: 585px; top: 145px;"><div class="room-label">İSMAİL (İK)</div></div>

        <div class="room" style="left: 15px; top: 275px;"><div class="room-label">ALEX (HUKUK)</div></div>
        <div class="room" style="left: 300px; top: 275px;"><div class="room-label">SKRİNAR (SİBER)</div></div>
        <div class="room" style="left: 585px; top: 275px;"><div class="room-label">KEREM (BAŞARI)</div></div>

        <!-- Mutfak ve Toplantı Alanları -->
        <div class="kitchen-area">☕ MUTFAK & MOLA</div>
        <div class="boardroom-area">🤝 TOPLANTI ODASI</div>

        <!-- Saksılar (Çiçekler) -->
        <div class="plant-pot" style="left: 275px; top: 110px;" id="plant-1">
            <span class="plant-status" id="plant-status-1">🌿 %80</span>🌱
        </div>
        <div class="plant-pot" style="left: 770px; top: 110px;" id="plant-2">
            <span class="plant-status" id="plant-status-2">🌿 %80</span>🌵
        </div>

        <!-- Ajanlar -->
        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.x }}px; top: {{ data.y }}px;" onclick="selectAgent('{{ name }}')">
            <div class="speech-bubble" id="bubble-{{ name }}">{{ data.state }}</div>
            <div class="robot-sprite" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name, data in employees.items() %}
                <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Emir ver veya sohbet et..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ LIVING SIMULATION TERMINAL</span>
            <span style="color: #34d399;">● ACTIVE MOVEMENT</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Yaşayan ofis simülasyonu başlatıldı. Ajanlar koridorda geziniyor ve saksılar takip ediliyor.</div>
        </div>
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
            appendLog(`> [SEÇİM]: ${name} seçildi.`);
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        // Ajanların Hareket Etmesi ve Ayak İzi Bırakması (Animate Loop)
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

                    // Eğer hareket ediyorsa ayak izi bırak
                    if (Math.abs(oldX - agent.x) > 2 || Math.abs(oldY - agent.y) > 2) {
                        createFootprint(agent.x + 20, agent.y + 45);
                    }
                });
            });
        }, 2000);

        function createFootprint(x, y) {
            const floor = document.getElementById('office-floor');
            const fp = document.createElement('div');
            fp.className = 'footprint';
            fp.style.left = x + 'px';
            fp.style.top = y + 'px';
            floor.appendChild(fp);
            setTimeout(() => fp.remove(), 2000); // 2 saniye sonra silinir
        }

        function sendDirectMessage() {
            const agentName = document.getElementById('agent-select').value;
            const messageInput = document.getElementById('ceo-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendLog(`> [KOMUT -> ${agentName}]: "${messageText}"`);
            messageInput.value = "";

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: agentName, message: messageText })
            })
            .then(res => res.json())
            .then(data => {
                appendLog(`> [<b>${agentName}</b>]: "${data.status}"`);
                if(data.action_type === 'kitchen') appendLog(`> [ETKİNLİK]: ${agentName} mutfağa kahve molasına gitti.`);
                if(data.action_type === 'boardroom') appendLog(`> [ETKİNLİK]: ${agentName} toplantı odasına geçti.`);
            });
        }

        function checkPlantStatus() {
            fetch('/api/plants').then(res => res.json()).then(data => {
                appendLog(`> [SİSTEM BİTKİ DURUMU]: ${data.status_text}`);
            });
        }

        function triggerWatering() {
            fetch('/api/water-plants', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [SULAMA]: Çiçekler sulandı! Sağlık seviyesi %100 oldu.`);
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

# Otonom Konum Güncelleyici (Ajanlar Koridorda / Mutfakta / Odada Gezinir)
import random

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    agent_list = []
    for name, data in employees.items():
        # Rastgele otonom hareket kararı (Mutfak: x=850, y=100 | Toplantı: x=850, y=300 | Oda: Kendi evi)
        if random.random() < 0.25: # %25 ihtimalle yer değiştirirler
            destinations = [
                (data["home_x"] if "home_x" in data else data["x"], data["home_y"] if "home_y" in data else data["y"]), # Kendi odası
                (850, random.randint(50, 180)), # Mutfak
                (850, random.randint(280, 400)) # Toplantı Odası
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest
            if dest[0] > 800:
                data["state"] = "Mutfakta/Molada" if dest[1] < 200 else "Toplantıda"
            else:
                data["state"] = "Masasında"

        # Yavaşça hedefe doğru ilerle (smooth movement)
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
        agent["target_x"], agent["target_y"] = 850, 300
        agent["state"] = "Toplantıda"
        action_type = "boardroom"

    try:
        system_prompt = f"Sen E-Trade Pro şirketinde {agent['role']} olarak çalışan {agent_name} adında bir uzmansın. Patronun Mertcan sana yazdı: '{user_message}'. Kısa, net ve profesyonel yanıt ver."
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=150, temperature=0.7
        )
        reply = completion.choices[0].message.content.strip('"').strip()
    except:
        reply = "Emredersiniz patron, çalışıyorum."

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
        cur.execute("UPDATE office_plants SET health_level = 100, water_status = 'Çok İyi' WHERE id=1;")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"success": True})
    except:
        return jsonify({"success": False})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
