import logging
import asyncio
import os

from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv
from datetime import datetime


# Create an Disptcher instance and load env data
dp = Dispatcher(storage=MemoryStorage())
load_dotenv()

# Create bot instance
bot = Bot(
    token=os.getenv('TOKEN'),
        default=DefaultBotProperties(
            parse_mode=ParseMode.MARKDOWN_V2
        )
    )


async def main():
    """
        #### Starts the bot
        - All previous messages (*before start*) would be **ignored**
        - All temporary values are **dropped** when bot turns off
        
        Lorem ipsum
    """
    # Avoid circular import
    from src.interactions.handlers import group_router, private_router

    # Use 2 routers: one for DM and one for groups
    dp.include_router(router=group_router)
    dp.include_router(router=private_router)

    await bot.delete_webhook(drop_pending_updates=True)
    updates = dp.resolve_used_update_types()
    updates.append("chat_member")
    await dp.start_polling(bot, allowed_updates=updates)
                           

if __name__ == "__main__":
    today = datetime.now().strftime("%Y-%m-%d_%H:%M")

    # Write logs
    logging.basicConfig(
        level=logging.DEBUG, 
        format="[%(levelname)s] - %(asctime)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        filename=f"./src/logs/log_{today}.log",
        filemode="a"
    )
    asyncio.run(main())