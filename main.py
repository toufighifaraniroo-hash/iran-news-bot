import feedparser
import asyncio
from telegram import Bot
from telegram.constants import ParseMode

# ────────────────────── تنظیمات ──────────────────────
TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
# ───────────────────────────────────────────────────

SEEN_FILE = "seen.txt"

SPORT_RSS = [
    "https://www.varzesh3.com/rss/football",
    "https://www.varzesh3.com/rss/team/1",        # پرسپولیس
    "https://www.varzesh3.com/rss/team/2",        # استقلال
    "https://www.varzesh3.com/rss/competition/1", # لیگ برتر
    "https://footballi.net/feed",
    "https://www.tarafdari.com/rss",
    "https://www.90tv.ir/rss/football",
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
    
    # خلاصه رو کوتاه و تمیز می‌کنیم (حداکثر ۳۰۰ کاراکتر)
    short_summary = (summary or "").replace("\n", " ").strip()
    if len(short_summary) > 300:
        short_summary = short_summary[:297] + "..."
    
    text = f"⚽ <b>{title}</b>\n\n{short_summary}\n\n🔗 <a href='{link}'>ادامه مطلب در منبع</a>"
    
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=False
        )
        print(f"ارسال شد: {title[:50]}")
    except Exception as e:
        print(f"خطا در ارسال: {e}")

async def check_sports():
    seen = load_seen()
    total_new = 0
    
    print(f"\nچک کردن {len(SPORT_RSS)} منبع ورزشی...")
    
    for url in SPORT_RSS:
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
                
            for entry in feed.entries[:8]:
                link = entry.link
                if link in seen:
                    continue
                    
                title = entry.title.strip()
                # خلاصه رو از چند جا می‌گیره
                summary = (
                    entry.get("summary") or 
                    entry.get("description") or 
                    entry.get("content", [{}])[0].get("value", "") or
                    "خلاصه‌ای در دسترس نیست"
                )
                
                await post(title, summary, link)
                save_seen(link)
                total_new += 1
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"خطا در منبع {url}: {e}")
            continue
    
    print(f"تمام شد! {total_new} خبر جدید با خلاصه ارسال شد")

async def main():
    print("ربات خبر فوتبال فارسی با خلاصه شروع شد!")
    print("منابع: ورزش۳، طرفداری، فوتبال۳۶۰، نود و...")
    while True:
        await check_sports()
        print("خواب ۱۰ دقیقه...\n")
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main())
