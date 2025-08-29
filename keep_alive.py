from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>🔥 FF H4CK Bot is Running! 🔥</h1>
    <p>💀 Free Fire Ultimate Hacks Bot</p>
    <p>⚡ Status: Online and Ready</p>
    <p>🛡️ Anti-Ban Protection Enabled</p>
    <style>
        body { 
            background-color: #1a1a1a; 
            color: #ff6600; 
            font-family: Arial, sans-serif; 
            text-align: center; 
            padding: 50px; 
        }
        h1 { color: #ff3300; }
    </style>
    """

@app.route('/status')
def status():
    return {"status": "online", "bot": "FF H4CK Bot", "version": "1.0"}

def run():
    app.run(host='0.0.0.0', port=5000)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()