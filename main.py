import feedparser
import asyncio
import threading
import os
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode

app = Flask(__name__)

TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
SEEN_FILE = "seen.txt"

# فقط RSSهای فارسی که ۱۰۰٪ روی Render کار می‌کنن (تست شده دسامبر ۲۰۲۵)
PERSIAN_RSS = [
    "https://www.varzesh3.com/rss/football",           # ورزش۳ - فوتبال
    "https://www.varzesh3.com/rss/team/1",             # پرسپولیس
    "https://www.varzesh3.com/rss/team/2",             # استقلال
    "https://footballi.net/feed",                      # فوتبال۳۶۰
    "https://www.tarafdari.com/rss",                   # طرفداری
]

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except:
        return set()

def save_seen(link):
    with open(SEEN_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

async def post(title, summary, link):
    bot = Bot(TOKEN)
    text = f"<b>{title}</b>\n\n{summary}\n\n<a href='{link}'>ادامه در منبع</a>\n\n#فوتبال_ایران"
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False
        )
        print(f"ارسال شد: {title[:60]}")
    except Exception as e:
        print(f"خطا: {e}")

async def check_persian():
    seen = load_seen()
    new = 0
    
    for url in PERSIAN_RSS:
        try:
            print(f"چک {url}")
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
            for entry in feed.entries[:10]:
                link = entry.link
                if link in seen: continue
                title = entry.title.strip()
                summary = (entry.get("summary") or entry.get("description", "") or "بدون خلاصه")[:400]
                await post(title, summary + "...", link)
                save_seen(link)
                new += 1
                await asyncio.sleep(3)
        except Exception as e:
            print(f"خطا در {url}: {e}")
    
    print(f"تمام شد — {new} خبر فارسی ارسال شد")

async def bot_loop():
    print("ربات فقط خبر فارسی (ورزش۳ و ...) شروع شد — ۲۴ ساعته")
    while True:
        await check_persian()
        print("خواب ۱۰ دقیقه...\n")
        await asyncio.sleep(600)

@app.route("/", defaults={'path': ''})
@app.route('/<path:path>')
def home(path=""):
    return "ربات خبر فارسی فعاله! ⚽"

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(bot_loop()), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
