import os
import time
import threading
import random
import datetime
import requests
import base64
import psycopg2
from flask import Flask, render_template_string, jsonify, request
from groq import Groq

app = Flask(__name__)

DB_URL = "postgresql://postgres.prphsmgaujdwrqqdmmrd:yaheroyamero@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
GROQ_API_KEY = "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"
COINGECKO_API_KEY = "CG-rU5NZkTSGvA1dXfNV58J26fK"
GITHUB_TOKEN = "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"
GITHUB_USERNAME = "mertcanymlz326"

# İsmail'in Yeni Sistem Sağlığı Anahtarları
UPTIMEROBOT_API_KEY = "u3671342-858d5db4b2fd40032fce3ce6"
SUPABASE_REST_URL = "https://prphsmgaujdwrqqdmmrd.supabase.co/rest/v1/"

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

company_state = {
    "budget": 22500,
    "crisis": "Yok",
    "active_clients": 6
}

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
            CREATE TABLE IF NOT EXISTS client_orders (
                id SERIAL PRIMARY KEY,
                client_name TEXT,
                project_type TEXT,
                status TEXT DEFAULT 'İşleniyor',
                repo_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

def get_crypto_price(coin_id="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
        headers = {"x-cg-demo-api-key": COINGECKO_API_KEY}
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        if coin_id in data:
            return data[coin_id]["usd"]
    except Exception as e:
        print(f"CoinGecko API Hatası: {e}")
    return None

def check_system_uptime():
    try:
        url = "https://api.uptimerobot.com/v2/getMonitors"
        payload = {
            "api_key": UPTIMEROBOT_API_KEY,
            "format": "json"
        }
        response = requests.post(url, data=payload, timeout=5)
        data = response.json()
        if data.get("stat") == "ok":
            monitors = data.get("monitors", [])
            if monitors:
                status_code = monitors[0].get("status")
                # 2: up, 8: seems offline, 9: offline
                status_text = "Aktif (Çalışıyor)" if status_code == 2.0 or status_code == 2 else f"Kod Durumu: {status_code}"
                return f"UptimeRobot: Sistem monitörleri {status_text}."
            else:
                return "UptimeRobot: Tanımlı monitör bulunamadı, ancak API bağlantısı başarılı."
    except Exception as e:
        print(f"UptimeRobot API Hatası: {e}")
    return "UptimeRobot API erişiminde geçici hata."

def create_github_repo_and_deploy(project_name, html_content):
    try:
        repo_name = f"e-trade-{int(time.time())}-{project_name.lower().replace(' ', '-')[:20]}"
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }
        repo_data = {
            "name": repo_name,
            "description": f"E-Trade Pro AI Agency - Otomatik Üretilen Proje: {project_name}",
            "private": False,
            "auto_init": True
        }
        r = requests.post("https://api.github.com/user/repos", json=repo_data, headers=headers, timeout=10)
        if r.status_code != 201:
            return None

        time.sleep(2)

        file_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{repo_name}/contents/index.html"
        encoded_content = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        file_data = {
            "message": "Brown agent: otomatik web sitesi şablonu eklendi",
            "content": encoded_content
        }
        r_file = requests.put(file_url, json=file_data, headers=headers, timeout=10)
        if r_file.status_code in [200, 201]:
            return f"https://github.com/{GITHUB_USERNAME}/{repo_name}"
    except Exception as e:
        print(f"GitHub Entegrasyon Hatası: {e}")
    return None

employees = {
    "Marco": {"role": "Destek", "salary": 800, "xp": 50, "level": 1, "title": "Junior", "room_x": 15, "room_y": 15, "x": 60, "y": 65, "target_x": 60, "target_y": 65, "color": "#3b82f6", "state": "Masada", "speech": "Destek hazır"},
    "Talisca": {"role": "Operasyon", "salary": 950, "xp": 70, "level": 1, "title": "Junior", "room_x": 195, "room_y": 15, "x": 240, "y": 65, "target_x": 240, "target_y": 65, "color": "#ef4444", "state": "Masada", "speech": "Süreç takipte"},
    "Brown": {"role": "Yazılım", "salary": 1200, "xp": 130, "level": 2, "title": "Senior", "room_x": 375, "room_y": 15, "x": 420, "y": 65, "target_x": 420, "target_y": 65, "color": "#10b981", "state": "Masada", "speech": "Kod yazılıyor"},
    
    "Kante": {"role": "Pazarlama", "salary": 900, "xp": 60, "level": 1, "title": "Junior", "room_x": 15, "room_y": 155, "x": 60, "y": 205, "target_x": 60, "target_y": 205, "color": "#f59e0b", "state": "Masada", "speech": "Lead topluyor"},
    "İrfan": {"role": "Finans", "salary": 1100, "xp": 100, "level": 2, "title": "Senior", "room_x": 195, "room_y": 155, "x": 240, "y": 205, "target_x": 240, "target_y": 205, "color": "#8b5cf6", "state": "Masada", "speech": "Bütçe kontrol"},
    "İsmail": {"role": "İK & Sistem", "salary": 850, "xp": 40, "level": 1, "title": "Junior", "room_x": 375, "room_y": 155, "x": 420, "y": 205, "target_x": 420, "target_y": 205, "color": "#f97316", "state": "Masada", "speech": "Sistem Sağlığı OK"},
    
    "Alex": {"role": "Hukuk", "salary": 1050, "xp": 90, "level": 2, "title": "Senior", "room_x": 15, "room_y": 295, "x": 60, "y": 345, "target_x": 60, "target_y": 345, "color": "#14b8a6", "state": "Masada", "speech": "Sözleşme aktif"},
    "Skrinar": {"role": "Siber", "salary": 1300, "xp": 160, "level": 3, "title": "Master", "room_x": 195, "room_y": 295, "x": 240, "y": 345, "target_x": 240, "target_y": 345, "color": "#64748b", "state": "Masada", "speech": "Firewall koruyor"},
    "Kerem": {"role": "Başarı", "salary": 950, "xp": 80, "level": 1, "title": "Junior", "room_x": 375, "room_y": 295, "x": 420, "y": 345, "target_x": 420, "target_y": 345, "color": "#ec4899", "state": "Masada", "speech": "Hedefler tuttu"},
    "Mutfak_Chef": {"role": "Mutfak", "salary": 700, "xp": 30, "level": 1, "title": "Chef", "room_x": 580, "room_y": 15, "x": 630, "y": 70, "target_x": 630, "target_y": 70, "color": "#f43f5e", "state": "Kahve Hazırlıyor", "speech": "Taze kahve!"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - AI Agency HQ</title>
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
        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }

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
        .terminal-body { padding: 10px; height: 110px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.4; word-break: break-word; overflow-wrap: break-word; }
        .log-line { margin-bottom: 4px; border-bottom: 1px dashed rgba(255,255,255,0.05); }

        #agent-modal {
            display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: #0f172a; border: 2px solid #38bdf8; padding: 20px; border-radius: 10px; z-index: 1000;
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.4); width: 280px; text-align: left;
        }

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
        <div style="font-weight: bold; color: #38bdf8; font-size: 13px;">🏢 E-TRADE PRO // İSMAİL UPTIME MONITOR HQ</div>
        <div>
            <span class="top-btn" onclick="loadMemory()">🧠 HAFIZA</span>
            <span class="top-btn" onclick="loadTasks()">📋 GÖREVLER</span>
            <span class="top-btn" onclick="checkUptime()">🛡️ SİSTEM SAĞLIĞI</span>
            <span class="top-btn" onclick="triggerBoardroom()">🤝 ZİRVE</span>
        </div>
    </div>

    <div id="stats-bar">
        <span style="color: #4ade80;">💰 KASA: $<span id="stat-budget">22500</span></span>
        <span style="color: #38bdf8;">👥 MÜŞTERİ: <span id="stat-clients">6</span></span>
        <span style="color: #fbbf24;">🚀 İSMAIL UPTIME: Aktif</span>
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
            <input type="text" id="ceo-message" placeholder="İsmail'e sistem durumunu sor veya Brown'a site kurdur..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ OPERATIONS TERMINAL</span>
            <span style="color: #38bdf8;">● UPTIMEROBOT & SUPABASE SYNCED</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: İsmail UptimeRobot ve Supabase REST denetim motoruyla donatıldı.</div>
        </div>
    </div>

    <!-- Karakter Kartı -->
    <div id="agent-modal">
        <h3 id="modal-title" style="color: #38bdf8; margin-top: 0;"></h3>
        <p id="modal-role" style="font-size: 12px; color: #94a3b8;"></p>
        <p id="modal-xp" style="font-size: 12px; color: #fbbf24;"></p>
        <p id="modal-status" style="font-size: 12px; color: #4ade80;"></p>
        <button onclick="closeModal()" class="top-btn" style="width: 100%; margin-top: 10px;">KAPAT</button>
    </div>

    <script>
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const terminalLogs = document.getElementById('terminal-logs');

        let agentsData = {};

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
            document.getElementById('modal-xp').innerText = "Departman Uzmanlığı: Sistem Operasyonları";
            document.getElementById('modal-status').innerText = "Durum: 7/24 Uptime denetimde.";
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

            ctx.fillStyle = "#111827";
            ctx.fillRect(0, 130, w, 35);
            ctx.fillRect(0, 270, w, 35);
            ctx.fillRect(530, 0, 35, h);

            const rooms = [
                {x: 15, y: 15, w: 160, h: 105, name: "1. MARCO", glow: "#3b82f6"},
                {x: 195, y: 15, w: 160, h: 105, name: "2. TALİSCA", glow: "#ef4444"},
                {x: 375, y: 15, w: 160, h: 105, name: "3. BROWN (DEV)", glow: "#10b981"},
                {x: 15, y: 155, w: 160, h: 105, name: "4. KANTE", glow: "#f59e0b"},
                {x: 195, y: 155, w: 160, h: 105, name: "5. İRFAN", glow: "#8b5cf6"},
                {x: 375, y: 155, w: 160, h: 105, name: "6. İSMAİL (İK)", glow: "#f97316"},
                {x: 15, y: 295, w: 160, h: 105, name: "7. ALEX", glow: "#14b8a6"},
                {x: 195, y: 295, w: 160, h: 105, name: "8. SKRİNAR", glow: "#64748b"},
                {x: 375, y: 295, w: 160, h: 105, name: "9. KEREM", glow: "#ec4899"}
            ];

            rooms.forEach(r => {
                ctx.fillStyle = "rgba(17, 24, 39, 0.85)";
                ctx.fillRect(r.x, r.y, r.w, r.h);

                ctx.strokeStyle = "rgba(56, 189, 248, 0.6)";
                ctx.lineWidth = 3;
                ctx.strokeRect(r.x, r.y, r.w, r.h);

                ctx.strokeStyle = r.glow;
                ctx.lineWidth = 1;
                ctx.strokeRect(r.x + 3, r.y + 3, r.w - 6, r.h - 6);

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(r.name, r.x + 8, r.y + 14);

                ctx.fillStyle = "#1e293b";
                ctx.fillRect(r.x + 50, r.y + 55, 60, 24);
                ctx.fillStyle = r.glow;
                ctx.fillRect(r.x + 68, r.y + 60, 24, 12);

                ctx.fillStyle = "#78350f";
                ctx.fillRect(r.x + 15, r.y + 55, 16, 18);
                ctx.fillStyle = "#4ade80";
                ctx.font = "12px sans-serif";
                ctx.fillText("🌿", r.x + 13, r.y + 50);

                ctx.fillStyle = "#4ade80";
                if (r.y < 130) ctx.fillRect(r.x + 65, r.y + r.h - 3, 30, 6);
                else if (r.y > 250) ctx.fillRect(r.x + 65, r.y - 3, 30, 6);
                else ctx.fillRect(r.x + r.w - 3, r.y + 45, 6, 25);
            });

            ctx.fillStyle = "rgba(2, 132, 199, 0.25)";
            ctx.fillRect(580, 135, 485, 30);
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 2;
            ctx.strokeRect(580, 135, 485, 30);
            ctx.fillStyle = "#38bdf8";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("👑 CEO KONTROL MERKEZİ", 600, 153);

            ctx.fillStyle = "rgba(120, 53, 15, 0.45)";
            ctx.fillRect(580, 15, 485, 110);
            ctx.strokeStyle = "#d97706";
            ctx.lineWidth = 3;
            ctx.strokeRect(580, 15, 485, 110);
            ctx.fillStyle = "#fde68a";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("☕ MUTFAK & KAHVE ALANI", 595, 30);

            ctx.fillStyle = "#451a03";
            ctx.fillRect(720, 55, 100, 40);
            ctx.fillStyle = "#1e293b";
            ctx.fillRect(960, 30, 40, 50);
            ctx.fillStyle = "#fbbf24";
            ctx.fillRect(970, 40, 18, 12);

            ctx.fillStyle = "rgba(109, 40, 217, 0.35)";
            ctx.fillRect(580, 175, 485, 250);
            ctx.strokeStyle = "#8b5cf6";
            ctx.lineWidth = 4;
            ctx.strokeRect(580, 175, 485, 250);
            ctx.fillStyle = "#e9d5ff";
            ctx.font = "bold 10px 'Courier New'";
            ctx.fillText("🤝 OTONOM PROJE ONAY ODASI", 600, 195);

            ctx.fillStyle = "#3b0764";
            ctx.fillRect(740, 270, 160, 60);

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

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 8px 'Courier New'";
                ctx.fillText(name + ` (${ag.title})`, ag.x - 6, ag.y + 38);

                let bubbleText = ag.speech || ag.state;
                ctx.fillStyle = "#f8fafc";
                ctx.fillRect(ag.x - 12, ag.y - 22, ctx.measureText(bubbleText).width + 12, 16);
                ctx.strokeStyle = "#38bdf8";
                ctx.strokeRect(ag.x - 12, ag.y - 22, ctx.measureText(bubbleText).width + 12, 16);
                ctx.fillStyle = "#0f172a";
                ctx.font = "bold 9px 'Courier New'";
                ctx.fillText(bubbleText, ag.x - 8, ag.y - 11);
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
                document.getElementById('stat-budget').innerText = data.budget;
                document.getElementById('stat-clients').innerText = data.active_clients;

                let mapped = {};
                data.agents.forEach(ag => {
                    mapped[ag.name] = ag;
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
                    appendLog(`> [GİTHUB DEPLOY]: Yeni web sitesi kodlandı ve GitHub'a yüklendi!`);
                    appendLog(`> [REPO LİNKİ]: <a href="${data.repo_url}" target="_blank" style="color: #38bdf8;">${data.repo_url}</a>`);
                }
            })
            .catch(err => {
                appendLog(`> [HATA]: Bağlantı kurulamadı.`);
            });
        }

        function loadMemory() {
            appendLog(`> [HAFIZA]: Supabase ajan hafızası taranıyor...`);
            fetch('/api/memory').then(res => res.json()).then(data => {
                appendLog(`> [HAFIZA ÖZETİ]: ${data.summary}`);
            });
        }

        function loadTasks() {
            appendLog(`> [GÖREVLER]: Otonom görev listesi yükleniyor...`);
            fetch('/api/tasks').then(res => res.json()).then(data => {
                appendLog(`> [AKTİF İŞLER]: ${data.tasks.join(" | ")}`);
            });
        }

        function checkUptime() {
            appendLog(`> [İSMAİL - UPTIME]: UptimeRobot API ile sistem sağlığı sorgulanıyor...`);
            fetch('/api/uptime').then(res => res.json()).then(data => {
                appendLog(`> [SİSTEM RAPORU]: ${data.status}`);
            });
        }

        function triggerBoardroom() {
            appendLog(`> [ZİRVE]: Otonom yönetim kurulu toplantısı başlatıldı...`);
            fetch('/api/boardroom', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [ZİRVE KARARI]: "${data.decision}"`);
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

tick_counter = 0

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    global tick_counter, company_state
    agent_list = []
    tick_counter += 1

    if tick_counter % 12 == 0:
        revenue = random.randint(2500, 5000)
        company_state["budget"] += revenue
        company_state["active_clients"] = random.randint(3, 8)

    for name, data in employees.items():
        if name == "Mutfak_Chef":
            data["x"], data["y"] = 630, 60
            data["state"] = "Kahve Hazırlıyor"
            data["speech"] = "Kahveler hazır!"
        else:
            data["x"] = data["room_x"] + 45
            data["y"] = data["room_y"] + 50
            data["state"] = "Masada Çalışıyor"
            data["speech"] = f"{data['role']} Aktif"

        agent_list.append({
            "name": name, 
            "role": data["role"], 
            "level": data["level"],
            "title": data["title"],
            "x": data["x"], 
            "y": data["y"], 
            "state": data["state"], 
            "speech": data["speech"],
            "color": data["color"]
        })

    return jsonify({
        "agents": agent_list, 
        "budget": company_state["budget"],
        "active_clients": company_state["active_clients"]
    })

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, employees=employees)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    agent_name = data.get('agent', 'Brown')
    user_message = data.get('message', '')

    if agent_name not in employees: agent_name = "Brown"
    agent = employees[agent_name]

    task_created = False
    task_title = ""
    repo_url = ""

    # Brown ile GitHub Repo Otomasyonu
    if agent_name == "Brown" and ("site" in user_message.lower() or "kur" in user_message.lower() or "yap" in user_message.lower() or "kod" in user_message.lower()):
        task_created = True
        task_title = user_message[:40]

        html_code = "<!DOCTYPE html><html><head><title>Proje</title></head><body><h1>E-Trade Pro AI Sitesi</h1></body></html>"
        try:
            code_prompt = f"Sen kıdemli bir yazılım uzmanısın. Kullanıcının şu isteği için eksiksiz, modern ve şık tek dosyalık bir HTML/CSS (Bootstrap veya dahili style içeren) web sitesi kodu yaz: '{user_message}'. Sadece ham HTML kodunu döndür, başka açıklama yazma."
            comp = groq_client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                messages=[{"role": "user", "content": code_prompt}],
                max_tokens=1500, temperature=0.3
            )
            raw_code = comp.choices[0].message.content.strip()
            if "```html" in raw_code:
                html_code = raw_code.split("```html")[1].split("```")[0].strip()
            elif "```" in raw_code:
                html_code = raw_code.split("```")[1].split("```")[0].strip()
            else:
                html_code = raw_code
        except Exception as e:
            print(f"Kod Üretim Hatası: {e}")

        repo_url = create_github_repo_and_deploy(task_title, html_code)

        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("INSERT INTO client_orders (client_name, project_type, repo_url) VALUES (%s, %s, %s)", ("Mertcan (CEO)", task_title, repo_url or "Başarısız"))
            conn.commit()
            cur.close()
            conn.close()
        except: pass

    # Canlı Veri (CoinGecko) İrfan için
    live_context = ""
    if agent_name == "İrfan" and ("btc" in user_message.lower() or "bitcoin" in user_message.lower() or "fiyat" in user_message.lower()):
        btc_price = get_crypto_price("bitcoin")
        if btc_price:
            live_context = f"[CANLI PİYASA VERİSİ]: Bitcoin (BTC) şu an anlık olarak ${btc_price:,} USD seviyesinden işlem görmektedir."

    # İsmail için Canlı Uptime Raporu
    uptime_context = ""
    if agent_name == "İsmail" and ("durum" in user_message.lower() or "sağlık" in user_message.lower() or "uptime" in user_message.lower() or "sistem" in user_message.lower()):
        uptime_status = check_system_uptime()
        uptime_context = f"[SİSTEM SAĞLIĞI]: {uptime_status}"

    reply = ""
    try:
        memory_context = query_supabase_memory(user_message)
        system_prompt = (
            f"Sen E-Trade Pro otonom ajansında {agent['role']} departmanında çalışan {agent_name} adında bir uzmansın. "
            f"Patronun Mertcan sana yazdı: '{user_message}'.\n"
            f"{live_context}\n"
            f"{uptime_context}\n"
            f"Kıdemli bir uzman gibi kısa, net, karizmatik ve doğrudan sonuca giden bir yanıt ver."
        )
        if task_created and repo_url:
            system_prompt += f" Proje başarıyla kodlandı ve GitHub'a yüklendi. Repo linki: {repo_url}"

        completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}],
            max_tokens=200, temperature=0.7
        )
        reply = completion.choices[0].message.content.strip('"').strip()
    except Exception as e:
        print(f"GROQ API HATASI: {e}")

    if not reply:
        if repo_url:
            reply = f"Patron site kodlandı ve GitHub'a atıldı: {repo_url}"
        elif agent_name == "İsmail":
            reply = check_system_uptime()
        else:
            reply = f"Emredersiniz patron, {agent['role']} olarak talimatınız işleme alındı."

    employees[agent_name]["speech"] = reply[:25]
    log_to_supabase(agent_name, "SYSTEM_OP", f"Talimat: {user_message} | Yanıt: {reply}")
    return jsonify({"status": reply, "task_created": task_created, "task_title": task_title, "repo_url": repo_url})

