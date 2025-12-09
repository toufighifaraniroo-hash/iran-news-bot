import feedparser
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

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
    text = f"<b>فوتبال ⚽ {title}</b>\n\n🔗 <a href='{link}'>ادامه در ورزش۳</a>"
    try:
        await bot.send_message(CHANNEL_ID, text, parse_mode=ParseMode.HTML)
        print(f"فوتبال: {title[:50]}")
    except Exception as e:
        print(f"خطا: {e}")

async def check_varzesh3():
    url = "https://www.varzesh3.com/rss/football"  # فقط فوتبال ورزش۳
    feed = feedparser.parse(url)
    
    if not feed.entries:
        print("ورزش۳ چیزی نداد")
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
    print(f"ورزش۳: {new} خبر جدید")

async def main():
    print("ربات فقط فوتبال ورزش۳ شروع شد!")
    while True:
        await check_varzesh3()
        print("خواب ۱۰ دقیقه...")
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
