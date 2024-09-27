"""
    ### File with all handlers
    
"""
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton )
from aiogram import Router, types, F
from aiogram.types import Message
from aiogram.filters import Command


router = Router()


@router.message(Command("start"))
async def start_handler(msg: Message) -> None:
    """
        Basically handles a `/start` message 
        and returns an inline keyboard
    """
    keyboard = ( 
        [
            [
                InlineKeyboardButton(text="Я пидор", callback_data="1")
            ],
            [
                InlineKeyboardButton(text="Испытать удачу", url="https://vk.cc/3uBrgx") # Come and see; useful stuff here!
            ]
        ]
    )

    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await msg.answer("привет ты первак?\nКороче я пиздец крутой добавь меня в группу и ~ты пожалеешь~ ты не пожалееш\!\!\!",
            reply_markup=reply_markup)


@router.message()
async def message_reply(msg: Message) -> None:
    prem = {None:"лох", True:"крутой"}
    await msg.answer(f"Ты знал что ты {msg.from_user.first_name} и еще ты {prem[msg.from_user.is_premium]}")