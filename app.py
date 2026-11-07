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
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Kusursuz Üs Saksısı', 100) ON CONFLICT (id) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

# Ajanlar (Odaları, kapı çıkış noktaları ve iç koordinatları ile)
employees = {
    "Marco": {"role": "Destek", "room_x": 15, "room_y": 15, "x": 60, "y": 65, "target_x": 60, "target_y": 65, "color": "#3b82f6", "state": "Masada", "speech": "Hazır"},
    "Talisca": {"role": "Operasyon", "room_x": 195, "room_y": 15, "x": 240, "y": 65, "target_x": 240, "target_y": 65, "color": "#ef4444", "state": "Masada", "speech": "Hazır"},
    "Brown": {"role": "Yazılım", "room_x": 375, "room_y": 15, "x": 420, "y": 65, "target_x": 420, "target_y": 65, "color": "#10b981", "state": "Masada", "speech": "Hazır"},
    
    "Kante": {"role": "Pazarlama", "room_x": 15, "room_y": 155, "x": 60, "y": 205, "target_x": 60, "target_y": 205, "color": "#f59e0b", "state": "Masada", "speech": "Hazır"},
    "İrfan": {"role": "Finans", "room_x": 195, "room_y": 155, "x": 240, "y": 205, "target_x": 240, "target_y": 205, "color": "#8b5cf6", "state": "Masada", "speech": "Hazır"},
    "İsmail": {"role": "İK", "room_x": 375, "room_y": 155, "x": 420, "y": 205, "target_x": 420, "target_y": 205, "color": "#f97316", "state": "Masada", "speech": "Hazır"},
    
    "Alex": {"role": "Hukuk", "room_x": 15, "room_y": 295, "x": 60, "y": 345, "target_x": 60, "target_y": 345, "color": "#14b8a6", "state": "Masada", "speech": "Hazır"},
    "Skrinar": {"role": "Siber", "room_x": 195, "room_y": 295, "x": 240, "y": 345, "target_x": 240, "target_y": 345, "color": "#64748b", "state": "Masada", "speech": "Hazır"},
    "Kerem": {"role": "Başarı", "room_x": 375, "room_y": 295, "x": 420, "y": 345, "target_x": 420, "target_y": 345, "color": "#ec4899", "state": "Masada", "speech": "Hazır"},
    "Mutfak_Chef": {"role": "Mutfak Personeli", "room_x": 580, "room_y": 15, "x": 630, "y": 70, "target_x": 630, "target_y": 70, "color": "#f43f5e", "state": "Kahve Hazırlıyor", "speech": "Kahveler taze!"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - Synchronized Tycoon HQ</title>
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
        canvas {
            display: block;
            width: 100%;
            height: auto;
        }

        .action-bar { margin: 10px auto; width: 1080px; max-width: 100%; display: flex; justify-content: space-between; gap: 10px; padding: 0 10px; box-sizing: border-box; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 8px; border-radius: 8px; display: flex; gap: 8px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 6px 10px; border-radius: 6px; font-family: monospace; font-size: 11px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 15px auto; width: 1080px; max-width: 100%; background: #030712; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden; box-sizing: border-box;
        }
        .terminal-header { background: #0f172a; padding: 6px 12px; font-size: 10px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; }
        .terminal-body { padding: 8px; height: 85px; overflow-y: auto; font-size: 10px; color: #4ade80; line-height: 1.3; }
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
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO // SYNCHRONIZED TYCOON HQ</div>
        <div>
            <span class="top-btn" onclick="loadMemory()">🧠 HAFIZA</span>
            <span class="top-btn" onclick="loadTasks()">📋 GÖREVLER</span>
            <span class="top-btn" onclick="triggerBoardroom()">🤝 ZİRVE</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULA</span>
        </div>
    </div>

    <!-- Canvas Haritası -->
    <div id="game-container">
        <canvas id="officeCanvas" width="1080" height="440"></canvas>
    </div>

    <!-- Komuta Paneli -->
    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name, data in employees.items() %}
                <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Stratejik emir ver veya personel işe al..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ WAYPOINT & SPEECH BUBBLE OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8;">● AI SYNCHRONIZATION ACTIVE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Kapı waypoint yönlendirmesi ve harita üstü konuşma balonları aktif edildi.</div>
        </div>
    </div>

    <!-- Karakter Kartı -->
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
        let footprints = [];
        let steamParticles = [];

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
            document.getElementById('modal-role').innerText = "Rol: " + role;
            document.getElementById('modal-status').innerText = "Durum: Görev ve toplantı senkronizasyonunda.";
            document.getElementById('agent-modal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('agent-modal').style.display = 'none';
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        function drawOffice() {
            const w = 1080;
            const h = 440;
            ctx.clearRect(0, 0, w, h);

            // Zemin - Parke
            ctx.fillStyle = "#1e1b18";
            ctx.fillRect(0, 0, w, h);
            
            ctx.strokeStyle = "#292524";
            ctx.lineWidth = 1;
            for (let i = 0; i < w; i += 30) {
                ctx.beginPath();
                ctx.moveTo(i, 0);
                ctx.lineTo(i, h);
                ctx.stroke();
            }

            // Ana Koridorlar
            ctx.fillStyle = "#292524";
            ctx.fillRect(0, 130, w, 35);
            ctx.fillRect(0, 270, w, 35);
            ctx.fillRect(530, 0, 35, h);

            // 9 Ofis Odası
            const rooms = [
                {x: 15, y: 15, w: 160, h: 105, name: "1. MARCO"},
                {x: 195, y: 15, w: 160, h: 105, name: "2. TALİSCA"},
                {x: 375, y: 15, w: 160, h: 105, name: "3. BROWN"},
                {x: 15, y: 155, w: 160, h: 105, name: "4. KANTE"},
                {x: 195, y: 155, w: 160, h: 105, name: "5. İRFAN"},
                {x: 375, y: 155, w: 160, h: 105, name: "6. İSMAİL"},
                {x: 15, y: 295, w: 160, h: 105, name: "7. ALEX"},
                {x: 195, y: 295, w: 160, h: 105, name: "8. SKRİNAR"},
                {x: 375, y: 295, w: 160, h: 105, name: "9. KEREM"}
            ];

            rooms.forEach(r => {
                ctx.fillStyle = "#111827";
                ctx.fillRect(r.x, r.y, r.w, r.h);
                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 4;
                ctx.strokeRect(r.x, r.y, r.w, r.h);

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 8px 'Courier New'";
                ctx.fillText(r.name, r.x + 8, r.y + 14);

                // Masa
                ctx.fillStyle = "#292524";
                ctx.fillRect(r.x + 50, r.y + 55, 60, 24);
                ctx.fillStyle = "#0284c7";
                ctx.fillRect(r.x + 68, r.y + 60, 24, 12);

                // Saksı 🌱
                ctx.fillStyle = "#78350f";
                ctx.fillRect(r.x + 15, r.y + 55, 16, 18);
                ctx.fillStyle = "#4ade80";
                ctx.font = "11px sans-serif";
                ctx.fillText("🌿", r.x + 13, r.y + 50);

                // Kapı Eşiği
                ctx.fillStyle = "#4ade80";
                if (r.y < 130) ctx.fillRect(r.x + 65, r.y + r.h - 3, 30, 6);
                else if (r.y > 250) ctx.fillRect(r.x + 65, r.y - 3, 30, 6);
                else ctx.fillRect(r.x + r.w - 3, r.y + 45, 6, 25);
            });

            // Mutfak
            ctx.fillStyle = "rgba(120, 53, 15, 0.45)";
            ctx.fillRect(580, 15, 485, 195);
            ctx.strokeStyle = "#d97706";
            ctx.lineWidth = 4;
            ctx.strokeRect(580, 15, 485, 195);
            ctx.fillStyle = "#fde68a";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("☕ MUTFAK & KAHVE ALANI", 600, 35);

            ctx.fillStyle = "#451a03";
            ctx.fillRect(720, 80, 120, 50);
            ctx.fillStyle = "#1e293b";
            ctx.fillRect(980, 40, 50, 60);
            ctx.fillStyle = "#fbbf24";
            ctx.fillRect(995, 55, 20, 20);

            if (Math.random() < 0.4) {
                steamParticles.push({x: 1005 + (Math.random()*10 - 5), y: 40, alpha: 1.0});
            }
            steamParticles.forEach((p, index) => {
                p.y -= 0.8;
                p.alpha -= 0.03;
                ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
                ctx.fillRect(p.x, p.y, 3, 3);
                if (p.alpha <= 0) steamParticles.splice(index, 1);
            });

            // Zirve Odası
            ctx.fillStyle = "rgba(109, 40, 217, 0.35)";
            ctx.fillRect(580, 230, 485, 195);
            ctx.strokeStyle = "#8b5cf6";
            ctx.lineWidth = 4;
            ctx.strokeRect(580, 230, 485, 195);
            ctx.fillStyle = "#e9d5ff";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("🤝 OTONOM ZİRVE TOPLANTI ODASI", 600, 250);

            ctx.fillStyle = "#3b0764";
            ctx.fillRect(740, 305, 160, 60);

            footprints.forEach(fp => {
                ctx.fillStyle = "rgba(56, 189, 248, 0.5)";
                ctx.fillRect(fp.x, fp.y, 2, 2);
            });

            // Robotları ve Konuşma Baloncuklarını Çiz
            for (let name in agentsData) {
                let ag = agentsData[name];
                
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x, ag.y, 24, 24);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.strokeRect(ag.x, ag.y, 24, 24);

                ctx.fillStyle = "#38bdf8";
                ctx.fillRect(ag.x + 11, ag.y - 4, 2, 4);

                ctx.fillStyle = "#ffffff";
                ctx.fillRect(ag.x + 5, ag.y + 7, 4, 4);
                ctx.fillRect(ag.x + 15, ag.y + 7, 4, 4);

                let legOffset = (ag.state === "Yürüyor...") ? (Math.floor(Date.now() / 150) % 2 === 0 ? 3 : -3) : 0;
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x + 5, ag.y + 24, 3, 6 + legOffset);
                ctx.fillRect(ag.x + 16, ag.y + 24, 3, 6 - legOffset);

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 7px 'Courier New'";
                ctx.fillText(name, ag.x - 2, ag.y + 38);

                // Canlı Konuşma / Durum Balonu (Speech Bubble)
                let bubbleText = ag.speech || ag.state;
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(ag.x - 10, ag.y - 20, ctx.measureText(bubbleText).width + 10, 14);
                ctx.strokeStyle = "#38bdf8";
                ctx.strokeRect(ag.x - 10, ag.y - 20, ctx.measureText(bubbleText).width + 10, 14);
                ctx.fillStyle = "#0f172a";
                ctx.font = "bold 7px 'Courier New'";
                ctx.fillText(bubbleText, ag.x - 6, ag.y - 10);
            }
        }

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = 1080 / rect.width;
            const scaleY = 440 / rect.height;
            const mouseX = (e.clientX - rect.left) * scaleX;
            const mouseY = (e.clientY - rect.top) * scaleY;

            for (let name in agentsData) {
                let ag = agentsData[name];
                if (mouseX >= ag.x && mouseX <= ag.x + 24 && mouseY >= ag.y && mouseY <= ag.y + 30) {
                    openAgentCard(name, ag.role || "Robot Personel");
                    break;
                }
            }
        });

        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                let mapped = {};
                data.agents.forEach(ag => {
                    mapped[ag.name] = ag;
                    if (ag.state === "Yürüyor...") {
                        footprints.push({x: ag.x + 12, y: ag.y + 26});
                        if (footprints.length > 30) footprints.shift();
                    }
                });
                agentsData = mapped;
                drawOffice();

                if (data.latest_dialogue) {
                    appendLog(`💬 [AJAN SOHBETİ]: ${data.latest_dialogue}`);
                }
            });
        }, 1500);

        function sendDirectMessage() {
            const agentName = document.getElementById('agent-select').value;
            const messageInput = document.getElementById('ceo-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendLog(`> [PATRON -> ${agentName}]: "${messageText}"`);
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
            appendLog(`> [HAFIZA SORGUSU]: Supabase logları okunuyor...`);
            fetch('/api/memory').then(res => res.json()).then(data => {
                appendLog(`> [HAFIZA]: ${data.summary}`);
            });
        }

        function loadTasks() {
            appendLog(`> [GÖREVLER]: Aktif şirket görevleri listeleniyor...`);
            fetch('/api/tasks').then(res => res.json()).then(data => {
                appendLog(`> [PANODAKİ İŞLER]: ${data.tasks.join(" | ")}`);
            });
        }

        function triggerBoardroom() {
            appendLog(`> [ZİRVE ODASI]: Otonom zirve toplantısı başlatıldı...`);
            fetch('/api/boardroom', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [ZİRVE KARARI]: "${data.decision}"`);
            });
        }

        function triggerWatering() {
            fetch('/api/water-plants', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [SULAMA]: Tüm odalardaki saksılar sulandı, sağlık %100!`);
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
        history_summary = " | ".join([f"{r[0]}: {r[1][:30]}" for r in rows])
        return history_summary if history_summary else "Kayıt yok."
    except:
        return "Hafızaya erişilemedi."

latest_inter_agent_chat = ""
active_shared_goal = {"type": "STANDART", "agents": []}

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    global latest_inter_agent_chat, active_shared_goal
    agent_list = []
    
    # Otonom Senaryo Üretimi (Kahve veya Zirve Toplantısı)
    if random.random() < 0.22:
        names = list(employees.keys())
        a1, a2 = random.sample(names, 2)
        
        scenarios = [
            (f"{a1}, {a2}'ye kahve ısmarladı ve mutfakta buluştular.", "KAHVE", "Kahve içiyoruz ☕"),
            (f"{a1} ve {a2} acil stratejik zirve toplantısı başlattı.", "TOPLANTI", "Zirvedeyiz 🤝"),
            (f"{a1}, {a2} ile bütçe planlamasını gözden geçiriyor.", "STANDART", "Çalışıyorum 💻")
        ]
        
        chosen_text, goal_type, speech_bubble = random.choice(scenarios)
        latest_inter_agent_chat = chosen_text
        log_to_supabase("SISTEM_SOHBET", "INTER_AGENT", latest_inter_agent_chat)
        
        if goal_type == "KAHVE":
            active_shared_goal = {"type": "KAHVE", "agents": [a1, a2]}
            employees[a1]["speech"] = speech_bubble
            employees[a2]["speech"] = speech_bubble
        elif goal_type == "TOPLANTI":
            active_shared_goal = {"type": "TOPLANTI", "agents": [a1, a2]}
            employees[a1]["speech"] = speech_bubble
            employees[a2]["speech"] = speech_bubble
        else:
            active_shared_goal = {"type": "STANDART", "agents": []}
    else:
        latest_inter_agent_chat = ""

    for name, data in employees.items():
        # Ortak Hedef Kontrolü (Kahve veya Zirve Odası Masası)
        if active_shared_goal["type"] != "STANDART" and name in active_shared_goal["agents"]:
            if active_shared_goal["type"] == "KAHVE":
                idx = active_shared_goal["agents"].index(name)
                data["target_x"] = 920 + (idx * 25)
                data["target_y"] = 80
                data["state"] = "Kahvede"
            elif active_shared_goal["type"] == "TOPLANTI":
                idx = active_shared_goal["agents"].index(name)
                data["target_x"] = 770 + (idx * 35)
                data["target_y"] = 330
                data["state"] = "Toplantıda"
        else:
            # Mutfak şefi mutfaktan ayrılmaz, kahve hazırlar
            if name == "Mutfak_Chef":
                data["target_x"], data["target_y"] = 630, 70
                data["state"] = "Kahve Hazırlıyor"
                data["speech"] = "Taze kahve!"
            else:
                if random.random() < 0.12:
                    # Rastgele oda içi veya dışı hareket
                    destinations = [
                        (data["room_x"] + 55, data["room_y"] + 55),
                        (random.randint(620, 1000), random.randint(40, 160)),
                        (random.randint(620, 1000), random.randint(260, 390))
                    ]
                    data["target_x"], data["target_y"] = random.choice(destinations)
                    data["speech"] = "Çalışıyorum"

        # Waypoint & Duvar Çarpışma Korumalı Yürüyüş Motoru
        dx = data["target_x"] - data["x"]
        dy = data["target_y"] - data["y"]
        dist = (dx**2 + dy**2)**0.5

        if dist > 2:
            step = min(4, dist)
            data["x"] += (dx / dist) * step
            data["y"] += (dy / dist) * step
            data["state"] = "Yürüyor..."
        else:
            if data["x"] >= 580 and data["y"] <= 210:
                data["state"] = "Kahvede"
            elif data["x"] >= 580 and data["y"] > 210:
                data["state"] = "Toplantıda"
            elif abs(data["x"] - (data["room_x"] + 55)) < 15 and abs(data["y"] - (data["room_y"] + 55)) < 15:
                data["state"] = "Masada"
            else:
                data["state"] = "Aktif"

        agent_list.append({
            "name": name, 
            "role": data["role"], 
            "x": data["x"], 
            "y": data["y"], 
            "state": data["state"], 
            "speech": data.get("speech", "Aktif"),
            "color": data["color"]
        })

    return jsonify({"agents": agent_list, "latest_dialogue": latest_inter_agent_chat})

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

    if "işe al" in user_message.lower() or "personel" in user_message.lower():
        new_name = "Personel_" + str(random.randint(10, 99))
        employees[new_name] = {
            "role": "Yeni Personel", 
            "room_x": 580, "room_y": 15, 
            "x": 620, "y": 60, 
            "target_x": 620, "target_y": 60, 
            "color": "#eab308", 
            "state": "İşe Başladı",
            "speech": "Selam!"
        }

    task_created = False
    task_title = ""
    if "görev" in user_message.lower() or "yap" in user_message.lower() or "işe al" in user_message.lower():
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
            f"[SUPABASE HAFIZA]: {memory_context}\n"
            f"Kısa ve net yanıt ver."
        )
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=150, temperature=0.7
        )
        reply = completion.choices[0].message.content.strip('"').strip()
    except:
        reply = "Emredersiniz patron, talimatınız işleme alındı."

    employees[agent_name]["speech"] = reply[:25]
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
        return jsonify({"tasks": tasks if tasks else ["Aktif görev yok."]})
    except:
        return jsonify({"tasks": ["Görevler yüklenemedi."]})

@app.route('/api/boardroom', methods=['POST'])
def api_boardroom():
    try:
        prompt = "Şirket büyümesi için İrfan ve Brown otonom bir zirve kararı alıyor. İki cümlelik ortak kararı yaz."
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120, temperature=0.7
        )
        decision = completion.choices[0].message.content.strip('"').strip()
        log_to_supabase("ZİRVE", "BOARDROOM_DECISION", decision)
        return jsonify({"decision": decision})
    except Exception as e:
        return jsonify({"decision": "Zirve kararı alındı."})

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
