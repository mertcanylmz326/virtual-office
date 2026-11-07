import os
from flask import Flask, render_template_string, jsonify, request
from groq import Groq

app = Flask(__name__)

# Groq API Anahtarın ve Canlı Bağlantı
GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Dinamik Çalışan Kadromuz
employees = {
    "Marco": {"role": "Müşteri İlişkileri & Destek", "room": "Destek Odası", "home_x": 90, "home_y": 70, "color": "#3b82f6", "default": "Destek hattında..."},
    "Talisca": {"role": "Sipariş Takip & Operasyon", "room": "Operasyon Odası", "home_x": 270, "home_y": 70, "color": "#ef4444", "default": "Sipariş işliyor"},
    "Brown": {"role": "Yazılım Mühendisi", "room": "Yazılım Üssü", "home_x": 560, "home_y": 70, "color": "#10b981", "default": "Kod derleniyor..."},
    "Kante": {"role": "Pazarlama & Büyüme Uzmanı", "room": "Pazarlama Odası", "home_x": 740, "home_y": 70, "color": "#f59e0b", "default": "Kampanya kurguluyor"},
    "İrfan": {"role": "Finans & Trader / Kripto Uzmanı", "room": "Finans Odası", "home_x": 820, "home_y": 330, "color": "#8b5cf6", "default": "Bütçe kontrolü"},
    "İsmail": {"role": "İnsan Kaynakları", "room": "İK Odası", "home_x": 90, "home_y": 330, "color": "#f97316", "default": "Mülakatta..."},
    "Alex": {"role": "Hukuk & Mevzuat Danışmanı", "room": "Hukuk Bürosu", "home_x": 270, "home_y": 330, "color": "#14b8a6", "default": "Sözleşme inceliyor"},
    "Skrinar": {"role": "Siber Güvenlik Uzmanı", "room": "Güvenlik Odası", "home_x": 530, "home_y": 330, "color": "#64748b", "default": "Sistem taranıyor"},
    "Kerem": {"role": "Müşteri Başarı Uzmanı", "room": "Müşteri Başarı Odası", "home_x": 670, "home_y": 330, "color": "#ec4899", "default": "Onboarding aktif"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>E-Trade Pro - Ultimate Command Center</title>
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
            width: 920px; 
            height: 480px; 
            margin: 10px auto; 
            background-color: #2c1d11;
            background-image: 
                linear-gradient(90deg, rgba(255,255,255,0.06) 2px, transparent 2px),
                linear-gradient(rgba(0,0,0,0.35) 2px, transparent 2px);
            background-size: 60px 30px;
            border: 6px solid #1e293b; 
            border-radius: 10px; 
            box-shadow: 0 25px 50px rgba(0,0,0,0.95); 
            overflow: hidden;
        }

        .hq-room {
            position: absolute;
            border: 4px solid #334155;
            background: rgba(30, 20, 14, 0.92);
            border-radius: 6px;
        }
        .hq-room-title {
            position: absolute;
            font-size: 7px;
            color: #94a3b8;
            top: 4px;
            left: 6px;
            font-weight: bold;
            text-transform: uppercase;
        }

        .hq-door {
            position: absolute;
            background: #78350f;
            border: 2px solid #451a03;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 6px;
            color: #fde68a;
            font-weight: bold;
        }

        .desk { position: absolute; width: 45px; height: 24px; background: #1c1917; border: 2px solid #44403c; border-radius: 3px; }
        .pc-monitor { position: absolute; width: 16px; height: 9px; background: #38bdf8; top: 3px; left: 14px; border-radius: 2px; box-shadow: 0 0 6px #38bdf8; }
        
        .lounge-area {
            position: absolute;
            left: 410px;
            top: 200px;
            width: 100px;
            height: 80px;
            background: rgba(14, 165, 233, 0.12);
            border: 2px dashed #0284c7;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 8px;
            color: #38bdf8;
            font-weight: bold;
        }

        .ceo-hq {
            position: absolute;
            left: 425px;
            top: 105px;
            width: 70px;
            height: 70px;
            background: radial-gradient(circle, #dc2626 0%, #7f1d1d 100%);
            border: 3px solid #fff;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            font-size: 10px;
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
            width: 30px;
            height: 30px;
            background-color: #18181b;
            border: 2px solid;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
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
            top: -24px;
            background: #f8fafc;
            color: #0f172a;
            font-size: 6px;
            font-weight: bold;
            padding: 2px 5px;
            border-radius: 4px;
            white-space: nowrap;
            box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            pointer-events: none;
            max-width: 120px;
        }

        .agent:hover { transform: scale(1.3); z-index: 100; }

        @keyframes robotStep {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-4px) rotate(2deg); }
        }

        #command-panel {
            margin: 10px auto;
            width: 910px;
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
            width: 910px;
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
            height: 110px;
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
        <div style="font-weight: bold; color: #38bdf8;">🏢 E-TRADE PRO HQ - UNIFIED BRIDGE</div>
        <div>
            <span class="top-btn">CEO: MERTCAN</span>
            <span class="top-btn" style="color: #34d399;">WEBUI / CHAT SYNC</span>
        </div>
    </div>

    <!-- Ofis Haritası -->
    <div id="office-floor">
        <div class="hq-room" style="left: 15px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">MARCO (DESTEK)</div></div>
        <div class="hq-room" style="left: 225px; top: 15px; width: 195px; height: 215px;"><div class="hq-room-title">TALİSCA (SİPARİŞ)</div></div>
        <div class="hq-room" style="left: 495px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">BROWN (YAZILIM)</div></div>
        <div class="hq-room" style="left: 705px; top: 15px; width: 200px; height: 215px;"><div class="hq-room-title">KANTE (PAZARLAMA)</div></div>
        
        <div class="hq-room" style="left: 15px; top: 255px; width: 200px; height: 215px;"><div class="hq-room-title">İSMAİL (İK)</div></div>
        <div class="hq-room" style="left: 225px; top: 255px; width: 195px; height: 215px;"><div class="hq-room-title">ALEX (HUKUK)</div></div>
        <div class="hq-room" style="left: 495px; top: 255px; width: 150px; height: 215px;"><div class="hq-room-title">SKRİNAR (SİBER)</div></div>
        <div class="hq-room" style="left: 655px; top: 255px; width: 115px; height: 215px;"><div class="hq-room-title">KEREM (BAŞARI)</div></div>
        <div class="hq-room" style="left: 780px; top: 255px; width: 125px; height: 215px;"><div class="hq-room-title">İRFAN (FİNANS)</div></div>

        <div class="hq-door" style="left: 425px; top: 110px; width: 65px; height: 15px;">KAPI</div>
        <div class="hq-door" style="left: 425px; top: 350px; width: 65px; height: 15px;">KAPI</div>
        <div class="lounge-area">☕ ORTAK MOLA</div>

        <div class="desk" style="left: 90px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 295px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 570px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 770px; top: 75px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 90px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 295px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 545px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 690px; top: 315px;"><div class="pc-monitor"></div></div>
        <div class="desk" style="left: 820px; top: 315px;"><div class="pc-monitor"></div></div>

        <div class="ceo-hq">
            <span>👑 SEN</span>
            <span style="font-size: 7px; color: #fca5a5;">CEO</span>
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
        <input type="text" id="ceo-message" placeholder="Komut ver (Örn: Yeni eleman al: Cem, rolü: Destek)..." onkeypress="checkEnter(event)">
        <button class="send-btn" onclick="sendDirectMessage()">GÖNDER</button>
    </div>

    <!-- Terminal -->
    <div id="activity-terminal">
        <div class="terminal-header">
            <span>⚡ UNIFIED BRIDGE OPERATIONS TERMINAL</span>
            <span style="color: #34d399;">● READY</span>
        </div>
        <div class="terminal-body" id="terminal-logs">
            <div class="log-line">[SYSTEM]: Harici chat istemcisi ve ofis köprüsü kuruldu.</div>
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
                if (data.is_hr_action) {
                    appendLog(`> [İK]: ${data.status}`);
                    setTimeout(() => location.reload(), 1500);
                } else {
                    document.getElementById('bubble-' + agentName).innerText = data.short_status;
                    appendLog(`> [<b>${agentName}</b>]: "${data.status}"`);
                }
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, employees=employees)

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    agent_name = data.get('agent')
    user_message = data.get('message')

    # HR Komut Kontrolü
    if "yeni eleman al" in user_message.lower() or "eleman ekle" in user_message.lower():
        try:
            parts = user_message.split(":")
            new_name = "Agent"
            new_role = "Personel"
            if len(parts) > 1:
                sub = parts[1].split(",")
                new_name = sub[0].strip().split()[0]
                if len(sub) > 1: new_role = sub[1].replace("rolü", "").replace(":", "").strip()
            
            if new_name not in employees:
                employees[new_name] = {"role": new_role, "room": "Ofis", "home_x": 450, "home_y": 180, "color": "#ec4899", "default": "Yeni görevde!"}
                return jsonify({"status": f"{new_name} ({new_role}) işe alındı!", "short_status": "İşe alındı", "is_hr_action": True})
        except: pass

    if agent_name not in employees: agent_name = "İrfan" # Varsayılan
    agent = employees[agent_name]

    try:
        messages = [
            {"role": "system", "content": f"Sen E-Trade Pro şirketinde {agent['role']} olarak çalışan {agent_name} adında bir yapay zeka ajanısın. Patronun Mertcan'a net, profesyonel ve kısa yanıt ver."},
            {"role": "user", "content": user_message}
        ]
        completion = groq_client.chat.completions.create(model="openai/gpt-oss-20b", messages=messages, max_tokens=120, temperature=0.7)
        status_text = completion.choices[0].message.content.strip('"').strip() if completion.choices else "Tamam patron."
        return jsonify({"status": status_text, "short_status": status_text[:22] + "...", "is_hr_action": False})
    except:
        return jsonify({"status": "Komut işlendi.", "short_status": "Tamam", "is_hr_action": False})

# --- DIŞARIDAKİ CHAT UYGULAMASI (Open WebUI vb.) İÇİN OPENAI UYUMLU ENDPOINT ---
@app.route('/v1/chat/completions', methods=['POST'])
def v1_chat_completions():
    req_data = request.json
    incoming_messages = req_data.get('messages', [])
    
    # Kullanıcının son mesajını al
    last_user_msg = "Selam"
    if incoming_messages:
        last_user_msg = incoming_messages[-1].get('content', 'Selam')

    # Mesaj içinde hangi ajana hitap edildiğini bulmaya çalışalım (Örn: "Selam İsmail", "İrfan Bitcoin ne kadar?")
    target_agent = "İrfan" # Varsayılan trader/uzman
    for name in employees.keys():
        if name.lower() in last_user_msg.lower():
            target_agent = name
            break

    agent = employees[target_agent]

    try:
        system_prompt = f"Sen E-Trade Pro şirketinde {agent['role']} olarak çalışan {target_agent} adında bir yapay zeka ajanısın. Patronun Mertcan sana dışarıdaki chat panelinden yazdı. Ona profesyonel, net ve nokta atışı yanıt ver."
        
        full_messages = [{"role": "system", "content": system_prompt}] + incoming_messages

        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=full_messages,
            max_tokens=150,
            temperature=0.7
        )
        
        reply_text = completion.choices[0].message.content if completion.choices else "Emredersiniz patron."

        # OpenAI formatında yanıt dönüyoruz ki harici chat uygulaması patlamasın!
        return jsonify({
            "id": "chatcmpl-etrade",
            "object": "chat.completion",
            "created": 1700000000,
            "model": "openai/gpt-oss-20b",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"[{target_agent} - {agent['role']}]: {reply_text}"
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20}
        })
    except Exception as e:
        return jsonify({
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": f"[Sistem Hatası]: {str(e)}"},
                "finish_reason": "stop"
            }]
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
