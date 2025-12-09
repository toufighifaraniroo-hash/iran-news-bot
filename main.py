import feedparser
import asyncio
import threading
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode

app = Flask(__name__)

TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
SEEN_FILE = "seen.txt"

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def save_seen(link):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

async def post(title, link):
    bot = Bot(TOKEN)
    text = f"<b>{title}</b>\n\n🔗 <a href='{link}'>ادامه مطلب</a>"
    try:
        await bot.send_message(CHANNEL_ID, text, parse_mode=ParseMode.HTML)
        print(f"ارسال شد: {title[:60]}")
    except Exception as e:
        print(f"خطا: {e}")

async def check_news():
    url = "https://news.google.com/rss/search?q=ایران&hl=fa&gl=IR&ceid=IR:fa"  # فارسی
    print("چک RSS...")
    feed = feedparser.parse(url)
    if not feed.entries:
        print("هیچ خبری پیدا نشد")
        return
    seen = load_seen()
    new = 0
    for entry in feed.entries[:10]:
        link = entry.link
        if link not in seen:
            await post(entry.title, link)
            save_seen(link)
            new += 1
            await asyncio.sleep(3)
    print(f"{new} خبر ارسال شد")

async def bot_loop():
    print("ربات شروع شد!")
    while True:
        await check_news()
        await asyncio.sleep(600)  # ۱۰ دقیقه

@app.route("/", defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return "ربات خبر فعاله! 🌟"  # برای Render health check

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(bot_loop()), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))  # Render port
