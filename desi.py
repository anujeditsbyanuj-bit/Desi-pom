import os
import random
import asyncio
import aiohttp
from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import logging

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Headers
def get_random_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0"
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache"
    }

# Env vars
API_ID = int(os.environ.get("API_ID", 34446649))
API_HASH = os.environ.get("API_HASH", "8dc570c08d8e35e88fb9bfc73c65d7fa")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8735534617:AAFNBedzWsDRcsiw6GXBq7QAHbqJSJiDw0w")
channel_id = os.environ.get("CHANNEL_ID", "-1003951808679")

try:
    channel_id = int(channel_id)
except ValueError:
    pass

bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 3000)))

# Fallback Dummy Data
DUMMY_DATA = [
    {
        "thumbnail": "https://placehold.co/600x400?text=No+Data",
        "name": "Sample Video",
        "description": "API কাজ না করায় এটি ডামি ভিডিও।",
        "content_url": "https://example.com/video"
    }
]

API_LIST = [
    "https://you-pom-lover.vercel.app/xnxx/10/school",
    "https://you-pom-lover.vercel.app/xnxx/10/desi",
    "https://you-pom-lover.vercel.app/xnxx/10/college",
    "https://you-pom-lover.vercel.app/xnxx/10/bhabhi"
]

async def fetch_api_data(session, api_url):
    try:
        async with session.get(api_url, headers=get_random_headers(), timeout=20) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("data", [])
            else:
                logger.warning(f"API status: {resp.status} from {api_url}")
    except Exception as e:
        logger.error(f"API Fetch Error from {api_url}: {e}")
    return []

async def auto_post():
    logger.info("🔁 Auto post started...")
    while True:
        try:
            selected_api = random.choice(API_LIST)
            logger.info(f"Selected API: {selected_api}")

            async with aiohttp.ClientSession() as session:
                api_data = await fetch_api_data(session, selected_api)

            if not api_data:
                logger.warning("No data from API, using fallback dummy data.")
                api_data = DUMMY_DATA

            success_count = 0
            for idx, item in enumerate(api_data[:10]):
                if not all(k in item for k in ['thumbnail', 'name', 'content_url']):
                    logger.warning(f"Invalid item at index {idx}")
                    continue

                thumbnail = item['thumbnail']
                if not thumbnail.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    thumbnail = "https://placehold.co/600x400?text=Image+Unavailable"

                caption = f"🔥 {item['name']}\n\n{item.get('description', 'No description')}"
                buttons = InlineKeyboardMarkup([[InlineKeyboardButton("📽️ ভিডিও দেখুন", url=item['content_url'])]])

                try:
                    await bot.send_photo(
                        chat_id=channel_id,
                        photo=thumbnail,
                        caption=caption,
                        reply_markup=buttons
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to post item {idx}: {e}")

                if idx < 9:
                    await asyncio.sleep(10)

            logger.info(f"✅ সফলভাবে {success_count} টি পোস্ট করা হয়েছে।")
            await asyncio.sleep(300)  # প্রতি 10 মিনিট পর পোস্ট হবে

        except Exception as e:
            logger.exception(f"❗ Auto post error: {e}")
            await asyncio.sleep(60)  # সমস্যা হলে ১ মিনিট অপেক্ষা করবে

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()
    logger.info("🤖 Bot is starting...")

    async def start_all():
        await bot.start()
        asyncio.create_task(auto_post())

        # Keep alive manually (Pyrogram doesn't use bot.idle)
        while True:
            await asyncio.sleep(3600)

    asyncio.run(start_all())
