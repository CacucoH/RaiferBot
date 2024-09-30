from aiogram.types import Message
from datetime import datetime, timedelta
from random import randint

from src.data import database
from main import bot


async def grow_raifa_logic(msg: Message) -> None:
    """
        ### Basically the main purpose of this bot
    """
    user_id = msg.from_user.id
    if not database.check_user_exist(id=user_id) and \
        not msg.from_user.is_bot:
        chat_id = msg.chat.id
        admin_status = database.get_admin_status(id=user_id, chat_id=chat_id)

        database.add_new_user(user_id=user_id, chat_id=chat_id, admin=admin_status)

    # Obtain date data for sender
    current_time = datetime.now()
    last_growth_time_str = database.get_raifa_growth_date(id=user_id)
    if last_growth_time_str != "newbie":
        last_growth_time = datetime.strptime(last_growth_time_str, "%Y-%m-%d/%H-%M-%S")

    """
        Check if user attempts to grow raifa
        within less 24hrs after last try
        
        If there is "newbie" recording -
        A new user attempts to grow raifa for the first time

        Note: comparation are performed on datetime classes
    """

    if last_growth_time_str == "newbie" or \
        (last_growth_time and \
        current_time > (last_growth_time + timedelta(days=1))):

        increment = randint(-10, 10)

        current_size = database.get_raifa_size(id=user_id)
        new_size = current_size + increment

        # Size of raifa >= 0
        if new_size < 0:
            new_size = 0

        current_time_str = current_time.strftime("%Y-%m-%d/%H:%M:%S")
        database.set_raifa_size(id=user_id, new_size=new_size, date=current_time_str)
        
        if increment < 0:
            await msg.answer(text=f"{msg.from_user.first_name} лошара и территория его Раифы сократилас на {-increment} км. Теперь она составляет {new_size} км")
        else:
            await msg.answer(text=f"{msg.from_user.first_name} крутой и территория его Раифы увеличинась на {increment} км. Теперь она составляет {new_size} км")
        return
    await msg.answer(text=f"Нет нет иди нвхуй завоевывай после {database.get_raifa_growth_date(id=user_id).split('/')[1]} завтрашнего для")
    return