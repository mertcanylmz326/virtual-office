import os
import time
import threading
import requests
import psycopg2
from flask import Flask, render_template_string, jsonify, request
from groq import Groq

app = Flask(__name__)

# Supabase Veritabanı Bilgileri
DB_URL = "postgresql://postgres.prphsmgaujdwrqqdmmrd:yaheroyamero@aws-0-eu-west-1.pooler.supabase.com:5432/postgres"

# Groq API Bağlantısı
GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Veritabanı Tablosunu Oluşturma
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
        """)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB Hatası: {e}")

init_db()

# Ajan Kadromuz ve Konumları
employees = {
    "Marco": {"role": "Müşteri İlişkileri & Destek", "room": "Destek Odası", "home_x": 90, "home_y": 70, "color": "#3b82f6", "default": "Destek hattında..."},
    "Talisca": {"role": "Sipariş Takip & Operasyon", "room": "Operasyon Odası", "home_x": 390, "home_y": 70, "color": "#ef4444", "default": "Sipariş işliyor"},
    "Brown": {"role": "Yazılım Mühendisi", "room": "Yazılım Üssü", "home_x": 690, "home_y": 70, "color": "#10b981", "default": "Kod derleniyor..."},
    "Kante": {"role": "Pazarlama Uzmanı", "room": "Pazarlama Odası", "home_x": 90, "home_y": 200, "color": "#f59e0b", "default": "Kampanya kurguluyor"},
    "İrfan": {"role": "Finans & Trader", "room": "Finans Odası", "home_x": 390, "home_y": 200, "color": "#8b5cf6", "default": "Piyasayı tarıyor"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK Odası", "home_x": 690, "home_y": 200, "color": "#f97316", "default": "Mülakatta..."},
    "Alex": {"role": "Hukuk Danışmanı", "room": "Hukuk Bürosu", "home_x": 90, "home_y": 330, "color": "#14b8a6", "default": "Sözleşme inceliyor"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik Odası", "home_x": 390, "home_y": 330, "color": "#64748b", "default": "Sistem taranıyor"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Başarı Odası", "home_x": 690, "home_y": 330, "color": "#ec4899", "default": "Onboarding aktif"}
}

# Orijinal Harika Görsel Ofis Tasarımı + Supabase & Otonom Arka Plan
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Autonomous Private Offices</title>
    <style>
        body { 
            background-color: #05070b; 
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
        .top-btn { background: #1e293b; color: #38bdf8; border: 1px solid #334155; padding: 4px 10px; border-radius: 4px; font-weight: bold; }

        #office-floor { 
            position: relative; 
            width: 960px; 
            height: 480px; 
            margin: 10px auto; 
            background-color: #1a120b;
            background-image: 
                linear-gradient(90deg, rgba(255,255,255,0.04) 2px, transparent 2px),
                linear-gradient(rgba(0,0,0,0.3) 2px, transparent 2px);
            background-size: 60px 30px;
            border: 6px solid #1e293b; 
            border-radius: 10px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.95); 
            overflow: hidden;
        }

        .private-room {
            position: absolute;
            border: 3px solid #475569;
            background: rgba(30, 41, 59, 0.75);
            border-radius: 6px;
            width: 280px;
            height: 115px;
        }
        .room-label {
            position: absolute;
            font-size: 8px;
            color: #38bdf8;
            top: 4px;
            left: 8px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .room-door {
            position: absolute;
            right: 0;
            top: 40px;
            width: 8px;
            height: 35px;
            background: #78350f;
            border: 1px solid #451a03;
        }

        .desk { position: absolute; width: 45px; height: 24px; background: #1c1917; border: 2px solid #44403c; border-radius: 3px; }
        .pc-monitor { position: absolute; width: 16px; height: 9px; background: #38bdf8; top: 3px; left: 14px; border-radius: 2px; box-shadow: 0 0 6px #38bdf8; }
        
        .ceo-hq {
            position: absolute;
            left: 440px;
            top: 400px;
            width: 80px;
            height: 65px;
            background: radial-gradient(circle, #dc2626 0%, #7f1d1d 100%);
            border: 3px solid #fff;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 9px;
            font-weight: bold;
            box-shadow: 0 0 25px rgba(220, 38, 38, 0.9);
            z-index: 50;
        }

        .agent { 
            position: absolute; 
            width: 45px; 
            height: 55px; 
            cursor: pointer; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            transition: left 2.2s ease, top 2.2s ease;
            z-index: 30;
        }
        
        .robot-sprite {
            width: 28px;
            height: 28px;
            background-color: #18181b;
            border: 2px solid;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 13px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.8);
            animation: robotStep 0.4s infinite alternate;
        }

        .agent-name {
            font-size: 7px;
            font-weight: bold;
            background: rgba(15, 23, 42, 0.95);
            padding: 1px 3px;
            border-radius: 3px;
            margin-top: 2px;
            white-space: nowrap;
            border: 1px solid #475569;
        }
        
        .speech-bubble {
            position: absolute;
            top: -22px;
            background: #f8fafc;
            color: #0f172a;
            font-size: 6px;
            font-weight: bold;
            padding: 2px 5px;
            border-radius: 4px;
            white-space: nowrap;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            pointer-events: none;
            max-width: 110px;
        }

        .agent:hover { transform: scale(1.3); z-index: 100; }

        @keyframes robotStep {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-4px) rotate(2deg); }
        }

        #command-panel {
            margin: 10px auto;
            width: 950px;
            background: #0f172a;
            border: 2px solid #334155;
            padding: 10px;
            border-radius: 6px;
            display: flex;
            gap: 10px;
            align-items: center;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        select, input[type="text"] {
            background: #1e293b;
            color: #fff;
            border: 1px solid #475569;
            padding: 6px 10px;
            border-radius: 4px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 11px;
        }
        input[type="text"] { flex-grow: 1; }
        .send-btn {
            background: #0284c7;
            color: #fff;
            border: none;
            padding: 6px 15px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
        }
        .send-btn:hover { background: #0369a1; }

        #activity-terminal {
            margin: 0 auto 20px auto;
            width: 950px;
            background: #020617;
            border: 2px solid #334155;
            border-radius: 6px;
            text-align: left;
            box-shadow: 0 4px 15px rgba(0,0,0,0.8);
            overflow: hidden;
        }
        .terminal-header {
            background: #0f172a;
            padding: 6px 12px;
            font-size: 10px;
            color: #38bdf8;
            border-bottom: 1px solid #1e293b;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
        }
        .terminal-body {
            padding: 10px;
            height: 100px;
            overflow-y: auto;
            font-size: 10px;
            color: #4ade80;
            line-height: 1.4;
        }
        .log-line { margin-bottom: 4px; border-bottom: 1px dashed rgba(255,255,255,0.05); padding-bottom: 2px; }
    </style>
</head>
<body>

    <div id="game-topbar">
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - AUTONOMOUS PRIVATE OFFICES</div>
        <div>
            <span class="top-btn">CEO: MERTCAN</span>
            <span class="top-btn" style="color: #34d399;">SUPABASE & OTONOM AKTİF</span>
        </div>
    </div>

    <!-- Orijinal Müstakil Odalı Ofis Haritası -->
    <div id="office-floor">
        <div class="private-room" style="left: 20px; top: 15px;"><div class="room-label">MARCO (DESTEK)</div><div class="room-door"></div></div>
        <div class="private-room" style="left: 340px; top: 15px;"><div class="room-label">TALİSCA (OPERASYON)</div><div class="room-door"></div></div>
        <div class="private-room" style="left: 660px; top: 15px;"><div class="room-label">BROWN (YAZILIM)</div><div class="room-door"></div></div>
        
        <div class="private-room" style="left: 20px; top: 145px;"><div class="room-label">KANTE (PAZARLAMA)</div><div class="room-door"></div></div>
        <div class="private-room" style="left: 340px; top: 145px;"><div class="room-label">İRFAN (FİNANS & TRADER)</div><div class="room-door"></div></div>
        <div class="private-room" style="left: 660px; top: 145px;"><div class="room-label">İSMAİL (İK)</div><div class="room-door"></div></div>

        <div class="private-room" style="left: 20px; top: 275px;"><div class="room-label">ALEX (HUKUK)</div><div class="room-door"></div></div>
        <div class="private-room" style="left: 340px; top: 275px;"><div class="room-label">SKRİNAR (SİBER)</div><div class="room-door"></div></div>
        <div class="private-room" style="left: 660px; top: 275px;"><div class="room-label">KEREM (BAŞARI)</div><div class="room-door"></div></div>

        <div class="desk" style="left: 135px; top: 60px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 455px; top: 60px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 775px; top: 60px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 135px; top: 190px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 455px; top: 190px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 775px; top: 190px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 135px; top: 320px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 455px; top: 320px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 775px; top: 320px;"><div class="pc-monitor"></div></div>

        <div class="ceo-hq">
            <span>👑 SEN</span>
            <span style="font-size: 7px; color: #fca5a5;">CEO OFİSİ</span>
        </div>

        {% for name, data in employees.items() %}
        <div class="agent" id="agent-{{ name }}" style="left: {{ data.home_x }}px; top: {{ data.home_y }}px;" 
             onclick="selectAgent('{{ name }}')">
            <div class="speech-bubble" id="bubble-{{ name }}">{{ data.default }}</div>
            <div class="robot-sprite" style="border-color: {{ data.color }};">🤖</div>
            <div class="agent-name" style="color: {{ data.color }};">{{ name }}</div>
        </div>
        {% endfor %}
    </div>

    <!-- Komuta Paneli -->
    <div id="command-panel">
        <select id="agent-select">
            {% for name, data in employees.items() %}
            <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
            {% endfor %}
        </select>
        <input type="text" id="ceo-message" placeholder="Stratejik komut ver veya piyasa sor..." onkeypress="checkEnter(event)">
        <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ AUTONOMOUS OPERATIONS TERMINAL</span>
            <span style="color: #34d399;">● LIVE SYNCED</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Supabase veritabanı ve otonom arka plan işçisi devreye girdi.</div>
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
            appendLog(`> [SEÇİM]: ${name} odasına bağlanıldı.`);
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        function sendDirectMessage() {
            const agentName = document.getElementById('agent-select').value;
            const messageInput = document.getElementById('ceo-message');
            const messageText = messageInput.value.trim();
            if (!messageText) return;

            appendLog(`> [KOMUT]: "${messageText}"`);
            messageInput.value = "";

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: agentName, message: messageText })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('bubble-' + agentName).innerText = data.short_status;
                appendLog(`> [<b>${agentName}</b>]: "${data.status}"`);
                if (data.handoff) {
                    appendLog(`> [PASLAŞMA]: ${data.handoff}`);
                }
            });
        }
    </script>
</body>
</html>
"""

