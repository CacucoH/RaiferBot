"""
    All logic for events are written here
"""
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberAdministrator
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.enums import ChatType, ChatMemberStatus
from aiogram.filters import chat_member_updated
from datetime import datetime, timedelta
from random import randint
import json, logging

from src.data import database
from main import bot


# Obtain all neccessary json data
with open("./src/data/text_data.json", "r") as f:
    json_data = json.load(f)


# ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗██████╗ ███████╗
# ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝
# ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ██████╔╝███████╗
# ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ██╔══██╗╚════██║
# ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗██║  ██║███████║
# ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝
                                                                                                                           

async def start_handler_logic(msg: Message):
    if msg.chat.type != ChatType.PRIVATE:
        await msg.answer("Ноу ноу ноу мистер фиш, меня можно натсроить только через личку")
        return
    
    user_in_db = database.check_user_exist(msg.from_user.id)
    keyboard = (
        [
            [
                InlineKeyboardButton(text="Погнали!", callback_data="1")
            ],
            [
                InlineKeyboardButton(text="Испытать удачу", url="https://vk.cc/3uBrgx") # Come and see; useful stuff here!
            ]
        ]
    )

    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    if not user_in_db:
        await msg.answer(text=json_data["RU"]["TEXT_MENU"]["GREETS"]["user_not_in_db"],
                reply_markup=reply_markup)
        return
    
    await msg.answer(text=json_data["RU"]["TEXT_MENU"]["GREETS"][f"greet_{randint(1,3)}"],
                reply_markup=reply_markup)
    

async def bot_added_to_chat_logic(event: chat_member_updated.ChatMemberUpdated):
    # Check if bot itself was added
    logging.info(f"Bot {event.new_chat_member.user.full_name} was added to {event.chat.full_name}; Status {event.new_chat_member.status}")
    admins = await bot.get_chat_administrators(event.chat.id)

    # Add admins to the database
    # If admin already exists in db - ignore
    for i in admins:
        if not i.user.is_bot:
            if database.set_group_admin(id=i.user.id, chat_id=event.chat.id):
                logging.info(f"Admin {i.user.full_name} in {event.chat.full_name} ({event.chat.id}) was added")
            else:
                logging.info(f"Admin {i.user.full_name} in {event.chat.full_name} already exists in db")


async def bot_kicked_from_chat_logic(event: chat_member_updated.ChatMemberUpdated):
    # Notify admins that bot was kicked
    admins = database.get_chat_admins(chat_id=event.chat.id)

    if admins[0]:
        for i in admins:
            admin = i[0]
            try:
                await bot.send_message(text=f"Бот был удален из канала {event.chat.full_name}", chat_id=admin)
            except TelegramForbiddenError:
                logging.warning(f"Cannot send DM to {admin}")

    # And then remove chat and all its members from DB
    database.remove_chat(event.chat.id)


async def someone_added_to_chat_logic(event: chat_member_updated.ChatMemberUpdated):
    # Check if bot was added
    # If not send greetings message
    if not event.new_chat_member.user.is_bot:
        await bot.send_message(
            text=f"Здарова, {event.new_chat_member.user.first_name}!",
            chat_id=event.chat.id
        )

    # Add user to database and check if they are admin
    user_info = await bot.get_chat_member(chat_id=event.chat.id, user_id=event.new_chat_member.user.id)
    admin_status = int(isinstance(user_info, ChatMemberAdministrator))
    database.add_new_user(user_id=event.new_chat_member.user.id,
                          chat_id=event.chat.id, admin=admin_status)


async def someone_kicked_from_chat_logic(event: chat_member_updated.ChatMemberUpdated):
    # Press F to pay respects
    if not event.new_chat_member.user.is_bot:
        await bot.send_message(
            text=f"Press F for, {event.new_chat_member.user.first_name}!",
            chat_id=event.chat.id
        )
    
    # Then, delete user from DB
    database.remove_user(user_id=event.new_chat_member.user.id, chat_id=event.chat.id)


async def user_privelege_escalated_logic(event: chat_member_updated.ChatMemberUpdated):
    database.set_group_admin(id=event.new_chat_member.user.id, chat_id=event.chat.id)
    logging.info("хуй")


async def user_privelege_downgrade_logic(event: chat_member_updated.ChatMemberUpdated):
    database.revoke_admin(user_id=event.new_chat_member.user.id, chat_id=event.chat.id)
    logging.info("хуй")


#  ██████╗  █████╗ ███╗   ███╗███████╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗██████╗ ███████╗
# ██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝
# ██║  ███╗███████║██╔████╔██║█████╗      ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ██████╔╝███████╗
# ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ██╔══██╗╚════██║
# ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗██║  ██║███████║
#  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝


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
        last_growth_time = datetime.strptime(last_growth_time_str, "%Y-%m-%d/%H:%M:%S")

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
    await msg.answer(text=f"Нет нет завоевывай после {database.get_raifa_growth_date(id=user_id).split('/')[1]} завтрашнего для")
    return


async def show_statistics_logic(chat_id: int):
    """
        Shows top raifas
    """
    players = database.get_raifa_statistics(chat_id=chat_id)
    if players:
        # Sort all players based on sizes
        players = sorted(players, key=lambda x: x[1], reverse=True)

        # And print
        stat = "Стата:\n"
        for i in players:
            player_id = i[0]
            try:
                player_info = await bot.get_chat_member(user_id=player_id, chat_id=chat_id)
            except TelegramBadRequest:
                continue

            stat += f"*{player_info.user.full_name}*: {i[1]} км\n"
        
        await bot.send_message(
            text=stat,
            chat_id=chat_id,
            parse_mode="MarkdownV2"
        )
        return
    
    await bot.send_message(
        text="Пока еще никто не растил раифу. Будь первым!",
        chat_id=chat_id
    )
    return