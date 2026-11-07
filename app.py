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

# Veritabanı Tablolarını Oluşturma (Bağlantı Kontrolü)
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

# Ajan Kadromuz
employees = {
    "Marco": {"role": "Müşteri İlişkileri & Destek", "room": "Destek Odası", "color": "#3b82f6", "default": "Destek hattında..."},
    "Talisca": {"role": "Sipariş Takip & Operasyon", "room": "Operasyon Odası", "color": "#ef4444", "default": "Sipariş işliyor"},
    "Brown": {"role": "Yazılım Mühendisi", "room": "Yazılım Üssü", "color": "#10b981", "default": "Kod derleniyor..."},
    "Kante": {"role": "Pazarlama Uzmanı", "room": "Pazarlama Odası", "color": "#f59e0b", "default": "Kampanya kurguluyor"},
    "İrfan": {"role": "Finans & Trader", "room": "Finans Odası", "color": "#8b5cf6", "default": "Piyasayı tarıyor"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK Odası", "color": "#f97316", "default": "Mülakatta..."},
    "Alex": {"role": "Hukuk Danışmanı", "room": "Hukuk Bürosu", "color": "#14b8a6", "default": "Sözleşme inceliyor"},
    "Skrinar": {"role": "Siber Güvenlik", "room": "Güvenlik Odası", "color": "#64748b", "default": "Sistem taranıyor"},
    "Kerem": {"role": "Müşteri Başarı", "room": "Başarı Odası", "color": "#ec4899", "default": "Onboarding aktif"}
}

# Sadeleştirilmiş ve Şık Tasarımlı Arayüz
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Autonomous Command Center</title>
    <style>
        body { 
            background-color: #030712; 
            color: #f8fafc; 
            font-family: 'Inter', system-ui, -apple-system, sans-serif; 
            margin: 0; 
            padding: 20px; 
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        header {
            width: 100%;
            max-width: 900px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #0f172a;
            padding: 12px 20px;
            border-radius: 8px;
            border: 1px solid #1e293b;
            margin-bottom: 20px;
        }
        .badge { background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: 600; }
        
        .grid-container {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            width: 100%;
            max-width: 900px;
            margin-bottom: 20px;
        }
        .agent-card {
            background: #0f172a;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .agent-card:hover { border-color: #38bdf8; transform: translateY(-2px); }
        .agent-title { font-size: 13px; font-weight: bold; margin-bottom: 5px; display: flex; align-items: center; gap: 8px; }
        .agent-role { font-size: 11px; color: #94a3b8; }
        .agent-status { font-size: 11px; color: #4ade80; margin-top: 8px; font-style: italic; }

        .control-panel {
            width: 100%;
            max-width: 900px;
            background: #0f172a;
            border: 1px solid #1e293b;
            padding: 15px;
            border-radius: 8px;
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        select, input[type="text"] {
            background: #1e293b;
            color: #fff;
            border: 1px solid #334155;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
        }
        input[type="text"] { flex-grow: 1; }
        .btn {
            background: #0284c7;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
        }
        .btn:hover { background: #0369a1; }

        .terminal {
            width: 100%;
            max-width: 900px;
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 12px;
            height: 150px;
            overflow-y: auto;
            color: #4ade80;
        }
        .log-item { margin-bottom: 6px; border-bottom: 1px dashed rgba(255,255,255,0.05); padding-bottom: 4px; }
    </style>
</head>
<body>

    <header>
        <div>🏢 <b>E-TRADE PRO</b> // AUTONOMOUS HQ</div>
        <div>
            <span class="badge">CEO: MERTCAN</span>
            <span class="badge" style="background: #064e3b; color: #34d399;">SUPABASE AKTİF</span>
        </div>
    </header>

    <!-- Sadeleştirilmiş Grid Görünümü -->
    <div class="grid-container">
        {% for name, data in employees.items() %}
        <div class="agent-card" onclick="selectAgent('{{ name }}')">
            <div class="agent-title">
                <span style="width: 10px; height: 10px; background: {{ data.color }}; border-radius: 50%;"></span>
                {{ name }}
            </div>
            <div class="agent-role">{{ data.role }}</div>
            <div class="agent-status" id="status-{{ name }}">{{ data.default }}</div>
        </div>
        {% endfor %}
    </div>

    <!-- Kontrol Paneli -->
    <div class="control-panel">
        <select id="agent-select">
            {% for name, data in employees.items() %}
            <option value="{{ name }}">{{ name }} ({{ data.role }})</option>
            {% endfor %}
        </select>
        <input type="text" id="ceo-message" placeholder="Ajana talimat ver veya piyasa sor..." onkeypress="checkEnter(event)">
        <button class="btn" onclick="sendDirectMessage()">EMİR GÖNDER</button>
    </div>

    <!-- Canlı Otonom Terminal -->
    <div class="terminal" id="terminal-logs">
        <div class="log-item">[SYSTEM]: Otonom veritabanı ve arka plan döngüsü devrede. Ajanlar göreve hazır.</div>
    </div>

    <script>
        const terminal = document.getElementById('terminal-logs');

        function appendLog(text) {
            const time = new Date().toLocaleTimeString();
            const div = document.createElement('div');
            div.className = 'log-item';
            div.innerHTML = `[${time}] ${text}`;
            terminal.prepend(div);
        }

        function selectAgent(name) {
            document.getElementById('agent-select').value = name;
            appendLog(`> [SEÇİM]: ${name} odak noktasına alındı.`);
        }

        function checkEnter(event) {
            if (event.key === 'Enter') sendDirectMessage();
        }

        function sendDirectMessage() {
            const agent = document.getElementById('agent-select').value;
            const input = document.getElementById('ceo-message');
            const message = input.value.trim();
            if (!message) return;

            appendLog(`> [CEO -> ${agent}]: "${message}"`);
            input.value = "";

            fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ agent: agent, message: message })
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('status-' + agent).innerText = data.short_status;
                appendLog(`> [<b>${agent}</b>]: "${data.status}"`);
                if (data.handoff) {
                    appendLog(`> [OTONOM PASLAŞMA]: ${data.handoff}`);
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

# Otonom Arka Plan Döngüsü (Background Autonomous Loop)
def autonomous_background_worker():
    """Ajanların sen sormadan arka planda periyodik olarak çalışmasını sağlayan döngü"""
    while True:
        time.sleep(180) # Her 3 dakikada bir otonom tetiklenme
        try:
            live_market = fetch_crypto_price()
            log_to_supabase("İrfan", "AUTONOMOUS_SCAN", f"Periyodik Piyasa Taraması: {live_market}")
        except Exception as e:
            print(f"Otonom İşçi Hatası: {e}")

# Arka plan işçisini başlatıyoruz
threading.Thread(target=autonomous_background_worker, daemon=True).start()

def generate_agent_reply(agent_name, role, user_message):
    try:
        extra_context = ""
        handoff_text = ""
        
        if any(w in user_message.lower() for w in ["btc", "bitcoin", "eth", "ethereum", "fiyat", "piyasa"]):
            extra_context = f"\n[CANLI PİYASA VERİSİ]: {fetch_crypto_price()}\n"

        # Ajanlar Arası İletişim / Paslaşma Mantığı (Agent Handoff)
        if "kod" in user_message.lower() or "yazılım" in user_message.lower():
            handoff_text = "Not: İşlem güvenliği için konu Siber Güvenlik Uzmanı Skrinar'a bildirildi."
        elif "sözleşme" in user_message.lower() or "hukuk" in user_message.lower():
            handoff_text = "Not: İnsan Kaynakları yöneticisi İsmail bilgilendirildi."

        system_prompt = (
            f"Sen E-Trade Pro şirketinde {role} olarak çalışan {agent_name} adında üst düzey bir uzmansın. "
            f"Patronun Mertcan sana yazdı: '{user_message}'.\n"
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
        
        # Supabase'e kaydet
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
        "short_status": status_text[:25] + "..." if len(status_text) > 25 else status_text,
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