def log_to_supabase(agent_name, action_type, content):
    """Yapılan işlemleri Supabase veritabanına kaydeder"""
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO agent_logs (agent_name, action_type, content) VALUES (%s, %s, %s)", (agent_name, action_type, content))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Log Kayıt Hatası: {e}")

def fetch_crypto_price():
    """Canlı Kripto Verisi Çekme Motoru"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        res = requests.get(url, timeout=3).json()
        btc = res.get("bitcoin", {}).get("usd", "N/A")
        eth = res.get("ethereum", {}).get("usd", "N/A")
        return f"BTC: ${btc} USD | ETH: ${eth} USD"
    except:
        return "Piyasa verisi geçici olarak alınamadı."

# Otonom Arka Plan Döngüsü
def autonomous_background_worker():
    while True:
        time.sleep(180) # Her 3 dakikada bir otomatik çalışma
        try:
            live_market = fetch_crypto_price()
            log_to_supabase("İrfan", "AUTONOMOUS_SCAN", f"Periyodik Piyasa Taraması: {live_market}")
        except Exception as e:
            print(f"Otonom İşçi Hatası: {e}")

threading.Thread(target=autonomous_background_worker, daemon=True).start()

def generate_agent_reply(agent_name, role, user_message):
    try:
        extra_context = ""
        handoff_text = ""
        
        if any(w in user_message.lower() for w in ["btc", "bitcoin", "eth", "ethereum", "fiyat", "piyasa"]):
            extra_context = f"\n[GÜNCEL PİYASA VERİSİ]: {fetch_crypto_price()}\n"

        if "kod" in user_message.lower() or "yazılım" in user_message.lower():
            handoff_text = "Siber Güvenlik Uzmanı Skrinar güvenlik testi için bilgilendirildi."
        elif "sözleşme" in user_message.lower() or "hukuk" in user_message.lower():
            handoff_text = "İnsan Kaynakları yöneticisi İsmail onay için bilgilendirildi."

        system_prompt = (
            f"Sen E-Trade Pro şirketinde {role} olarak çalışan {agent_name} adında üst düzey bir uzmansın. "
            f"Kendi müstakil odandasın. Patronun Mertcan sana yazdı: '{user_message}'.\n"
            f"{extra_context}\n"
            f"Profesyonel, net, stratejik ve doğrudan konuya odaklanan bir rapor sun. Kısa ve öz ol."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=messages,
            max_tokens=200,
            temperature=0.7
        )
        
        reply = completion.choices[0].message.content.strip('"').strip() if completion.choices else "Görev başında."
        
        log_to_supabase(agent_name, "CHAT_RESPONSE", f"Soru: {user_message} | Cevap: {reply}")

        return reply, handoff_text
    except Exception as e:
        return f"Sistem hatası oluştu.", ""

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

    status_text, handoff = generate_agent_reply(agent_name, agent['role'], user_message)

    return jsonify({
        "status": status_text, 
        "short_status": status_text[:22] + "..." if len(status_text) > 22 else status_text,
        "handoff": handoff
    })

@app.route('/v1/chat/completions', methods=['POST'])
def v1_chat_completions():
    req_data = request.json
    incoming_messages = req_data.get('messages', [])
    last_user_msg = incoming_messages[-1].get('content', 'Selam') if incoming_messages else "Selam"

    target_agent = "İrfan"
    for name in employees.keys():
        if name.lower() in last_user_msg.lower():
            target_agent = name
            break

    agent = employees[target_agent]
    reply_text, _ = generate_agent_reply(target_agent, agent['role'], last_user_msg)

    return jsonify({
        "id": "chatcmpl-etrade",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "openai/gpt-oss-20b",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": f"[{target_agent} - {agent['role']}]: {reply_text}"},
            "finish_reason": "stop"
        }]
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
