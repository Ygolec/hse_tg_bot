import os
import logging
import threading
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI
from app.bot.bot import setup_bot
from app.api.routes import setup_routes



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


load_dotenv()


app = FastAPI(title="Telegram Bot API",
              docs_url="/docs")


bot = setup_bot()
setup_routes(app, bot)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Telegram bot...")
    try:

        def run_bot():
            bot.infinity_polling()

        threading.Thread(target=run_bot, daemon=True).start()
        logger.info("Telegram bot started successfully!")
    except Exception as e:
        logger.error(f"Failed to start Telegram bot: {e}")
        raise


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8300, reload=False)