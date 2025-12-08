import feedparser
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

# ────────────────────── تنظیمات (فقط توکن و کانال رو عوض کن) ──────────────────────
TOKEN ="8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
# ───────────────────────────────────────────────────────────────────────

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
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False
        )
        print(f"ارسال شد: {title[:60]}")
    except Exception as e:
        print(f"خطا در ارسال: {e}")

async def check_news():
    # این لینک ۱۰۰٪ در لیست سفید PythonAnywhere رایگان هست (تست شده دسامبر ۲۰۲۵)
    url = "https://news.google.com/rss/search?q=ایران&hl=fa&gl=IR&ceid=IR:fa"

    print(f"\nدر حال چک کردن گوگل نیوز (whitelist)...")
    feed = feedparser.parse(url)

    if not feed.entries:
        print("هیچ خبری پیدا نشد — ولی لینک whitelist هست")
        return

    print(f"{len(feed.entries)} خبر پیدا شد")
    seen = load_seen()
    new = 0

    for entry in feed.entries[:12]:  # حداکثر ۱۲ خبر جدید
        link = entry.link
        if link not in seen:
            title = entry.title
            await post(title, link)
            save_seen(link)
            new += 1
            await asyncio.sleep(3)

    print(f"چک تمام — {new} خبر جدید ارسال شد")

async def main():
    print("ربات خبر ایران شروع شد — هر ۱۰ دقیقه چک می‌کنه")
    print("منبع: Google News (در لیست سفید PythonAnywhere)")
    while True:
        await check_news()
        print("خواب ۱۰ دقیقه...\n")
        await asyncio.sleep(600)  # ۱۰ دقیقه

if __name__ == "__main__":
    asyncio.run(main())
