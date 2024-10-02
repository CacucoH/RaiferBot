"""
    ### File with all handlers
    It handles the events and refers to `logic.py`
    that contains all necessary functions
    
"""
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, Message)
from aiogram import types, F, Router

from aiogram.enums import ChatType
from aiogram.filters import (Command, PROMOTED_TRANSITION, JOIN_TRANSITION, \
                             IS_MEMBER, LEAVE_TRANSITION, chat_member_updated)

from src.interactions import logic, my_filters
from main import bot


group_router = Router()
group_router.message.filter(
    my_filters.ChatTypeFilter(["group", "supergroup"])
)

private_router = Router()
private_router.message.filter(
    my_filters.ChatTypeFilter("private")
)

#    _____            __                    __                    ____              
#   / ___/__  _______/ /____  ____ ___     / /_  ____ _____  ____/ / /__  __________
#   \__ \/ / / / ___/ __/ _ \/ __ `__ \   / __ \/ __ `/ __ \/ __  / / _ \/ ___/ ___/
#  ___/ / /_/ (__  ) /_/  __/ / / / / /  / / / / /_/ / / / / /_/ / /  __/ /  (__  ) 
# /____/\__, /____/\__/\___/_/ /_/ /_/  /_/ /_/\__,_/_/ /_/\__,_/_/\___/_/  /____/  
#      /____/                                                                       

@private_router.message(Command(commands=["start", "setup"]))
async def start_handler(msg: Message) -> None:
    """
        Basically handles a `/start` and `/setup` message 
        and returns an inline keyboard.
        
        Content of keyboard depends on user presence in database.
        This option available only from **private** chat.
    """ 
    await logic.start_handler_logic(msg=msg)




@group_router.my_chat_member(chat_member_updated.ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def bot_added_to_chat(event: chat_member_updated.ChatMemberUpdated):
    """
        Handles if **this** bot joined the channel
    """
    if (event.new_chat_member.user.id == bot.id and event.new_chat_member.user.is_bot):
        await logic.bot_added_to_chat_logic(event)


@group_router.my_chat_member(chat_member_updated.ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def bot_kicked_from_chat(event: chat_member_updated.ChatMemberUpdated):
    """
        Deletes chat from db if **this** bot was kicked and notifies all admins
    """
    if (event.new_chat_member.user.id == bot.id and event.new_chat_member.user.is_bot):
        await logic.bot_kicked_from_chat_logic(event)


@group_router.chat_member(chat_member_updated.ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def someone_added_to_chat(event: chat_member_updated.ChatMemberUpdated):
    """
        Handles if new member joined the channel
    """
    await logic.someone_added_to_chat_logic(event)


@group_router.chat_member(chat_member_updated.ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def someone_kicked_from_chat(event: chat_member_updated.ChatMemberUpdated):
    """
        Handles if new member left the channel
    """
    await logic.someone_kicked_from_chat_logic(event)


@group_router.chat_member(chat_member_updated.ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION))
async def user_privelege_escalated(event: chat_member_updated.ChatMemberUpdated):
    """
        Handles if memner became admin
    """
    await logic.user_privelege_escalated_logic(event)


@group_router.chat_member(chat_member_updated.ChatMemberUpdatedFilter(member_status_changed=~PROMOTED_TRANSITION))
async def user_privelege_downgrade(event: chat_member_updated.ChatMemberUpdated):
    """
        Handles if memner became admin
    """
    await logic.user_privelege_downgrade_logic(event)


#    ______                        __                    ____              
#   / ____/___ _____ ___  ___     / /_  ____ _____  ____/ / /__  __________
#  / / __/ __ `/ __ `__ \/ _ \   / __ \/ __ `/ __ \/ __  / / _ \/ ___/ ___/
# / /_/ / /_/ / / / / / /  __/  / / / / /_/ / / / / /_/ / /  __/ /  (__  ) 
# \____/\__,_/_/ /_/ /_/\___/  /_/ /_/\__,_/_/ /_/\__,_/_/\___/_/  /____/  
                                                                         

@group_router.message(Command("raifa"))
async def grow_raifa(msg: Message):
    await logic.grow_raifa_logic(msg)


@group_router.message(Command("stat"))
async def show_statistics(msg: Message):
    await logic.show_statistics_logic(chat_id=msg.chat.id)


# @group_router.message(Command("rules"))
# async def show_rules():


@group_router.message(F.content_type.in_({'text', 'sticker'}))
async def message_reply(msg: Message) -> None:
    prem = {None:"лох", True:"крутой"}
    await msg.answer(f"Ты знал что ты {msg.from_user.first_name} и еще ты {prem[msg.from_user.is_premium]}")
