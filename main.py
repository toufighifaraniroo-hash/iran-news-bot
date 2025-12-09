import feedparser
import asyncio
import threading
from flask import Flask
from telegram import Bot
from telegram.constants import ParseMode

# ───── تنظیمات ─────
TOKEN = "8130796014:AAFaHCOMVXkxQ2hNA5NSQ5_sAVikB0Wkx5o"
CHANNEL_ID = "@world_iran_khabar"
# ──────────────────

app = Flask(__name__)

# این صفحه فقط برای اینه که Render نخوابه
@app.route("/")
def keep_alive():
    return "ربات خبر ایران فعاله — ۲۴ ساعته کار می‌کنه! 🚀"

# کد اصلی رباتت (همون کد قبلی با RSS فارسی + خارجی + ترجمه)
async def check_news():
    # ← اینجا کد کامل چک RSS و ارسال خبر رو بذار
    # (همون کدی که قبلاً برات دادم با PERSIAN_RSS + INTERNATIONAL_RSS + ترجمه)
    pass

async def bot_loop():
    print("ربات شروع شد — هر ۱۰ دقیقه چک می‌کنه")
    while True:
        await check_news()
        await asyncio.sleep(600)  # ۱۰ دقیقه

def run_bot():
    asyncio.run(bot_loop())

# اجرای ربات در ترد جدا + Flask برای Render
if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    # Render روی پورت 10000 گوش می‌کنه
    app.run(host="0.0.0.0", port=10000)
