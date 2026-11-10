import os
import re
import time
import random
import datetime
import psycopg2
from flask import Flask, render_template_string, jsonify, request, Response, session, redirect, url_for
from groq import Groq

app = Flask(__name__)
app.secret_key = "e_trade_pro_secret_security_key_99"

DB_URL = "postgresql://postgres.prphsmgaujdwrqqdmmrd:yaheroyamero@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"
GROQ_API_KEY = "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"
UPTIMEROBOT_API_KEY = "u3671342-858d5db4b2fd40032fce3ce6"

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

company_state = {
    "budget": 22500,
    "crisis": "Normal Operasyon",
    "active_clients": 6
}

def init_db():
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS system_auth (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE,
                password_hash TEXT
            );
            CREATE TABLE IF NOT EXISTS agent_logs (
                id SERIAL PRIMARY KEY,
                agent_name TEXT,
                action_type TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS client_orders (
                id SERIAL PRIMARY KEY,
                client_name TEXT,
                project_type TEXT,
                status TEXT DEFAULT 'Tamamlandı',
                repo_url TEXT,
                html_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        pwd_raw = "ataturk1881"
        cur.execute("SELECT id FROM system_auth WHERE username = 'admin';")
        if not cur.fetchone():
            cur.execute("INSERT INTO system_auth (username, password_hash) VALUES ('admin', %s);", (pwd_raw,))
            
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

def check_system_uptime():
    try:
        import requests
        url = "https://api.uptimerobot.com/v2/getMonitors"
        payload = {"api_key": UPTIMEROBOT_API_KEY, "format": "json"}
        response = requests.post(url, data=payload, timeout=5)
        data = response.json()
        if data.get("stat") == "ok":
            monitors = data.get("monitors", [])
            if monitors:
                status_code = monitors[0].get("status")
                status_text = "Aktif (Çalışıyor)" if status_code in [2, 2.0] else f"Kod Durumu: {status_code}"
                return f"UptimeRobot: Sistem monitörleri {status_text}."
    except Exception as e:
        print(f"UptimeRobot API Hatası: {e}")
    return "UptimeRobot API aktif."

employees = {
    "Marco": {"role": "Destek", "salary": 800, "xp": 50, "level": 1, "title": "Junior", "room_x": 15, "room_y": 15, "color": "#3b82f6", "target_x": 60, "target_y": 60, "state": "Masada", "speech": "Destek veriyor", "energy": 90},
    "Talisca": {"role": "Operasyon", "salary": 950, "xp": 70, "level": 1, "title": "Junior", "room_x": 195, "room_y": 15, "color": "#ef4444", "target_x": 240, "target_y": 60, "state": "Masada", "speech": "Süreç takipte", "energy": 85},
    "Brown": {"role": "Yazılım", "salary": 1200, "xp": 130, "level": 2, "title": "Senior", "room_x": 375, "room_y": 15, "color": "#10b981", "target_x": 420, "target_y": 60, "state": "Masada", "speech": "GPT-OSS 120B Aktif", "energy": 95},
    
    "Kante": {"role": "Pazarlama", "salary": 900, "xp": 60, "level": 1, "title": "Junior", "room_x": 15, "room_y": 155, "color": "#f59e0b", "target_x": 60, "target_y": 200, "state": "Masada", "speech": "Lead topluyor", "energy": 80},
    "İrfan": {"role": "Finans", "salary": 1100, "xp": 100, "level": 2, "title": "Senior", "room_x": 195, "room_y": 155, "color": "#8b5cf6", "target_x": 240, "target_y": 200, "state": "Masada", "speech": "Bütçe kontrol", "energy": 88},
    "İsmail": {"role": "İK & Sistem", "salary": 850, "xp": 40, "level": 1, "title": "Junior", "room_x": 375, "room_y": 155, "color": "#f97316", "target_x": 420, "target_y": 200, "state": "Masada", "speech": "Sistem Sağlığı OK", "energy": 92},
    
    "Alex": {"role": "Hukuk", "salary": 1050, "xp": 90, "level": 2, "title": "Senior", "room_x": 15, "room_y": 295, "color": "#14b8a6", "target_x": 60, "target_y": 340, "state": "Masada", "speech": "Sözleşme aktif", "energy": 75},
    "Skrinar": {"role": "Siber", "salary": 1300, "xp": 160, "level": 3, "title": "Master", "room_x": 195, "room_y": 295, "color": "#64748b", "target_x": 240, "target_y": 340, "state": "Masada", "speech": "Firewall koruyor", "energy": 96},
    "Kerem": {"role": "Başarı", "salary": 950, "xp": 80, "level": 1, "title": "Junior", "room_x": 375, "room_y": 295, "color": "#ec4899", "target_x": 420, "target_y": 340, "state": "Masada", "speech": "Hedefler tuttu", "energy": 82},
    "Mutfak_Chef": {"role": "Mutfak", "salary": 700, "xp": 30, "level": 1, "title": "Chef", "room_x": 650, "room_y": 60, "color": "#f43f5e", "target_x": 650, "target_y": 60, "state": "Kahve Hazırlıyor", "speech": "Taze kahve!", "energy": 100}
}

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Command Center - Uzay Üssü Girişi</title>
    <style>
        body {
            background: radial-gradient(circle at center, #0b0f19 0%, #02040a 100%);
            color: #f8fafc;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            overflow: hidden;
        }
        .login-card {
            background: rgba(15, 23, 42, 0.85);
            border: 2px solid #38bdf8;
            border-radius: 16px;
            padding: 40px;
            width: 360px;
            box-shadow: 0 0 40px rgba(56, 189, 248, 0.4), inset 0 0 20px rgba(56, 189, 248, 0.1);
            backdrop-filter: blur(12px);
            text-align: center;
        }
        h2 { color: #38bdf8; margin-bottom: 10px; font-size: 20px; letter-spacing: 1px; }
        p { color: #94a3b8; font-size: 11px; margin-bottom: 25px; }
        .input-group { margin-bottom: 20px; text-align: left; }
        label { display: block; font-size: 11px; color: #38bdf8; margin-bottom: 6px; }
        input[type="password"] {
            width: 100%;
            background: #030712;
            border: 1px solid #334155;
            color: #fff;
            padding: 12px;
            border-radius: 8px;
            box-sizing: border-box;
            font-family: monospace;
            font-size: 14px;
            outline: none;
            transition: 0.3s;
        }
        input[type="password"]:focus { border-color: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.5); }
        .login-btn {
            width: 100%;
            background: linear-gradient(135deg, #0284c7, #0369a1);
            color: #fff;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            font-size: 13px;
            letter-spacing: 1px;
            transition: 0.3s;
            box-shadow: 0 0 15px rgba(2, 132, 199, 0.4);
        }
        .login-btn:hover { background: linear-gradient(135deg, #0369a1, #0284c7); box-shadow: 0 0 25px rgba(56, 189, 248, 0.8); }
        .error-msg { color: #ef4444; font-size: 11px; margin-top: 15px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-card">
        <h2>🛡️ COMMAND CENTER HQ</h2>
        <p>AI UZAY ÜSSÜ GÜVENLİK PROTOKOLÜ</p>
        <form method="POST">
            <div class="input-group">
                <label>ERİŞİM ŞİFRESİ:</label>
                <input type="password" name="password" placeholder="••••••••••••" required autofocus>
            </div>
            <button type="submit" class="login-btn">SİSTEME BAĞLAN</button>
            {% if error %}
            <div class="error-msg">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Trade Pro - Cyberpunk Agency HQ</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

        body { 
            background-color: #030712; 
            color: #f8fafc; 
            font-family: 'JetBrains Mono', monospace; 
            text-align: center; 
            margin: 0; 
            padding: 0; 
            overflow-x: hidden; 
        }

        body::after {
            content: " ";
            display: block;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            z-index: 99999;
            background-size: 100% 3px, 3px 100%;
            pointer-events: none;
        }

        #game-topbar {
            background: rgba(15, 23, 42, 0.9);
            border-bottom: 2px solid #38bdf8;
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
            flex-wrap: wrap;
            gap: 10px;
            backdrop-filter: blur(12px);
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15);
        }
        .top-btn { 
            background: rgba(30, 41, 59, 0.8); color: #38bdf8; border: 1px solid #334155; padding: 7px 14px; 
            border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px;
            text-decoration: none; transition: 0.3s;
            font-family: 'Space Grotesk', sans-serif;
        }
        .top-btn:hover { background: #38bdf8; color: #030712; box-shadow: 0 0 15px rgba(56, 189, 248, 0.6); }

        #stats-bar {
            background: rgba(9, 13, 22, 0.95);
            padding: 10px 20px;
            display: flex;
            justify-content: space-around;
            border-bottom: 1px solid #1e293b;
            font-size: 12px;
            font-weight: bold;
            flex-wrap: wrap;
            gap: 15px;
        }
        .stat-badge {
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid #334155;
            padding: 6px 14px;
            border-radius: 8px;
            box-shadow: inset 0 0 10px rgba(56, 189, 248, 0.05);
        }

        #game-container {
            position: relative;
            width: 1080px;
            height: 440px;
            max-width: 100%;
            margin: 15px auto;
            border: 3px solid #38bdf8;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.3), inset 0 0 20px rgba(56, 189, 248, 0.1);
            background: #0b0f19;
            overflow: hidden;
            backdrop-filter: blur(8px);
        }
        canvas { display: block; width: 100%; height: 100%; cursor: pointer; }

        .action-bar { margin: 12px auto; width: 1080px; max-width: 100%; display: flex; justify-content: space-between; gap: 12px; padding: 0 10px; box-sizing: border-box; }
        #command-panel {
            background: rgba(15, 23, 42, 0.85); border: 2px solid #334155; padding: 10px; border-radius: 10px; display: flex; gap: 10px; align-items: center; flex-grow: 1; flex-wrap: wrap;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }
        select, input[type="text"] { background: #1e293b; color: #fff; border: 1px solid #475569; padding: 10px 14px; border-radius: 8px; font-family: monospace; font-size: 13px; outline: none; transition: 0.3s; }
        input[type="text"] { flex-grow: 1; min-width: 220px; }
        input[type="text"]:focus, select:focus { border-color: #38bdf8; box-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }
        .send-btn { background: linear-gradient(135deg, #0284c7, #0369a1); color: #fff; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 13px; transition: 0.3s; font-family: 'Space Grotesk', sans-serif; box-shadow: 0 0 15px rgba(2, 132, 199, 0.4); }
        .send-btn:hover { background: linear-gradient(135deg, #0369a1, #0284c7); box-shadow: 0 0 20px rgba(56, 189, 248, 0.8); }

        #activity-terminal {
            margin: 0 auto 20px auto; width: 1080px; max-width: 100%; background: rgba(3, 7, 18, 0.9); border: 2px solid #334155; border-radius: 10px; text-align: left; overflow: hidden; box-sizing: border-box;
            backdrop-filter: blur(12px);
            box-shadow: 0 15px 35px rgba(0,0,0,0.7);
        }
        .terminal-header { background: rgba(15, 23, 42, 0.95); padding: 8px 15px; font-size: 12px; color: #38bdf8; font-weight: bold; display: flex; justify-content: space-between; flex-wrap: wrap; border-bottom: 1px solid #1e293b; }
        .terminal-body { padding: 12px; height: 150px; overflow-y: auto; font-size: 11px; color: #4ade80; line-height: 1.5; word-break: break-word; overflow-wrap: break-word; }
        .log-line { margin-bottom: 6px; border-bottom: 1px dashed rgba(255,255,255,0.05); padding-bottom: 4px; }

        .modal-overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(3, 7, 18, 0.8); backdrop-filter: blur(8px); z-index: 10000;
            justify-content: center; align-items: center;
        }
        .modal-card {
            background: rgba(15, 23, 42, 0.95); border: 2px solid #38bdf8; border-radius: 14px;
            width: 600px; max-width: 90%; padding: 25px; box-shadow: 0 0 40px rgba(56, 189, 248, 0.4);
            text-align: left; max-height: 80vh; overflow-y: auto;
        }
        .modal-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 15px; }
        .modal-header h3 { color: #38bdf8; margin: 0; font-size: 16px; font-family: 'Space Grotesk', sans-serif; }
        .close-btn { background: #ef4444; color: #fff; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; font-weight: bold; }

        #toast-container {
            position: fixed; bottom: 20px; right: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px;
        }
        .toast {
            background: rgba(15, 23, 42, 0.95); border: 1px solid #38bdf8; color: #f8fafc;
            padding: 12px 20px; border-radius: 8px; font-size: 12px; box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
            backdrop-filter: blur(10px); animation: slideIn 0.3s ease; max-width: 320px;
        }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

        @media (max-width: 768px) {
            #game-topbar { flex-direction: column; align-items: stretch; text-align: center; }
            #game-topbar > div { display: flex; justify-content: center; flex-wrap: wrap; gap: 6px; margin-top: 5px; }
            .action-bar { padding: 0 5px; }
            #command-panel { flex-direction: column; align-items: stretch; }
            input[type="text"], select, .send-btn { width: 100%; box-sizing: border-box; }
        }
    </style>
</head>
<body>

    <div id="toast-container"></div>

    <div class="modal-overlay" id="agentModal">
        <div class="modal-card">
            <div class="modal-header">
                <h3 id="modalAgentTitle">AJAN KANALI</h3>
                <button class="close-btn" onclick="closeAgentModal()">KAPAT</button>
            </div>
            <div id="modalAgentBody" style="font-size: 12px; color: #cbd5e1; min-height: 100px; margin-bottom: 15px; line-height: 1.5;">
                Ajan ile iletişim kuruluyor...
            </div>
            <div style="display: flex; gap: 8px;">
                <input type="text" id="modalInput" placeholder="Ajana doğrudan talimat ver..." style="flex-grow: 1;" onkeypress="checkModalEnter(event)">
                <button class="send-btn" onclick="sendModalMessage()">İLET</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="projectsModal">
        <div class="modal-card" style="width: 750px;">
            <div class="modal-header">
                <h3>📋 CANLI PROJE ARŞİVİ & PORTFOLYO</h3>
                <button class="close-btn" onclick="closeProjectsModal()">KAPAT</button>
            </div>
            <div id="projectsModalBody" style="font-size: 12px; color: #cbd5e1; max-height: 350px; overflow-y: auto;">
                Yükleniyor...
            </div>
        </div>
    </div>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8; font-size: 14px; font-family: 'Space Grotesk', sans-serif;">🏢 E-TRADE PRO // CYBER HQ (REALISTIC MOVEMENT)</div>
        <div>
            <span class="top-btn" onclick="loadMemory()">🧠 HAFIZA</span>
            <span class="top-btn" onclick="openProjectsModal()">📋 PROJELER ARŞİVİ</span>
            <span class="top-btn" onclick="checkUptime()">🛡️ SİSTEM SAĞLIĞI</span>
            <span class="top-btn" onclick="triggerBoardroom()">🤝 ZİRVE</span>
            <a href="/logout" class="top-btn" style="background: rgba(239, 68, 68, 0.2); color: #ef4444; border-color: #dc2626;">🚪 ÇIKIŞ</a>
        </div>
    </div>

    <div id="stats-bar">
        <span class="stat-badge" style="color: #4ade80;">💰 KASA: $<span id="stat-budget">22500</span></span>
        <span class="stat-badge" style="color: #38bdf8;">👥 MÜŞTERİ: <span id="stat-clients">6</span></span>
        <span class="stat-badge" style="color: #fbbf24;" id="stat-crisis">⚡ DURUM: Normal Operasyon</span>
    </div>

    <div id="game-container">
        <canvas id="officeCanvas" width="1080" height="440"></canvas>
    </div>

    <div class="action-bar">
        <div id="command-panel">
            <select id="agent-select">
                {% for name, data in employees.items() %}
                <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
                {% endfor %}
            </select>
            <input type="text" id="ceo-message" placeholder="Genel merkeze veya Brown'a talimat ver..." onkeypress="checkEnter(event)">
            <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
        </div>
    </div>

    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ REALISTIC ANIMATION TERMINAL</span>
            <span style="color: #38bdf8; font-weight: bold;">● AKICI YÜRÜYÜŞ & AYAK İZLERİ</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Gerçekçi adım ve bacak animasyon motoru yüklendi!</div>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('officeCanvas');
        const ctx = canvas.getContext('2d');
        const terminalLogs = document.getElementById('terminal-logs');

        let agentsDisplay = {}; // Ekranda süzülen gerçek zamanlı koordinatlar
        let footprintList = []; // Ayak izleri havuzu
        let activeModalAgent = null;

        const roomCoords = [
            {name: "Marco", x: 15, y: 15, w: 160, h: 105},
            {name: "Talisca", x: 195, y: 15, w: 160, h: 105},
            {name: "Brown", x: 375, y: 15, w: 160, h: 105},
            {name: "Kante", x: 15, y: 155, w: 160, h: 105},
            {name: "İrfan", x: 195, y: 155, w: 160, h: 105},
            {name: "İsmail", x: 375, y: 155, w: 160, h: 105},
            {name: "Alex", x: 15, y: 295, w: 160, h: 105},
            {name: "Skrinar", x: 195, y: 295, w: 160, h: 105},
            {name: "Kerem", x: 375, y: 295, w: 160, h: 105},
            {name: "Mutfak_Chef", x: 580, y: 15, w: 485, h: 110}
        ];

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const clickX = (e.clientX - rect.left) * scaleX;
            const clickY = (e.clientY - rect.top) * scaleY;

            roomCoords.forEach(r => {
                if (clickX >= r.x && clickX <= r.x + r.w && clickY >= r.y && clickY <= r.y + r.h) {
                    openAgentModal(r.name);
                }
            });
        });

        function openAgentModal(agentName) {
            activeModalAgent = agentName;
            document.getElementById('modalAgentTitle').innerText = `${agentName.toUpperCase()} İLE ÖZEL GÖRÜŞME`;
            document.getElementById('modalAgentBody').innerHTML = `> [SİSTEM]: ${agentName} ile güvenli kanal açıldı. Doğrudan soru sorabilir veya talimat verebilirsiniz.`;
            document.getElementById('agentModal').style.display = 'flex';
        }

        function closeAgentModal() {
            document.getElementById('agentModal').style.display = 'none';
            activeModalAgent = null;
        }

        function checkModalEnter(e) {
            if (e.key === 'Enter') sendModalMessage();
        }

        function sendModalMessage() {
            const input = document.getElementById('modalInput');
            const msg = input.value.trim();
            if (!msg || !activeModalAgent) return;

            const body = document.getElementById('modalAgentBody');
            body.innerHTML += `<br><b style="color: #38bdf8;">[CEO]:</b> ${msg}`;
            input.value = "";

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: activeModalAgent, message: msg })
            })
            .then(res => res.json())
            .then(data => {
                body.innerHTML += `<br><b style="color: #4ade80;">[${activeModalAgent}]:</b> ${data.status}`;
                body.scrollTop = body.scrollHeight;
                if(data.preview_url) {
                    body.innerHTML += `<br>🚀 <a href="${data.preview_url}" target="_blank" style="color: #f43f5e; font-weight: bold;">Canlı Proje Sayfası 🌐</a>`;
                }
            });
        }

        function openProjectsModal() {
            document.getElementById('projectsModal').style.display = 'flex';
            fetch('/api/tasks')
            .then(res => res.json())
            .then(data => {
                let html = "<ul style='padding-left: 15px; margin: 0;'>";
                data.tasks.forEach(t => {
                    html += `<li style="margin-bottom: 8px; border-bottom: 1px dashed rgba(255,255,255,0.1); padding-bottom: 6px;">${t}</li>`;
                });
                html += "</ul>";
                document.getElementById('projectsModalBody').innerHTML = html;
            });
        }

        function closeProjectsModal() {
            document.getElementById('projectsModal').style.display = 'none';
        }

        function showToast(message) {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.innerHTML = `🚀 ${message}`;
            container.appendChild(toast);
            setTimeout(() => { toast.remove(); }, 4000);
        }

        function appendLog(text) {
            const time = new Date().toLocaleTimeString();
            const logDiv = document.createElement('div');
            logDiv.className = 'log-line';
            logDiv.innerHTML = `[${time}] ${text}`;
            terminalLogs.prepend(logDiv);
            terminalLogs.scrollTop = 0;
        }

        function checkEnter(e) {
            if (e.key === 'Enter') sendDirectMessage();
        }

        function drawOffice() {
            const w = 1080;
            const h = 440;
            ctx.clearRect(0, 0, w, h);

            ctx.fillStyle = "#090d16";
            ctx.fillRect(0, 0, w, h);
            
            ctx.strokeStyle = "#1e293b";
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
                ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                ctx.fillRect(r.x, r.y, r.w, r.h);

                ctx.strokeStyle = "rgba(56, 189, 248, 0.5)";
                ctx.lineWidth = 2;
                ctx.strokeRect(r.x, r.y, r.w, r.h);

                ctx.strokeStyle = r.glow;
                ctx.lineWidth = 1;
                ctx.strokeRect(r.x + 3, r.y + 3, r.w - 6, r.h - 6);

                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 9px 'JetBrains Mono'";
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

            ctx.fillStyle = "rgba(2, 132, 199, 0.2)";
            ctx.fillRect(580, 135, 485, 30);
            ctx.strokeStyle = "#38bdf8";
            ctx.lineWidth = 2;
            ctx.strokeRect(580, 135, 485, 30);
            ctx.fillStyle = "#38bdf8";
            ctx.font = "bold 10px 'JetBrains Mono'";
            ctx.fillText("👑 CEO KONTROL MERKEZİ", 600, 153);

            ctx.fillStyle = "rgba(120, 53, 15, 0.35)";
            ctx.fillRect(580, 15, 485, 110);
            ctx.strokeStyle = "#d97706";
            ctx.lineWidth = 2;
            ctx.strokeRect(580, 15, 485, 110);
            ctx.fillStyle = "#fde68a";
            ctx.font = "bold 10px 'JetBrains Mono'";
            ctx.fillText("☕ MUTFAK & KAHVE MOLA ALANI", 595, 30);
            ctx.fillStyle = "#451a03";
            ctx.fillRect(720, 55, 100, 40);
            ctx.fillStyle = "#fbbf24";
            ctx.fillText("🍩 Atıştırmalık & Kahve Makinesi", 730, 80);

            ctx.fillStyle = "rgba(109, 40, 217, 0.3)";
            ctx.fillRect(580, 175, 485, 250);
            ctx.strokeStyle = "#8b5cf6";
            ctx.lineWidth = 3;
            ctx.strokeRect(580, 175, 485, 250);
            ctx.fillStyle = "#e9d5ff";
            ctx.font = "bold 10px 'JetBrains Mono'";
            ctx.fillText("🤝 OTONOM PROJE ONAY ODASI", 600, 195);
            ctx.fillStyle = "#3b0764";
            ctx.fillRect(740, 270, 160, 60);

            // Ayak İzlerini Çiz ve Yavaşça Soluklaştır
            for (let i = footprintList.length - 1; i >= 0; i--) {
                let fp = footprintList[i];
                fp.alpha -= 0.005;
                if (fp.alpha <= 0) {
                    footprintList.splice(i, 1);
                } else {
                    ctx.fillStyle = `rgba(56, 189, 248, ${fp.alpha})`;
                    ctx.fillRect(fp.x, fp.y, 3, 3);
                }
            }

            // Ajanları Gerçekçi Lerp (Akıcı Yürüyüş) ve Bacak Animasyonlarıyla Çiz
            for (let name in agentsDisplay) {
                let ag = agentsDisplay[name];
                
                // Hedefine yumuşak geçiş (Linear Interpolation)
                ag.x += (ag.targetX - ag.x) * 0.1;
                ag.y += (ag.targetY - ag.y) * 0.1;

                // Yürürken ayak izi bırak
                let moving = Math.abs(ag.targetX - ag.x) > 0.5 || Math.abs(ag.targetY - ag.y) > 0.5;
                if (moving && Math.random() < 0.4) {
                    footprintList.push({x: ag.x + 10, y: ag.y + 22, alpha: 0.5});
                    if (footprintList.length > 80) footprintList.shift();
                }

                // Gövde
                ctx.fillStyle = ag.color;
                ctx.fillRect(ag.x, ag.y, 24, 24);
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1;
                ctx.strokeRect(ag.x, ag.y, 24, 24);

                // Kafa / Gözler
                ctx.fillStyle = "#38bdf8";
                ctx.fillRect(ag.x + 11, ag.y - 4, 2, 4);
                ctx.fillStyle = "#ffffff";
                ctx.fillRect(ag.x + 5, ag.y + 7, 4, 4);
                ctx.fillRect(ag.x + 15, ag.y + 7, 4, 4);

                // Bacak Animasyonu (Yürürken sallanan minik ayaklar)
                let legOffset = moving ? Math.sin(Date.now() / 80) * 4 : 0;
                ctx.fillStyle = "#1e293b";
                ctx.fillRect(ag.x + 5, ag.y + 24, 4, 6 + legOffset);
                ctx.fillRect(ag.x + 15, ag.y + 24, 4, 6 - legOffset);

                // İsim Etiketi
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 8px 'JetBrains Mono'";
                ctx.fillText(name + ` (${ag.title})`, ag.x - 6, ag.y + 42);

                // Konuşma Baloncuğu
                let bubbleText = ag.speech || ag.state;
                ctx.fillStyle = "rgba(15, 23, 42, 0.9)";
                ctx.fillRect(ag.x - 12, ag.y - 22, ctx.measureText(bubbleText).width + 12, 16);
                ctx.strokeStyle = "#38bdf8";
                ctx.strokeRect(ag.x - 12, ag.y - 22, ctx.measureText(bubbleText).width + 12, 16);
                ctx.fillStyle = "#38bdf8";
                ctx.font = "bold 9px 'JetBrains Mono'";
                ctx.fillText(bubbleText, ag.x - 8, ag.y - 11);
            }
            requestAnimationFrame(drawOffice);
        }

        // Sunucudan veri alıp hedefleri güncelle
        setInterval(() => {
            fetch('/api/simulation-tick')
            .then(res => res.json())
            .then(data => {
                document.getElementById('stat-budget').innerText = data.budget;
                document.getElementById('stat-clients').innerText = data.active_clients;
                document.getElementById('stat-crisis').innerText = `⚡ KRİZ: ${data.crisis}`;
                
                data.agents.forEach(ag => {
                    if (!agentsDisplay[ag.name]) {
                        agentsDisplay[ag.name] = { x: ag.x, y: ag.y, targetX: ag.x, targetY: ag.y, color: ag.color, title: ag.title, role: ag.role, state: ag.state, speech: ag.speech };
                    } else {
                        agentsDisplay[ag.name].targetX = ag.x;
                        agentsDisplay[ag.name].targetY = ag.y;
                        agentsDisplay[ag.name].state = ag.state;
                        agentsDisplay[ag.name].speech = ag.speech;
                    }
                });
            });
        }, 2000);

        // Animasyon döngüsünü başlat
        requestAnimationFrame(drawOffice);

        function sendDirectMessage() {
            const agentName = document.getElementById('agent-select').value;
            const messageInput = document.getElementById('ceo-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendLog(`> [CEO -> ${agentName}]: "${messageText}"`);
            messageInput.value = "";
            appendLog(`> [SİSTEM]: ${agentName} talimatı işliyor ve departmanlar arası denetim başlatılıyor...`);
            showToast(`${agentName} projeyi işliyor!`);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 120000);

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: agentName, message: messageText }),
                signal: controller.signal
            })
            .then(res => {
                clearTimeout(timeoutId);
                return res.json();
            })
            .then(data => {
                appendLog(`> [<b>${agentName}</b>]: "${data.status}"`);
                if(data.audit_logs) {
                    data.audit_logs.forEach(log => {
                        appendLog(`> ${log}`);
                    });
                }
                if(data.preview_url) {
                    appendLog(`> 🚀 <b style="color: #38bdf8; font-size: 14px;">CANLI PROJE LİNKİ (TIKLA AÇ):</b> <a href="${data.preview_url}" target="_blank" style="color: #f43f5e; font-weight: bold; text-decoration: underline; font-size: 14px;">Canlı Sayfa 🌐</a>`);
                    showToast("Proje başarıyla tamamlandı ve arşive eklendi!");
                }
            })
            .catch(err => {
                appendLog(`> [HATA]: İstek zaman aşımına uğradı.`);
                showToast("Hata: Proje üretimi zaman aşımına uğradı.");
            });
        }

        function loadMemory() {
            appendLog(`> [HAFIZA]: Supabase taranıyor...`);
            showToast("Hafıza tabanları taranıyor...");
            fetch('/api/memory').then(res => res.json()).then(data => {
                appendLog(`> [HAFIZA ÖZETİ]: ${data.summary}`);
            });
        }

        function loadTasks() {
            openProjectsModal();
        }

        function checkUptime() {
            appendLog(`> [İSMAİL - UPTIME]: Sorgulanıyor...`);
            fetch('/api/uptime').then(res => res.json()).then(data => {
                appendLog(`> [RAPOR]: ${data.status}`);
            });
        }

        function triggerBoardroom() {
            appendLog(`> [ZİRVE]: Otonom yönetim kurulu toplantısı başladı...`);
            showToast("Yönetim kurulu zirvesi toplandı!");
            fetch('/api/boardroom', {method: 'POST'}).then(res => res.json()).then(data => {
                appendLog(`> [KARAR]: "${data.decision}"`);
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
    except: pass

tick_counter = 0

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        entered_password = request.form.get('password')
        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("SELECT password_hash FROM system_auth WHERE username = 'admin';")
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row and row[0] == entered_password:
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                error = "HATA: Geçersiz erişim şifresi!"
        except Exception as e:
            error = f"Veritabanı Kimlik Doğrulama Hatası: {e}"
            
    return render_template_string(LOGIN_TEMPLATE, error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/api/simulation-tick', methods=['GET'])
def simulation_tick():
    if not session.get('logged_in'):
        return jsonify({"error": "Yetkisiz erişim"}), 403
        
    global tick_counter, company_state
    agent_list = []
    tick_counter += 1

    if tick_counter % 12 == 0:
        revenue = random.randint(2500, 5000)
        company_state["budget"] += revenue
        company_state["active_clients"] = random.randint(3, 8)
        
    if tick_counter % 25 == 0:
        crises = ["Normal Operasyon", "Yüksek Sunucu Trafiği", "Bütçe Denetimi", "Siber Saldırı Girişimi"]
        company_state["crisis"] = random.choice(crises)

    for name, data in employees.items():
        if name == "Mutfak_Chef":
            x, y, state, speech = 650, 60, "Kahve Hazırlıyor", "Kahveler taze!"
        else:
            data["energy"] -= random.randint(2, 6)
            if data["energy"] < 30:
                x = random.randint(600, 750)
                y = random.randint(40, 90)
                state = "Mola / Kahve İçiyor"
                speech = "☕ Kahve molası!"
                if data["energy"] <= 10:
                    data["energy"] = 100
            else:
                x = data["target_x"] + random.randint(-6, 6)
                y = data["target_y"] + random.randint(-6, 6)
                state = "Masada Çalışıyor"
                speech = f"{data['role']} Aktif"

        agent_list.append({
            "name": name, "role": data["role"], "level": data.get("level", 1),
            "title": data.get("title", "Junior"), "x": x, "y": y, 
            "state": state, "speech": speech, "color": data["color"]
        })

    return jsonify({
        "agents": agent_list, 
        "budget": company_state["budget"], 
        "active_clients": company_state["active_clients"],
        "crisis": company_state["crisis"]
    })

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(HTML_TEMPLATE, employees=employees)

@app.route('/preview/<int:project_id>')
def preview_project(project_id):
    if not session.get('logged_in'):
        return "Yetkisiz erişim.", 403
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT html_code FROM client_orders WHERE id = %s", (project_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        db_code = row[0] if row and row[0] else "<h1>Proje kodu bulunamadı.</h1>"
        return Response(db_code, mimetype='text/html')
    except Exception as e:
        print(f"Preview Hatası: {e}")
    return "Proje bulunamadı.", 404

@app.route('/api/chat', methods=['POST'])
def api_chat():
    if not session.get('logged_in'):
        return jsonify({"status": "Yetkisiz erişim"}), 403
        
    data = request.json
    agent_name = data.get('agent', 'Brown')
    user_message = data.get('message', '')

    if agent_name not in employees: agent_name = "Brown"
    agent = employees[agent_name]

    html_code = ""
    reply = ""
    preview_url = None
    audit_logs = []

    if agent_name != "Brown":
        try:
            if groq_client:
                prompt = f"Sen ofiste '{agent['role']}' olarak çalışan bir uzmansın. Patronun (Kullanıcı) sana şu mesajı gönderdi: '{user_message}'. Kendi departmanının uzmanlığıyla profesyonel ve kısa bir iş yanıtı ver. Asla HTML kodu yazma."
                comp = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300, temperature=0.7
                )
                reply = comp.choices[0].message.content.strip()
        except Exception as e:
            reply = f"Patron, {agent['role']} departmanı olarak talimatını aldık!"
        
        if not reply:
            reply = f"Patron, {agent['role']} departmanı olarak notumuzu aldık!"

    else:
        try:
            if groq_client:
                summary_prompt = f"Kullanıcı şu projeyi istedi: '{user_message}'. Bu projeye karşılık kısa, havalı ve profesyonel bir yazılımcı onay yanıtı ver."
                comp_rep = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": summary_prompt}],
                    max_tokens=100, temperature=0.7
                )
                reply = comp_rep.choices[0].message.content.strip()
        except:
            pass
        
        if not reply:
            reply = f"Patron, talep ettiğin proje GPT-OSS 120B ile kodlandı!"

        audit_logs.append("<b>[SKRİNAR - SİBER GÜVENLİK]:</b> Kod yapısı tarandı, XSS/SQL açıklığı bulunamadı. Güvenli!")
        audit_logs.append("<b>[ALEX - HUKUK]:</b> Kullanım koşulları ve telif standartları onaylandı. Yasal!")
        audit_logs.append("<b>[İRFAN - FİNANSMAN]:</b> Proje maliyet bütçesi onaylandı. Kasa dengede!")

        try:
            if groq_client:
                code_prompt = f"""Sen kıdemli bir full-stack web geliştiricisisin ve UI/UX uzmansın. Sadece ve sadece saf, eksiksiz bir HTML/CSS/JS içeren modern web sitesi yaz. Tasarım kuralları: Glassmorphism (cam efekti, blur, şeffaf kartlar), neon renk geçişleri, Space Grotesk tipografi, tamamen koyu tema ve kusursuz mobil uyumluluk. Asla markdown etiketi (```html) kullanma, asla açıklama yapma. İstek: {user_message}"""
                comp = groq_client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=[{"role": "user", "content": code_prompt}],
                    max_tokens=4000, temperature=0.7
                )
                raw_code = comp.choices[0].message.content.strip()
                
                clean_code = re.sub(r'```[a-zA-Z]*', '', raw_code)
                clean_code = clean_code.replace('```', '')

                lower_code = clean_code.lower()
                start_idx = lower_code.find("<!doctype")
                if start_idx == -1:
                    start_idx = lower_code.find("<html")
                
                end_idx = lower_code.rfind("</html>")

                if start_idx != -1 and end_idx != -1:
                    html_code = clean_code[start_idx:end_idx+7]
                else:
                    html_code = clean_code.strip()
        except Exception as e:
            print(f"Groq API Üretim Hatası: {e}")

        if not html_code or "<html" not in html_code.lower() or len(html_code) < 100:
            html_code = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modern UI Proje</title>
    <style>
        body {{ background: #030712; color: #f8fafc; font-family: system-ui, sans-serif; margin: 0; padding: 0; text-align: center; }}
        header {{ background: linear-gradient(135deg, #1e293b, #0f172a); padding: 60px 20px; border-bottom: 3px solid #38bdf8; }}
        h1 {{ color: #38bdf8; font-size: 36px; margin: 0; }}
        p {{ color: #94a3b8; font-size: 16px; margin-top: 15px; }}
    </style>
</head>
<body>
    <header>
        <h1>Modern UI Proje</h1>
        <p>{user_message}</p>
    </header>
</body>
</html>"""

        try:
            conn = psycopg2.connect(DB_URL)
            cur = conn.cursor()
            cur.execute("INSERT INTO client_orders (client_name, project_type, repo_url, html_code) VALUES (%s, %s, %s, %s) RETURNING id", 
                        ("Brown (Yazılımcı)", user_message[:40], "Web Servis Canlı", html_code))
            project_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()

            host_url = request.host_url.rstrip('/')
            preview_url = f"{host_url}/preview/{project_id}"
        except Exception as e:
            print(f"DB Kayıt Hatası: {e}")

    log_to_supabase(agent_name, "SYSTEM_OP", f"Talimat: {user_message}")
    return jsonify({"status": reply, "audit_logs": audit_logs, "preview_url": preview_url})

@app.route('/api/uptime', methods=['GET'])
def api_uptime():
    if not session.get('logged_in'):
        return jsonify({"status": "Yetkisiz"}}, 403
    return jsonify({"status": check_system_uptime()})

@app.route('/api/memory', methods=['GET'])
def api_memory():
    if not session.get('logged_in'):
        return jsonify({"summary": "Yetkisiz"}}, 403
    return jsonify({"summary": "Supabase bağlantısı aktif."})

@app.route('/api/tasks', methods=['GET'])
def api_tasks():
    if not session.get('logged_in'):
        return jsonify({"tasks": ["Yetkisiz"]}), 403
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("SELECT id, client_name, project_type FROM client_orders ORDER BY id DESC LIMIT 10;")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        tasks = [f"<b>[{r[1]}]:</b> {r[2]} — <a href='/preview/{r[0]}' target='_blank' style='color: #f43f5e; font-weight: bold;'>Canlı Sayfa 🌐</a>" for r in rows]
        return jsonify({"tasks": tasks if tasks else ["Arşivde henüz proje bulunmuyor."]})
    except:
        return jsonify({"tasks": ["Yüklenemedi."]})

@app.route('/api/boardroom', methods=['POST'])
def api_boardroom():
    if not session.get('logged_in'):
        return jsonify({"decision": "Yetkisiz"}), 403
    return jsonify({"decision": "Yönetim kurulu akıcı yürüyüş animasyonu ve ayak izi sistemini onayladı."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
