import feedparser
import asyncio
import threading
import os
import requests
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode

app = Flask(__name__)

# ────────────────────── تنظیمات ──────────────────────
TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
# ───────────────────────────────────────────────────

SEEN_FILE = "seen.txt"

# ۱. سایت‌های ورزشی فارسی (بدون ترجمه)
PERSIAN_SPORTS = [
    "https://www.varzesh3.com/rss/football",
    "https://www.varzesh3.com/rss/team/1",        # پرسپولیس
    "https://www.varzesh3.com/rss/team/2",        # استقلال
    "https://footballi.net/feed",
    "https://www.tarafdari.com/rss",
    "https://www.90tv.ir/rss/football",
    "https://www.fartakvarzeshi.ir/rss",
]

# ۲. سایت‌های خارجی (با ترجمه خودکار به فارسی)
FOREIGN_SPORTS = [
    "https://www.bbc.com/sport/football/rss.xml",
    "https://www.skysports.com/football/rss",
    "https://www.goal.com/en/feeds/news",
    "https://www.espn.com/soccer/rss",
    "https://www.theguardian.com/football/rss",
    "https://www.marca.com/en/football/rss.xml",
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

# ترجمه رایگان گوگل (بدون کلید)
def translate(text):
    if not text or len(text) > 4000:
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {"client": "gtx", "sl": "en", "tl": "fa", "dt": "t", "q": text}
        r = requests.get(url, params=params, timeout=10)
        return "".join([x[0] for x in r.json()[0]])
    except:
        return text

async def post(title, summary, link, prefix=""):
    bot = Bot(TOKEN)
    text = f"{prefix}\n\n<b>{title}</b>\n\n{summary}\n\n<a href='{link}'>منبع</a>"
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True
        )
        print(f"{prefix} ارسال شد: {title[:50]}")
    except Exception as e:
        print(f"خطا: {e}")

async def check_all():
    seen = load_seen()
    new = 0

    # فارسی‌ها (بدون ترجمه)
    for url in PERSIAN_SPORTS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:7]:
                link = entry.link
                if link in seen: continue
                title = entry.title
                summary = (entry.get("summary") or entry.get("description", "") or "بدون خلاصه")[:350]
                await post(title, summary + "...", link, "فوتبال ایران")
                save_seen(link)
                new += 1
                await asyncio.sleep(2)
        except: pass

    # خارجی‌ها (با ترجمه)
    for url in FOREIGN_SPORTS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                link = entry.link
                if link in seen: continue
                title_en = entry.title
                summary_en = (entry.get("summary") or entry.get("description", "") or "No summary")[:500]
                
                title_fa = translate(title_en)
                summary_fa = translate(summary_en)
                if len(summary_fa) > 350:
                    summary_fa = summary_fa[:347] + "..."
                
                await post(title_fa, summary_fa, link, "فوتبال جهان")
                save_seen(link)
                new += 1
                await asyncio.sleep(4)
        except: pass

    print(f"تمام شد! {new} خبر جدید ارسال شد")

async def bot_loop():
    print("ربات خبر فوتبال فارسی + جهانی با ترجمه شروع شد!")
    while True:
        await check_all()
        print("خواب ۱۲ دقیقه...\n")
        await asyncio.sleep(720)

@app.route("/", defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return "ربات خبر فوتبال فعاله! ۲۴ ساعته کار می‌کنه 🚀"

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(bot_loop()), daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
