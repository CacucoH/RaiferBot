"""
    ### File with all handlers
    It handles the events and refers to `logic.py`
    that contains all necessary functions
    
"""
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, Message)
from aiogram import types, F, Router
from aiogram.enums import ChatType
from aiogram.filters import (Command, IS_ADMIN, \
                             IS_MEMBER, IS_NOT_MEMBER, chat_member_updated)
import json, random

import src.data.database as db
from src.interactions import logic
from main import bot


router = Router()


# Obtain all neccessary json data
with open("./src/data/text_data.json", "r") as f:
    json_data = json.load(f)


@router.message(Command("start"))
async def start_handler(msg: Message) -> None:
    """
        Basically handles a `/start` and `/setup` message 
        and returns an inline keyboard.

        Content of keyboard depends on user presence in database.
        This option available only from **private** chat.
    """
    if msg.chat.type != ChatType.PRIVATE:
        await msg.answer("Ноу ноу ноу мистер фиш, меня можно натсроить только через личку")
        return
    
    user_in_db = db.check_user_exist(msg.from_user.id)

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
    
    await msg.answer(text=json_data["RU"]["TEXT_MENU"]["GREETS"][f"greet_{random.randint(1,3)}"],
                reply_markup=reply_markup)


@router.message(Command("raifa"))
async def grow_raifa(msg: Message):
    await logic.grow_raifa_logic(msg)


# @router.chat_member(chat_member_updated.ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
# async def new_member_added(event: chat_member_updated.ChatMemberUpdated):
#     """
#         Handles if someone joined
#     """
#     # Check if bot itself was added
#     if (event.new_chat_member.user.id == bot.id and event.new_chat_member.user.is_bot):
#         print("я чурка")


@router.my_chat_member(chat_member_updated.ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added_to_chat(event: chat_member_updated.ChatMemberUpdated):
    """
        Handles if this bot joined the channel
    """
    # Check if bot itself was added
    if (event.new_chat_member.user.id == bot.id and event.new_chat_member.user.is_bot):
        admins = await bot.get_chat_administrators(event.chat.id)

        # Add admins to the database
        for i in admins:
            if not i.user.is_bot:
                db.set_group_admin(id=i.user.id, chat_id=event.chat.id)


@router.message()
async def message_reply(msg: Message) -> None:
    prem = {None:"лох", True:"крутой"}
    await msg.answer(f"Ты знал что ты {msg.from_user.first_name} и еще ты {prem[msg.from_user.is_premium]}")