@app.route('/api/uptime', methods=['GET'])
def api_uptime():
    status = check_system_uptime()
    return jsonify({"status": status})

@app.route('/api/memory', methods=['GET'])
def api_memory():
    summary = query_supabase_memory("genel")
    return jsonify({"summary": summary})

@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT client_name, project_type, status, repo_url FROM client_orders ORDER BY id DESC LIMIT 5;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tasks = [f"[{r[0]}]: {r[1]} ({r[2]}) -> {r[3]}" for r in rows]
        return jsonify({"tasks": tasks if tasks else ["Bekleyen müşteri projesi yok."]})
    except:
        return jsonify({"tasks": ["Projeler yüklenemedi."]})

@app.route('/api/boardroom', methods=['POST'])
def api_boardroom():
    decision = ""
    try:
        prompt = "Otonom ajansın büyümesi için stratejik bir yapay zeka entegrasyon kararı al. İki cümlelik karar yaz."
        completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120, temperature=0.7
        )
        decision = completion.choices[0].message.content.strip('"').strip()
    except Exception as e:
        print(f"GROQ ZİRVE HATASI: {e}")
    
    if not decision:
        decision = "Yönetim kurulu otonom ağ altyapısını güçlendirme kararı aldı."

    log_to_supabase("ZİRVE", "AI_AGENCY_DECISION", decision)
    return jsonify({"decision": decision})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
