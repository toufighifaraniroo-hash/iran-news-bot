import feedparser
import asyncio
import threading
import os
import requests
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode

app = Flask(__name__)

TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
SEEN_FILE = "seen.txt"

# منابع فارسی (۱۰۰٪ کار می‌کنه)
PERSIAN_RSS = [
    "https://www.varzesh3.com/rss/football",

]

# منابع خارجی معتبر (همه فرمت درست دارن)
INTERNATIONAL_RSS = [
    "https://www.bbc.com/sport/football/rss.xml",
    "https://www.theguardian.com/football/rss",
    "https://feeds.feedburner.com/reuters/sportsNews",
    "https://rss.nytimes.com/services/xml/rss/nyt/Soccer.xml",
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

def translate(text):
    if not text: return text
    try:
        r = requests.get("https://translate.googleapis.com/translate_a/single", 
                        params={"client": "gtx", "sl": "en", "tl": "fa", "dt": "t", "q": text}, timeout=10)
        return "".join([x[0] for x in r.json()[0]])
    except:
        return text

async def post(title, summary, link, tag):
    bot = Bot(TOKEN)
    short = (summary or "").strip()
    if len(short) > 350: short = short[:347] + "..."
    text = f"<b>{title}</b>\n\n{short}\n\n<a href='{link}'>منبع</a>\n\n{tag}"
    try:
        await bot.send_message(CHANNEL_ID, text, ParseMode.HTML, disable_web_page_preview=False)
        print(f"ارسال {tag}: {title[:50]}")
    except Exception as e:
        print(f"خطا: {e}")

async def check_all():
    seen = load_seen()
    new = 0

    for url in PERSIAN_RSS + INTERNATIONAL_RSS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                link = entry.link
                if link in seen: continue

                title_en = entry.title.strip()
                summary_en = (entry.get("summary") or entry.get("description", "") or "")[:500]

                if url in PERSIAN_RSS:
                    title_fa = title_en
                    summary_fa = summary_en
                    tag = "#ایران"
                else:
                    title_fa = translate(title_en)
                    summary_fa = translate(summary_en)
                    tag = "#جهان"

                await post(title_fa, summary_fa, link, tag)
                save_seen(link)
                new += 1
                await asyncio.sleep(3)
        except Exception as e:
            print(f"خطا در {url}: {e}")

    print(f"تمام شد — {new} خبر جدید")

async def run_bot():
    print("ربات نهایی — فارسی + خارجی معتبر + ترجمه — شروع شد!")
    while True:
        await check_all()
        print("خواب ۱۰ دقیقه...")
        await asyncio.sleep(600)

@app.route("/")
def home():
    return "ربات خبر فعاله! ⚽"

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_bot()), daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
