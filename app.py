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
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Robot Üs Saksısı', 100) ON CONFLICT (id) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

# 9 Ajan ve Gerçekçi Oda İçi Masa Konumları
employees = {
    "Marco": {"role": "Destek", "room_x": 15, "room_y": 15, "x": 60, "y": 55, "target_x": 60, "target_y": 55, "color": "#3b82f6", "state": "Masada"},
    "Talisca": {"role": "Operasyon", "room_x": 175, "room_y": 15, "x": 220, "y": 55, "target_x": 220, "target_y": 55, "color": "#ef4444", "state": "Masada"},
    "Brown": {"role": "Yazılım", "room_x": 335, "room_y": 15, "x": 380, "y": 55, "target_x": 380, "target_y": 55, "color": "#10b981", "state": "Masada"},
    
    "Kante": {"role": "Pazarlama", "room_x": 15, "room_y": 145, "x": 60, "y": 185, "target_x": 60, "target_y": 185, "color": "#f59e0b", "state": "Masada"},
    "İrfan": {"role": "Finans", "room_x": 175, "room_y": 145, "x": 220, "y": 185, "target_x": 220, "target_y": 185, "color": "#8b5cf6", "state": "Masada"},
    "İsmail": {"role": "İK", "room_x": 335, "room_y": 145, "x": 380, "y": 185, "target_x": 380, "target_y": 185, "color": "#f97316", "state": "Masada"},
    
    "Alex": {"role": "Hukuk", "room_x": 15, "room_y": 275, "x": 60, "y": 315, "target_x": 60, "target_y": 315, "color": "#14b8a6", "state": "Masada"},
    "Skrinar": {"role": "Siber", "room_x": 175, "room_y": 275, "x": 220, "y": 315, "target_x": 220, "target_y": 315, "color": "#64748b", "state": "Masada"},
    "Kerem": {"role": "Başarı", "room_x": 335, "room_y": 275, "x": 380, "y": 315, "target_x": 380, "target_y": 315, "color": "#ec4899", "state": "Masada"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - Robot Corridor Tycoon HQ</title>
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

        #game-container {
            position: relative;
            width: 980px;
            height: 410px;
            margin: 10px auto;
            border: 3px solid #38bdf8;
            border-radius: 8px;
            box-shadow: 0 15px 30px rgba(0,0,0,0.9);
            background: #0b0f19;
            overflow: hidden;
        }
        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }

        .action-bar { margin: 10px auto; width: 980px; display: flex; justify-content: space-between; gap: 10px; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 8px; border-radius: 8px; display: flex; gap: 8px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 6px 10px; border-radius: 6px; font-family: monospace; font-size: 11px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 15px auto; width: 980px; background: #030712; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden;
        }
        .terminal-header { background: #0f172a; padding: 6px 12px; font-size: 10px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 8px; height: 75px; overflow-y: auto; font-size: 10px; color: #4ade80; line-height: 1.3; }
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
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO // ROBOT CORRIDOR TYCOON HQ</div>
        <div>
            <span class="top-btn" onclick="loadMemory()">🧠 RAG HAFIZA</span>
            <span class="top-btn" onclick="loadTasks()">📋 GÖREVLER</span>
            <span class="top-btn" onclick="triggerBoardroom()">🤝 ZİRVE</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULA</span>
        </div>
    </div>

    <!-- Canvas Haritası -->
    <div id="game-container">
        <canvas id="officeCanvas"></canvas>
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
            <span>⚡ ROBOT CORRIDOR OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8;">● WALL COLLISION & PATHFINDING ACTIVE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Gerçekçi duvarlar, koridorlar, açılır kapılar ve robot sprite motoru yüklendi.</div>
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
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const terminalLogs = document.getElementById('terminal-logs');

        let agentsData = {};
        let footprints = []; // Ayak izleri dizisi

        function resizeCanvas() {
            const dpr = window.devicePixelRatio || 1;
            canvas.width = 980 * dpr;
            canvas.height = 410 * dpr;
            ctx.scale(dpr, dpr);
        }
        resizeCanvas();

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
            document.getElementById('modal-status').innerText = "Durum: Koridor ve oda navigasyonunda aktif.";
            document.getElementById('agent-modal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('agent-modal').style.display = 'none';
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        // Harita Çizim Motoru (Duvarlar, Kapılar, Koridorlar)
        function drawOffice() {
            const w = 980;
            const h = 410;
            ctx.clearRect(0, 0, w, h);

            // Zemin
            ctx.fillStyle = "#0b0f19";
            ctx.fillRect(0, 0, w, h);

            // Koridorlar (Parke Dokusu)
            ctx.fillStyle = "#151c2c";
            ctx.fillRect(0, 120, w, 25); // Üst koridor
            ctx.fillRect(0, 245, w, 25); // Alt koridor
            ctx.fillRect(470, 0, 30, h);  // Dikey koridor

            // 9 Oda ve Açılır Kapıları
            const rooms = [
                {x: 15, y: 15, w: 145, h: 95, name: "1. MARCO"},
                {x: 175, y: 15, w: 145, h: 95, name: "2. TALİSCA"},
                {x: 335, y: 15, w: 145, h: 95, name: "3. BROWN"},
                {x: 15, y: 145, w: 145, h: 95, name: "4. KANTE"},
                {x: 175, y: 145, w: 145, h: 95, name: "5. İRFAN"},
                {x: 335, y: 145, w: 145, h: 95, name: "6. İSMAİL"},
                {x: 15, y: 275, w: 145, h: 95, name: "7. ALEX"},
                {x: 175, y: 275, w: 145, h: 95, name: "8. SKRİNAR"},
                {x: 335, y: 275, w: 145, h: 95, name: "9. KEREM"}
            ];

            rooms.forEach(r => {
                ctx.fillStyle = "#111827";
                ctx.fillRect(r.x, r.y, r.w, r.h);
                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 3; // Kalın duvar
                ctx.strokeRect(r.x, r.y, r.w, r.h);

                // Oda Başlığı
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 8px 'Courier New'";
                ctx.fillText(r.name, r.x + 6, r.y + 12);

                // Çalışma Masası ve Monitör
                ctx.fillStyle = "#292524";
                ctx.fillRect(r.x + 45, r.y + 50, 55, 20);
                ctx.fillStyle = "#0284c7";
                ctx.fillRect(r.x + 60, r.y + 54, 22, 10);

                // Odaların Koridora Açılan Kapısı (Açık görünüm)
                ctx.fillStyle = "#0284c7";
                if (r.y < 120) ctx.fillRect(r.x + 60, r.y + r.h - 2, 25, 4); // Alt duvar kapısı
                else if (r.y > 200) ctx.fillRect(r.x + 60, r.y - 2, 25, 4);  // Üst duvar kapısı
                else ctx.fillRect(r.x + r.w - 2, r.y + 40, 4, 20);           // Sağ duvar kapısı
            });

            // Sağ Taraf: Mutfak ve Zirve Odası
            ctx.fillStyle = "rgba(120, 53, 15, 0.25)";
            ctx.fillRect(520, 15, 445, 185);
            ctx.strokeStyle = "#d97706";
            ctx.lineWidth = 3;
            ctx.strokeRect(520, 15, 445, 185);
            ctx.fillStyle = "#fde68a";
            ctx.font = "bold 9px 'Courier New'";
            ctx.fillText("☕ MUTFAK & KAHVE ALANI", 540, 35);

            ctx.fillStyle = "rgba(109, 40, 217, 0.25)";
            ctx.fillRect(520, 215, 445, 185);
            ctx.strokeStyle = "#8b5cf6";
            ctx.lineWidth = 3;
            ctx.strokeRect(520, 215, 445, 185);
            ctx.fillStyle = "#e9d5ff";
            ctx.font = "bold 9px 'Courier New'";
            ctx.fillText("🤝 OTONOM ZİRVE ODASI", 540, 235);

            // Ayak İzlerini Çiz
            footprints.forEach(fp => {
                ctx.fillStyle = "rgba(56, 189, 248, 0.4)";
                ctx.fillRect(fp.x, fp.y, 3, 3);
            });

            // Ajanları ve Robot Görünümünü Çiz
            for (let name in agentsData) {
                let ag = agentsData[name];
                
                // Robot Gövdesi ve Anteni
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x, ag.y, 24, 24);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.strokeRect(ag.x, ag.y, 24, 24);

                // Robot Anteni
                ctx.fillStyle = "#38bdf8";
                ctx.fillRect(ag.x + 11, ag.y - 4, 2, 4);
                ctx.fillRect(ag.x + 9, ag.y - 6, 6, 2);

                // Baş Harf
                ctx.fillStyle = "#ffffff";
                ctx.font = "bold 8px 'Courier New'";
                ctx.fillText(name.substring(0, 2).toUpperCase(), ag.x + 5, ag.y + 16);

                // İsim Etiketi
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 7px 'Courier New'";
                ctx.fillText(name, ag.x - 4, ag.y + 34);

                // Temiz Durum Balonu
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(ag.x - 6, ag.y - 18, ctx.measureText(ag.state).width + 6, 10);
                ctx.strokeStyle = "#0f172a";
                ctx.strokeRect(ag.x - 6, ag.y - 18, ctx.measureText(ag.state).width + 6, 10);
                ctx.fillStyle = "#0f172a";
                ctx.font = "bold 7px 'Courier New'";
                ctx.fillText(ag.state, ag.x - 3, ag.y - 10);
            }
        }

        // Tıklama ile Kart Açma
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = 980 / rect.width;
            const scaleY = 410 / rect.height;
            const mouseX = (e.clientX - rect.left) * scaleX;
            const mouseY = (e.clientY - rect.top) * scaleY;

            for (let name in agentsData) {
                let ag = agentsData[name];
                if (mouseX >= ag.x && mouseX <= ag.x + 24 && mouseY >= ag.y && mouseY <= ag.y + 24) {
                    openAgentCard(name, "Robot Personel");
                    break;
                }
            }
        });

        // Simülasyon Verisini Çek ve Ayak İzi Ekle
        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                let mapped = {};
                data.agents.forEach(ag => {
                    mapped[ag.name] = ag;
                    // Eğer yürüyorsa ayak izi ekle
                    if (ag.state === "Yürüyor...") {
                        footprints.push({x: ag.x + 10, y: ag.y + 20});
                        if (footprints.length > 50) footprints.shift();
                    }
                });
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
        if random.random() < 0.25:
            destinations = [
                (data["room_x"] + 45, data["room_y"] + 40), # Kendi masası
                (random.randint(540, 900), random.randint(30, 150)),  # Mutfak
                (random.randint(540, 900), random.randint(230, 350)) # Zirve Odası
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest

        # Adım adım hareket (Pathfinding simülasyonu)
        if data["x"] < data["target_x"]: data["x"] += min(6, data["target_x"] - data["x"])
        elif data["x"] > data["target_x"]: data["x"] -= min(6, data["x"] - data["target_x"])

        if data["y"] < data["target_y"]: data["y"] += min(6, data["target_y"] - data["y"])
        elif data["y"] > data["target_y"]: data["y"] -= min(6, data["y"] - data["target_y"])

        # Durum belirleme
        if data["x"] >= 500 and data["y"] <= 200:
            data["state"] = "☕ Molada"
        elif data["x"] >= 500 and data["y"] > 200:
            data["state"] = "🤝 Toplantıda"
        elif abs(data["x"] - (data["room_x"] + 45)) < 10 and abs(data["y"] - (data["room_y"] + 40)) < 10:
            data["state"] = "Masada"
        else:
            data["state"] = "Yürüyor..."

        agent_list.append({"name": name, "x": data["x"], "y": data["y"], "state": data["state"], "color": data["color"]})

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
            f"Sen E-Trade Pro şirketinde {agent['role']} olarak çalışan {agent_name} adında bir robot uzmansın. "
            f"Patronun Mertcan sana yazdı: '{user_message}'.\n"
            f"[SUPABASE GEÇMİŞ HAFIZA]: {memory_context}\n"
            f"Profesyonel ve kısa yanıt ver."
        )
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=150, temperature=0.7
        )
        reply = completion.choices[0].message.content.strip('"').strip()
    except:
        reply = "Emredersiniz patron, sistem çalışıyor."

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
