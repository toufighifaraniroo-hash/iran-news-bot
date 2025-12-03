import feedparser
import asyncio
import logging
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode

# تنظیمات
TOKEN = " 8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"  # توکن رباتت رو اینجا بذار
CHANNEL_ID = "@world_iran_khabar"  # مثلاً @MyIranNews
RSS_URL = " https://rss.app/rss-feed?keyword=%D8%A7%DB%8C%D8%B1%D8%A7%D9%86&region=US&lang=en"  # RSS URL از RSS.app

# لیست اخبار دیده‌شده (برای جلوگیری از تکرار، در فایل ذخیره می‌شه)
SEEN_NEWS_FILE = "seen_news.txt"
seen_news = set()

# لود اخبار دیده‌شده
def load_seen():
    try:
        with open(SEEN_NEWS_FILE, "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

# ذخیره اخبار
def save_seen(news_id):
    with open(SEEN_NEWS_FILE, "a") as f:
        f.write(news_id + "\n")

# فانکشن پست کردن به کانال
async def post_to_channel(bot, title, link, description, image_url=None):
    message = f"<b>{title}</b>\n\n{description[:500]}...\n\n<a href='{link}'>بیشتر بخوانید</a>"  # HTML mode
    if image_url:
        await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=message, parse_mode=ParseMode.HTML)
    else:
        await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=False)

# چک کردن RSS و پست کردن
async def check_rss():
    global seen_news
    seen_news = load_seen()
    bot = Bot(token=TOKEN)

    feed = feedparser.parse(RSS_URL)
    new_posts = 0

    for entry in feed.entries[:5]:  # فقط ۵ تا آخر رو چک کن
        news_id = entry.id or entry.link  # ID منحصربه‌فرد
        if news_id not in seen_news:
            title = entry.title
            link = entry.link
            description = entry.get('summary', 'خلاصه‌ای موجود نیست')
            image_url = entry.get('media_content', [{}])[0].get('url') if entry.get('media_content') else None

            await post_to_channel(bot, title, link, description, image_url)
            save_seen(news_id)
            new_posts += 1
            print(f"پست جدید: {title}")

    if new_posts == 0:
        print("خبر جدیدی نیست.")

# حلقه اصلی (هر ۱۰ دقیقه)
async def main():
    logging.basicConfig(level=logging.INFO)
    print("ربات شروع شد...")
    while True:
        await check_rss()
        await asyncio.sleep(600)  # ۱۰ دقیقه صبر

if __name__ == "__main__":
    asyncio.run(main())
