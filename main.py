import os
import asyncio
import feedparser
from telegram import Bot
from telegram.constants import ParseMode

# توکن را از متغیر محیطی می‌خوانیم
TOKEN = os.environ["TELEGRAM_TOKEN"]
CHANNEL_ID = "@world_iran_khabar"

# لیست RSSها (در صورت نیاز بعداً می‌توانی عوض کنی)
RSS_URLS = [
    "https://en.mehrnews.com/rss",
    "https://www.tehrantimes.com/rss",
    "https://presstv.ir/rss",
    "https://ifpnews.com/feed/",
    "https://www.tasnimnews.com/en/rss/feed/0/7/0/0",
]

SEEN_FILE = "seen.txt"


def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()
    except Exception as e:
        print(f"خطا در خواندن {SEEN_FILE}: {e}")
        return set()


def save_seen(news_id: str) -> None:
    try:
        with open(SEEN_FILE, "a", encoding="utf-8") as f:
            f.write(news_id + "\n")
    except Exception as e:
        print(f"خطا در ذخیره seen: {e}")


async def post(title: str, link: str, desc: str, img: str | None = None) -> None:
    bot = Bot(TOKEN)
    text = f"<b>{title}</b>\n\n{desc[:500]}...\n\n<a href='{link}'>🔗 ادامه مطلب</a>"

    try:
        if img and img.startswith(("http://", "https://")):
            await bot.send_photo(
                chat_id=CHANNEL_ID,
                photo=img,
                caption=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
            print(f"ارسال با عکس: {title[:40]}...")
        else:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
            print(f"ارسال: {title[:40]}...")
    except Exception as e:
        print(f"خطا در ارسال پیام/عکس: {e}")


async def check_rss(url: str, seen: set[str]) -> int:
    print(f"\nچک کردن: {url}")
    feed = feedparser.parse(url)

    # فقط برای لاگ و دیباگ ساده
    status = getattr(feed, "status", "N/A")
    entries = len(getattr(feed, "entries", []))
    print(f"Status: {status} | Entries: {entries}")

    if not entries:
        print("هیچ خبری برنگشت (احتمالاً دسترسی یا فیلتر).")
        return 0

    new_count = 0

    # 10 خبر آخر
    for item in reversed(feed.entries[:10]):
        news_id = item.get("id") or item.get("link") or (item.get("title", "") + item.get("link", ""))

        if not news_id or news_id in seen:
            continue

        title = item.get("title", "بدون عنوان")[:100]
        link = item.get("link", "")
        desc = (item.get("summary") or item.get("description", "خلاصه موجود نیست"))[:400]

        img = None
        if hasattr(item, "media_content") and item.media_content:
            img = item.media_content[0].get("url")
        elif hasattr(item, "enclosures") and item.enclosures:
            img = item.enclosures[0].get("href")

        await post(title, link, desc, img)
        seen.add(news_id)
        save_seen(news_id)
        new_count += 1

        if new_count >= 3:  # حداکثر 3 خبر از هر فید
            break

        await asyncio.sleep(3)

    return new_count


async def check_all() -> None:
    seen = load_seen()
    total_new = 0

    print("=" * 50)
    print(f"تعداد خبرهای قبلاً دیده شده: {len(seen)}")

    for url in RSS_URLS:
        try:
            new_cnt = await check_rss(url, seen)
            total_new += new_cnt
        except Exception as e:
            print(f"خطا در پردازش {url}: {e}")
        await asyncio.sleep(5)

    print(f"\nمجموع خبرهای جدید ارسال‌شده: {total_new}")


async def main() -> None:
    print("ربات خبر ایران راه‌اندازی شد (Loop هر ۱۵ دقیقه)")
    while True:
        try:
            await check_all()
        except Exception as e:
            print(f"خطای کلی: {e}")
        print("خواب ۱۵ دقیقه...")
        await asyncio.sleep(900)


if __name__ == "__main__":
    asyncio.run(main())
