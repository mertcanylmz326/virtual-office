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
        cur.execute("INSERT INTO office_plants (id, plant_name, health_level) VALUES (1, 'Merkezi Üs Saksısı', 100) ON CONFLICT (id) DO NOTHING;")
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

# 9 Ajan + Mutfak Personeli ve Saksı Eşleşmeleri
employees = {
    "Marco": {"role": "Destek", "room_x": 15, "room_y": 15, "x": 60, "y": 55, "target_x": 60, "target_y": 55, "color": "#3b82f6", "state": "Masada", "plant_health": 100},
    "Talisca": {"role": "Operasyon", "room_x": 175, "room_y": 15, "x": 220, "y": 55, "target_x": 220, "target_y": 55, "color": "#ef4444", "state": "Masada", "plant_health": 95},
    "Brown": {"role": "Yazılım", "room_x": 335, "room_y": 15, "x": 380, "y": 55, "target_x": 380, "target_y": 55, "color": "#10b981", "state": "Masada", "plant_health": 100},
    
    "Kante": {"role": "Pazarlama", "room_x": 15, "room_y": 145, "x": 60, "y": 185, "target_x": 60, "target_y": 185, "color": "#f59e0b", "state": "Masada", "plant_health": 90},
    "İrfan": {"role": "Finans", "room_x": 175, "room_y": 145, "x": 220, "y": 185, "target_x": 220, "target_y": 185, "color": "#8b5cf6", "state": "Masada", "plant_health": 100},
    "İsmail": {"role": "İK", "room_x": 335, "room_y": 145, "x": 380, "y": 185, "target_x": 380, "target_y": 185, "color": "#f97316", "state": "Masada", "plant_health": 85},
    
    "Alex": {"role": "Hukuk", "room_x": 15, "room_y": 275, "x": 60, "y": 315, "target_x": 60, "target_y": 315, "color": "#14b8a6", "state": "Masada", "plant_health": 100},
    "Skrinar": {"role": "Siber", "room_x": 175, "room_y": 275, "x": 220, "y": 315, "target_x": 220, "target_y": 315, "color": "#64748b", "state": "Masada", "plant_health": 95},
    "Kerem": {"role": "Başarı", "room_x": 335, "room_y": 275, "x": 380, "y": 315, "target_x": 380, "target_y": 315, "color": "#ec4899", "state": "Masada", "plant_health": 100},
    "Mutfak_Chef": {"role": "Mutfak Personeli", "room_x": 530, "room_y": 15, "x": 560, "y": 55, "target_x": 560, "target_y": 55, "color": "#f43f5e", "state": "Kahve Hazırlıyor", "plant_health": 100}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - AAA Indie Tycoon HQ</title>
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
            width: 1020px;
            height: 410px;
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

        .action-bar { margin: 10px auto; width: 1020px; max-width: 100%; display: flex; justify-content: space-between; gap: 10px; padding: 0 10px; box-sizing: border-box; }
        #command-panel {
            background: #0f172a; border: 2px solid #334155; padding: 8px; border-radius: 8px; display: flex; gap: 8px; align-items: center; flex-grow: 1;
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 6px 10px; border-radius: 6px; font-family: monospace; font-size: 11px; }
        input[type="text"] { flex-grow: 1; }
        .send-btn { background: #0284c7; color: #fff; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 15px auto; width: 1020px; max-width: 100%; background: #030712; border: 2px solid #334155; border-radius: 8px; text-align: left; overflow: hidden; box-sizing: border-box;
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
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO // AAA INDE TYCOON HQ</div>
        <div>
            <span class="top-btn" onclick="loadMemory()">🧠 HAFIZA</span>
            <span class="top-btn" onclick="loadTasks()">📋 GÖREVLER</span>
            <span class="top-btn" onclick="triggerBoardroom()">🤝 ZİRVE</span>
            <span class="top-btn" onclick="triggerWatering()">💧 SULA</span>
        </div>
    </div>

    <!-- Canvas Haritası -->
    <div id="game-container">
        <canvas id="officeCanvas" width="1020" height="410"></canvas>
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
            <span>⚡ AAA TYCOON LIVE OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8;">● TILE FLOORS & PARTICLES & BUBBLES ACTIVE</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Departman zemin motifleri, kahve buharı, saksı barları ve konuşma balonları yüklendi.</div>
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
        let steamParticles = []; // Kahve makinesi buhar parçacıkları

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
            document.getElementById('modal-status').innerText = "Durum: Görev başında, saksısı ve masası aktif.";
            document.getElementById('agent-modal').style.display = 'block';
        }

        function closeModal() {
            document.getElementById('agent-modal').style.display = 'none';
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        function drawOffice() {
            const w = 1020;
            const h = 410;
            ctx.clearRect(0, 0, w, h);

            // Zemin
            ctx.fillStyle = "#0b0f19";
            ctx.fillRect(0, 0, w, h);

            // Parke Koridorlar
            ctx.fillStyle = "#151c2c";
            ctx.fillRect(0, 120, w, 25);
            ctx.fillRect(0, 245, w, 25);
            ctx.fillRect(480, 0, 30, h);

            // 9 Ofis Odası (Departmana Özel Zemin Motifleri)
            const rooms = [
                {x: 15, y: 15, w: 145, h: 95, name: "1. MARCO", theme: "#111827"},
                {x: 175, y: 15, w: 145, h: 95, name: "2. TALİSCA", theme: "#111827"},
                {x: 335, y: 15, w: 145, h: 95, name: "3. BROWN (YAZILIM)", theme: "#064e3b"}, // Yazılım yeşilimsi zemin
                {x: 15, y: 145, w: 145, h: 95, name: "4. KANTE", theme: "#111827"},
                {x: 175, y: 145, w: 145, h: 95, name: "5. İRFAN (FİNANS)", theme: "#3b0764"}, // Finans morumsu zemin
                {x: 335, y: 145, w: 145, h: 95, name: "6. İSMAİL", theme: "#111827"},
                {x: 15, y: 275, w: 145, h: 95, name: "7. ALEX", theme: "#111827"},
                {x: 175, y: 275, w: 145, h: 95, name: "8. SKRİNAR", theme: "#111827"},
                {x: 335, y: 275, w: 145, h: 95, name: "9. KEREM", theme: "#111827"}
            ];

            rooms.forEach(r => {
                ctx.fillStyle = r.theme;
                ctx.fillRect(r.x, r.y, r.w, r.h);
                ctx.strokeStyle = "#475569";
                ctx.lineWidth = 3;
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

                // Odalara Özel Saksı 🌱 ve Sağlık Barı
                ctx.fillStyle = "#78350f";
                ctx.fillRect(r.x + 15, r.y + 50, 14, 16);
                ctx.fillStyle = "#4ade80";
                ctx.font = "10px sans-serif";
                ctx.fillText("🌿", r.x + 13, r.y + 45);

                // Sağlık Barı
                ctx.fillStyle = "#1e293b";
                ctx.fillRect(r.x + 12, r.y + 70, 20, 4);
                ctx.fillStyle = "#4ade80";
                ctx.fillRect(r.x + 12, r.y + 70, 16, 4);

                // Kapı Eşiği
                ctx.fillStyle = "#38bdf8";
                if (r.y < 120) ctx.fillRect(r.x + 60, r.y + r.h - 2, 25, 4);
                else if (r.y > 200) ctx.fillRect(r.x + 60, r.y - 2, 25, 4);
                else ctx.fillRect(r.x + r.w - 2, r.y + 40, 4, 20);
            });

            // Sağ Taraf: Mutfak (Karo Fayans Zemin ve Kahve Makinesi + Buhar)
            ctx.fillStyle = "rgba(120, 53, 15, 0.35)";
            ctx.fillRect(530, 15, 475, 185);
            ctx.strokeStyle = "#d97706";
            ctx.lineWidth = 3;
            ctx.strokeRect(530, 15, 475, 185);
            ctx.fillStyle = "#fde68a";
            ctx.font = "bold 9px 'Courier New'";
            ctx.fillText("☕ MUTFAK & KAHVE MAKİNESİ (FAYANS ZEMİN)", 545, 35);
            
            // Kahve Makinesi
            ctx.fillStyle = "#451a03";
            ctx.fillRect(920, 50, 40, 50);
            ctx.fillStyle = "#fbbf24";
            ctx.fillRect(930, 60, 20, 15);

            // Kahve Buharı Parçacıkları (Animasyonlu)
            if (Math.random() < 0.4) {
                steamParticles.push({x: 940 + randomRange(-5, 5), y: 50, alpha: 1.0});
            }
            steamParticles.forEach((p, index) => {
                p.y -= 0.8;
                p.alpha -= 0.03;
                ctx.fillStyle = `rgba(255, 255, 255, ${p.alpha})`;
                ctx.fillRect(p.x, p.y, 3, 3);
                if (p.alpha <= 0) steamParticles.splice(index, 1);
            });

            // Zirve Odası
            ctx.fillStyle = "rgba(109, 40, 217, 0.3)";
            ctx.fillRect(530, 215, 475, 185);
            ctx.strokeStyle = "#8b5cf6";
            ctx.lineWidth = 3;
            ctx.strokeRect(530, 215, 475, 185);
            ctx.fillStyle = "#e9d5ff";
            ctx.font = "bold 9px 'Courier New'";
            ctx.fillText("🤝 OTONOM ZİRVE TOPLANTI ODASI", 545, 235);

            // Ayak İzleri
            footprints.forEach(fp => {
                ctx.fillStyle = "rgba(56, 189, 248, 0.5)";
                ctx.fillRect(fp.x, fp.y, 2, 2);
            });

            // Robot Ajanları Çiz (Animasyonlu Eller, Bacaklar ve Konuşma Baloncukları)
            for (let name in agentsData) {
                let ag = agentsData[name];
                
                // Robot Kafa/Gövde
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x, ag.y, 22, 22);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.strokeRect(ag.x, ag.y, 22, 22);

                // Anten
                ctx.fillStyle = "#38bdf8";
                ctx.fillRect(ag.x + 10, ag.y - 4, 2, 4);

                // Robot Gözleri
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(ag.x + 4, ag.y + 6, 4, 4);
                ctx.fillRect(ag.x + 14, ag.y + 6, 4, 4);

                // Hareketli Bacaklar
                let legOffset = (ag.state === "Yürüyor...") ? (Math.floor(Date.now() / 150) % 2 === 0 ? 3 : -3) : 0;
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x + 4, ag.y + 22, 3, 6 + legOffset);
                ctx.fillRect(ag.x + 15, ag.y + 22, 3, 6 - legOffset);

                // Çalışırken veya kahvedeyken eller / kupa simgesi
                if (ag.state === "Masada") {
                    ctx.fillStyle = "#fbbf24";
                    ctx.fillRect(ag.x - 2, ag.y + 10, 2, 4); // Klavye üstü eller
                    ctx.fillRect(ag.x + 22, ag.y + 10, 2, 4);
                } else if (ag.state === "Kahvede") {
                    ctx.fillStyle = "#fff";
                    ctx.font = "8px sans-serif";
                    ctx.fillText("☕", ag.x + 24, ag.y + 12);
                }

                // İsim Etiketi
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 7px 'Courier New'";
                ctx.fillText(name, ag.x - 2, ag.y + 36);

                // Canvas Üstü İnteraktif Konuşma / Durum Balonu (Comic Bubble)
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(ag.x - 8, ag.y - 18, ctx.measureText(ag.state).width + 8, 12);
                ctx.strokeStyle = "#38bdf8";
                ctx.lineWidth = 1;
                ctx.strokeRect(ag.x - 8, ag.y - 18, ctx.measureText(ag.state).width + 8, 12);
                
                ctx.fillStyle = "#0f172a";
                ctx.font = "bold 7px 'Courier New'";
                ctx.fillText(ag.state, ag.x - 4, ag.y - 10);
            }
        }

        function randomRange(min, max) {
            return Math.random() * (max - min) + min;
        }

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = 1020 / rect.width;
            const scaleY = 410 / rect.height;
            const mouseX = (e.clientX - rect.left) * scaleX;
            const mouseY = (e.clientY - rect.top) * scaleY;

            for (let name in agentsData) {
                let ag = agentsData[name];
                if (mouseX >= ag.x && mouseX <= ag.x + 22 && mouseY >= ag.y && mouseY <= ag.y + 28) {
                    openAgentCard(name, ag.role || "Robot Personel");
                    break;
                }
            }
        });

        // Simülasyon Verisini Çek
        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                let mapped = {};
                data.agents.forEach(ag => {
                    mapped[ag.name] = ag;
                    if (ag.state === "Yürüyor...") {
                        footprints.push({x: ag.x + 11, y: ag.y + 24});
                        if (footprints.length > 25) footprints.shift();
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

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    global latest_inter_agent_chat
    agent_list = []
    
    if random.random() < 0.15:
        names = list(employees.keys())
        a1, a2 = random.sample(names, 2)
        dialogues = [
            f"{a1}, {a2}'ye kahve ısmarladı ve projeyi sordu.",
            f"{a1}, {a2} ile bütçe detaylarını tartıştı.",
            f"{a1}, {a2}'ye yeni siparişler hakkında bilgi verdi."
        ]
        latest_inter_agent_chat = random.choice(dialogues)
        log_to_supabase("SISTEM_SOHBET", "INTER_AGENT", latest_inter_agent_chat)
    else:
        latest_inter_agent_chat = ""

    for name, data in employees.items():
        if random.random() < 0.2:
            destinations = [
                (data["room_x"] + 45, data["room_y"] + 40),
                (random.randint(550, 930), random.randint(30, 150)),  # Mutfak
                (random.randint(550, 930), random.randint(230, 350)) # Zirve Odası
            ]
            dest = random.choice(destinations)
            data["target_x"], data["target_y"] = dest

        if data["x"] < data["target_x"]: data["x"] += min(5, data["target_x"] - data["x"])
        elif data["x"] > data["target_x"]: data["x"] -= min(5, data["x"] - data["target_x"])

        if data["y"] < data["target_y"]: data["y"] += min(5, data["target_y"] - data["y"])
        elif data["y"] > data["target_y"]: data["y"] -= min(5, data["y"] - data["target_y"])

        if data["x"] >= 510 and data["y"] <= 200:
            data["state"] = "Kahvede"
        elif data["x"] >= 510 and data["y"] > 200:
            data["state"] = "Toplantıda"
        elif abs(data["x"] - (data["room_x"] + 45)) < 15 and abs(data["y"] - (data["room_y"] + 40)) < 15:
            data["state"] = "Masada"
        else:
            data["state"] = "Yürüyor..."

        agent_list.append({
            "name": name, 
            "role": data["role"], 
            "x": data["x"], 
            "y": data["y"], 
            "state": data["state"], 
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
            "room_x": 530, "room_y": 15, 
            "x": 550, "y": 50, 
            "target_x": 550, "target_y": 50, 
            "color": "#eab308", 
            "state": "İşe Başladı", 
            "plant_health": 100
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
