import feedparser
import asyncio
import threading
import os
import requests
import urllib.request
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode

app = Flask(__name__)

# تنظیمات
TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
SEEN_FILE = "seen.txt"

# لینک seen.txt تو GitHub (این رو با لینک خودت عوض کن!)
GITHUB_SEEN_URL = "https://github.com/toufighifaraniroo-hash/iran-news-bot/blob/main/seen.txt"

# منابع فارسی
PERSIAN_RSS = [
    "https://www.varzesh3.com/rss/all",
    "https://www.khabaronline.ir/rss/tp/6",#خبرآنلاین
    "https://www.tabnak.ir/fa/rss/2",#تابناک
    "https://www.tarafdari.com/static/page/taxonomy/all/feed.xml",
]

# منابع خارجی (ترجمه به فارسی)
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

# هر بار که ربات بیدار می‌شه، seen.txt رو از GitHub می‌کشه
def pull_seen_from_github():
    try:
        with urllib.request.urlopen(GITHUB_SEEN_URL, timeout=10) as response:
            with open(SEEN_FILE, "wb") as f:
                f.write(response.read())
        print("seen.txt از GitHub کشیده شد — تکراری نمیاد!")
    except Exception as e:
        print(f"نشد seen.txt رو از GitHub بکشم: {e}")

def translate(text):
    if not text or len(text) > 4000:
        return text
    try:
        r = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "en", "tl": "fa", "dt": "t", "q": text},
            timeout=10
        )
        return "".join([x[0] for x in r.json()[0]])
    except:
        return text

async def post(title, summary, link, tag):
    bot = Bot(TOKEN)
    short = (summary or "").strip()
    if len(short) > 350:
        short = short[:347] + "..."
    text = f"<b>{title}</b>\n\n{short}\n\n<a href='{link}'>منبع</a>\n\n{tag}"
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False
        )
        print(f"ارسال {tag}: {title[:50]}")
    except Exception as e:
        print(f"خطا: {e}")

async def check_all():
    seen = load_seen()
    new = 0

    for url in PERSIAN_RSS + INTERNATIONAL_RSS:
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
            for entry in feed.entries[:8]:
                link = entry.link
                if link in seen:
                    continue
                title_en = entry.title.strip()
                summary_en = (entry.get("summary") or entry.get("description", "") or "")[:500]

                if url in PERSIAN_RSS:
                    title_fa = title_en
                    summary_fa = summary_en
                    tag = "#ایران"
                else:
                    title_fa = translate(title_en)
                    summary_fa = translate(summary_en)
                    if len(summary_fa) > 350:
                        summary_fa = summary_fa[:347] + "..."
                    tag = "#جهان"

                await post(title_fa, summary_fa, link, tag)
                save_seen(link)
                new += 1
                await asyncio.sleep(3)
        except Exception as e:
            print(f"خطا در {url}: {e}")

    print(f"تمام شد — {new} خبر جدید")

async def run_bot():
    print("ربات نهایی شروع شد — فارسی + جهانی + بدون تکرار")
    pull_seen_from_github()  # ← هر بار seen.txt رو از GitHub می‌کشه
    while True:
        await check_all()
        print("خواب ۱۰ دقیقه...")
        await asyncio.sleep(600)

@app.route("/")
def home():
    return "ربات خبر فوتبال ۲۴ ساعته فعاله! ⚽"

if __name__ == "__main__":
    threading.Thread(target=lambda: asyncio.run(run_bot()), daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


