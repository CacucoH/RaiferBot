import logging
import asyncio
import os

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from src.interactions.handlers import router
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv


# Create an Disptcher instance and load env data
dp = Dispatcher(storage=MemoryStorage())
load_dotenv()


async def main():
    """
        #### Starts the bot
        - All previous messages (*before start*) would be **ignored**
        - All temporary values are **dropped** when bot turns off
        Lorem ipsum
    """
    bot = Bot(token=os.getenv('TOKEN'))
    dp.include_router(router=router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())