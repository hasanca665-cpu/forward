# forward_perfect.py
from telethon import TelegramClient, events, Button
import asyncio, json, re, os
import requests
import threading
import time
import random
from flask import Flask

# === Flask App for Web Service ===
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Telegram Forward Bot is Running!"

@app.route('/health')
def health():
    return "✅ Bot is healthy and running!"

# === CONFIG ===
api_id = 24742957
api_hash = "40d421e05a414534910ebc0998f97c10"
SOURCE = 2818830065
TARGET = "cucuucugrggfd"
SESSION_FILE = 'session.json'
COUNTRY_FILE = 'countries.json'

# Keep-alive configuration
KEEP_ALIVE_URL = "https://forward-45n9.onrender.com"  # CHANGE THIS

client = TelegramClient(SESSION_FILE, api_id, api_hash)

# === Enhanced keep-alive system ===
def ping_server():
    try:
        response = requests.get(KEEP_ALIVE_URL, timeout=10)
        print(f'🔄 Keep-alive ping sent: {response.status_code}')
        return True
    except Exception as e:
        print(f'⚠️ Keep-alive ping failed: {e}')
        return False

def keep_alive_worker():
    """Main keep-alive worker that runs every 5 minutes"""
    while True:
        ping_server()
        time.sleep(300)  # 5 minutes

def random_ping_worker():
    """Additional random pings to avoid pattern detection"""
    while True:
        random_time = random.randint(300, 600)  # 5-10 minutes
        time.sleep(random_time)
        ping_server()

def start_keep_alive():
    """Start all keep-alive systems"""
    # Main ping every 5 minutes
    main_thread = threading.Thread(target=keep_alive_worker, daemon=True)
    main_thread.start()
    
    # Random ping system
    random_thread = threading.Thread(target=random_ping_worker, daemon=True)
    random_thread.start()
    
    # Immediate ping on startup
    threading.Timer(30, ping_server).start()
    
    print("🚀 Keep-alive system started! Bot will run 24/7")

# === Load/save country status ===
def load_countries():
    if not os.path.exists(COUNTRY_FILE):
        return {}
    with open(COUNTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

def save_countries(data):
    with open(COUNTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

countries = load_countries()

# === Extract country name ===
def extract_country(text):
    match = re.search(r"([🇦-🇿]{1,2}\s*[A-Za-z]+)", text)
    if match:
        return match.group(1).strip()
    return None

# === Commands ===
@client.on(events.NewMessage(pattern=r'^/list'))
async def list_countries(event):
    if not countries:
        await event.reply("❌ এখনো কোনো country detect হয়নি।")
        return
    
    # Create message with clickable country names
    msg = "🌍 **Country List:**\n\n"
    for c, status in countries.items():
        # Make country name clickable to copy
        status_icon = '🟢' if status else '🔴'
        msg += f"`{c}`: {status_icon} {'ON' if status else 'OFF'}\n"
    
    msg += "\nℹ️ **Country name-এ ক্লিক করলে automatically copy হবে**"
    
    await event.reply(msg)

@client.on(events.NewMessage(pattern=r'^/on (.+)'))
async def on_country(event):
    name = event.pattern_match.group(1).strip()
    if name in countries:
        countries[name] = True
        save_countries(countries)
        await event.reply(f"✅ {name} forwarding **ON** করা হলো।")
    else:
        await event.reply("❌ Country list এ এই নামটা নেই।")

@client.on(events.NewMessage(pattern=r'^/off (.+)'))
async def off_country(event):
    name = event.pattern_match.group(1).strip()
    if name in countries:
        countries[name] = False
        save_countries(countries)
        await event.reply(f"🚫 {name} forwarding **OFF** করা হলো।")
    else:
        await event.reply("❌ Country list এ এই নামটা নেই。")

# === Message Handler ===
@client.on(events.NewMessage(chats=SOURCE))
async def message_handler(event):
    text = event.raw_text

    # skip unwanted welcome text
    if "Hey there Asad shah" in text:
        return

    # detect country
    country = extract_country(text)
    if not country:
        return

    # auto add new country but OFF by default
    if country not in countries:
        countries[country] = False
        save_countries(countries)
        print(f"🆕 Detected new country (default OFF): {country}")

    if not countries.get(country, False):
        print(f"⏸️ Skipped {country} (OFF)")
        return

    try:
        # Create buttons that will definitely show
        buttons = [
            [Button.url("🔗 Join Channel", "https://t.me/Seven1telTNE")],
            [Button.url("👤 Contact Admin", "https://t.me/notfound_errorx")]
        ]

        # Send original message + buttons together
        await client.send_message(
            TARGET,
            message=event.message.message,
            formatting_entities=event.message.entities,
            buttons=buttons,
            link_preview=False
        )
        print(f"✅ Forwarded ({country}) with working buttons.")
    except Exception as e:
        print(f"❌ Forward failed ({country}): {e}")

# === Telegram Bot Startup ===
async def start_telegram_bot():
    await client.start()
    me = await client.get_me()
    print(f"🤖 Logged in as @{me.username}")
    print("🎯 Forwarding bot active and perfect.")
    print("⏰ 24/7 Keep-alive system: ACTIVE")
    print("🚀 Bot is now running superfast!\n")
    await client.run_until_disconnected()

# === Main Function ===
def main():
    # Start keep-alive system
    start_keep_alive()
    
    # Start Telegram bot in a separate thread
    telegram_thread = threading.Thread(
        target=lambda: asyncio.run(start_telegram_bot()),
        daemon=True
    )
    telegram_thread.start()
    
    # Start Flask web server
    print("🌐 Starting Flask web server on port 10000...")
    app.run(host='0.0.0.0', port=10000, debug=False)

if __name__ == "__main__":
    main()
