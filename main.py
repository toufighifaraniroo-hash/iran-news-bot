import feedparser
import asyncio
import hashlib
from telegram import Bot
from telegram.constants import ParseMode

TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"

# RSSهای فعال و تست‌شده (دسامبر 2025)
RSS_URLS = [
    "https://www.isna.ir/rss",
    "https://www.irna.ir/rss",
    "https://www.yjc.ir/fa/rss/all",
]


SEEN_FILE = "seen.txt"

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()
    except Exception as e:
        print(f"خطا در خواندن seen.txt: {e}")
        return set()

def save_seen(news_id):
    try:
        with open(SEEN_FILE, "a", encoding="utf-8") as f:
            f.write(news_id + "\n")
    except Exception as e:
        print(f"خطا در ذخیره seen: {e}")

async def post(title, link, desc, img=None):
    bot = Bot(TOKEN)
    text = f"<b>{title}</b>\n\n{desc[:500]}...\n\n<a href='{link}'>🔗 ادامه مطلب</a>"

    try:
        if img and img.startswith(('http://', 'https://')):
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img,
                caption=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            print(f"🖼️ ارسال با عکس: {title[:40]}...")
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False
            )
            print(f"📄 ارسال: {title[:40]}...")

    except Exception as e:
        print(f"❌ خطا در ارسال: {e}")

async def check_rss(url, seen):
    """چک یک RSS خاص با دیباگ کامل"""
    print(f"\n🔍 چک کردن: {url}")

    feed = feedparser.parse(url)

    # دیباگ اطلاعات feed
    print(f"   Status: {feed.status if hasattr(feed, 'status') else 'N/A'}")
    print(f"   Entries: {len(feed.entries) if hasattr(feed, 'entries') else 0}")
    print(f"   Bozo: {'خطا!' if hasattr(feed, 'bozo_exception') else 'OK'}")

    if not feed.entries:
        print(f"   ❌ خالی! (احتمال VPN یا feed مرده)")
        return 0

    print(f"   ✅ {len(feed.entries)} خبر پیدا شد")

    new_count = 0
    # فقط 10 خبر آخر را چک کن
    for item in reversed(feed.entries[:10]):
        # ID منحصربفرد (اول GUID، بعد link)
        news_id = item.get('id', item.link)
        if not news_id:
            news_id = item.link + item.title

        if news_id not in seen:
            title = item.title[:100] if item.title else "بدون عنوان"
            link = item.link
            desc = (item.get("summary") or item.get("description", "خلاصه موجود نیست"))[:400]

            # استخراج عکس
            img = None
            if hasattr(item, 'media_content') and item.media_content:
                img = item.media_content[0].get('url')
            elif hasattr(item, 'enclosures') and item.enclosures:
                img = item.enclosures[0].get('href')

            await post(title, link, desc, img)
            seen.add(news_id)
            save_seen(news_id)
            new_count += 1

            # تاخیر بین پست‌ها
            if new_count < 3:  # حداکثر 3 خبر از هر feed
                await asyncio.sleep(3)
            else:
                break

    return new_count

async def check_all():
    """چک همه RSSها"""
    seen = load_seen()
    total_new = 0

    print(f"\n{'='*50}")
    print(f"⏰ چک کلی - {asyncio.get_event_loop().time():.0f}")
    print(f"📁 اخبار دیده‌شده: {len(seen)}")

    for url in RSS_URLS:
        new = await check_rss(url, seen)
        total_new += new

        # تاخیر بین RSSها
        await asyncio.sleep(5)

    print(f"\n✅ تمام شد! {total_new} خبر جدید ارسال شد")
    if total_new == 0:
        print("💡 نکته: VPN روشن کن یا RSSها رو عوض کن")

    return total_new

async def main():
    print("🚀 ربات خبر ایران v2.0 راه‌اندازی شد")
    print("⏱️  هر 15 دقیقه (900 ثانیه) چک می‌کند")
    print(f"📢 کانال: {CHANNEL_ID}")
    print("-" * 50)

    while True:
        try:
            await check_all()
            print("\n😴 خواب 15 دقیقه...")
            await asyncio.sleep(900)  # 15 دقیقه
        except KeyboardInterrupt:
            print("\n🛑 متوقف شد توسط کاربر")
            break
        except Exception as e:
            print(f"❌ خطای کلی: {e}")
            await asyncio.sleep(60)  # 1 دقیقه صبر بعد خطا

if __name__ == "__main__":
    asyncio.run(main())
async def test_feed():
    feed = feedparser.parse("https://www.isna.ir/rss")
    print(f"Test: Entries = {len(feed.entries) if feed.entries else 0}")
    if feed.bozo_exception:
        print(f"Error: {feed.bozo_exception}")

# در main() اول اینو صدا بزن
await test_feed()
