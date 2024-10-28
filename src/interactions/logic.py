"""
    All logic for events are written here
"""
from aiogram.types import (Message, InlineKeyboardButton, InlineKeyboardMarkup,
                           ChatMemberAdministrator, CallbackQuery)
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from aiogram.enums import ChatType, ChatMemberStatus
from aiogram.filters import chat_member_updated
from datetime import datetime, timedelta
from random import randint, choice
import json, logging

from src.data_manipulation import database
from main import bot


# Obtain all neccessary json data
with open("./src/data_manipulation/text_data.json", "r") as f:
    json_data = json.load(f)


# ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗██████╗ ███████╗
# ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝
# ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║    ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ██████╔╝███████╗
# ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║    ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ██╔══██╗╚════██║
# ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗██║  ██║███████║
# ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝


def get_start_message(user_id: int, chat_id: int) -> str:
    # Check if this is first user's occurance
    user_in_db = database.check_user_exist_v2(id=user_id)

    if not user_in_db:
        return json_data['RU']['DM_MENU']['GREETS']['user_not_in_db']
    return json_data['RU']['DM_MENU']['GREETS'][f'greet_{randint(1,2)}']


async def show_rules_dm(callback: CallbackQuery):
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=json_data['RU']['DM_MENU']['BUTTONS']['RETURN_MENU'], callback_data="exit_main_menu")]])
    await callback.message.edit_text(
        text=json_data['RU']['RULES']['rules_DM'],
        reply_markup=reply_markup
    )


async def start_handler_logic(
    msg: Message | None = None,
    callback: CallbackQuery | None = None
):
    # Create a keyboard of needed buttons
    keyboard = (
        [
            [
                InlineKeyboardButton(text=json_data['RU']['DM_MENU']['BUTTONS']['CHNL_MNG_BUTTON'][f'managing_{randint(1,2)}'], callback_data="lesgo")
            ],
            [
                InlineKeyboardButton(text=json_data['RU']['DM_MENU']['BUTTONS']['RULES'][f'rules_btn_{randint(1,2)}'], callback_data="rules")
            ],
            [
                InlineKeyboardButton(text="Испытать удачу", url="https://vk.cc/3uBrgx") # Come and see; useful stuff here!
            ]
        ]
    )
    reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    # If command received from a button - edit message
    # If not - send new one
    if callback:
        text_message = get_start_message(
            user_id=callback.from_user.id,
            chat_id=callback.from_user.id
        )
        await callback.message.edit_text(
            text=text_message,
            reply_markup=reply_markup
        )
        return

    # No data at all! Exit!
    if not msg:
        return
    
    # Send new greets message to the user
    text_message = get_start_message(user_id=msg.from_user.id, chat_id=msg.from_user.id)
    await bot.send_message(chat_id=msg.from_user.id, text=text_message, reply_markup=reply_markup)


async def setup_menu_logic(callback: CallbackQuery):
    this_usr_chats = database.get_chats_for_user(callback.from_user.id)

    # If bot are not in any user's channel
    if not this_usr_chats:
        await callback.answer(
            text="Ты не добавил меня ни в один свой канал 😕",
            show_alert=True
        )
        return

    answer_keyboard = []
    for i in this_usr_chats:
        chat_info = await bot.get_chat(chat_id=i[0])
        chat_name = chat_info.full_name
        
        if len(chat_name) > 9:
            chat_name = f"{chat_name}..."

        answer_keyboard.append(
            [
                InlineKeyboardButton(text=f"{chat_name}", callback_data=f"setup_channel:{chat_info.id}")
            ]
        )
    answer_keyboard.append(
        [
            InlineKeyboardButton(text=json_data['RU']['DM_MENU']['BUTTONS']['RETURN_MENU'],
                                 callback_data="exit_main_menu")
        ]
    )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=answer_keyboard)
    
    await callback.message.edit_text(
        text="Вот список твоих каналов где есть я:",
        reply_markup = reply_markup
    )


async def setup_chat_logic(callback: CallbackQuery):
    this_chat_id = callback.data.split(":")[1]
    actions_on_channel = (
        [
            [
                InlineKeyboardButton(text=json_data['RU']['DM_MENU']['BUTTONS']['MENU_OPTIONS']['kick'],
                                     callback_data=f"delete_bot_in:{this_chat_id}")
            ],
            [
                InlineKeyboardButton(text=json_data['RU']['DM_MENU']['BUTTONS']['RETURN_MENU'],
                                     callback_data="exit_main_menu")
            ]
        ]
    )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=actions_on_channel)
    await callback.message.edit_text(
        text="Выбери действие:",
        reply_markup=reply_markup
    )


async def remove_bot_from_logic(callback: CallbackQuery):
    # Just leave. Handler bot_kicked_from_chat would notify admins
    chat_id = callback.data.split(":")[1]
    await bot.leave_chat(chat_id=chat_id)

    # Then send regular menu message
    menu_text = get_start_message(user_id=callback.from_user.id, chat_id=chat_id)
    await start_handler_logic(
        msg=menu_text,
        callback=callback
    )
    

async def bot_added_to_chat_logic(event: chat_member_updated.ChatMemberUpdated):
    # Check if bot itself was added
    logging.debug(f"Bot {event.new_chat_member.user.full_name} was added to {event.chat.full_name}; Status {event.new_chat_member.status}")
    admins = await bot.get_chat_administrators(event.chat.id)

    # Add admins to the database
    # If admin already exists in db - ignore
    for i in admins:
        if not i.user.is_bot: 
            # Should i record this bot as admin? (or \ i.user.id == bot.id:)
            if database.set_group_admin(id=i.user.id, chat_id=event.chat.id):
                logging.debug(f"Admin {i.user.full_name} in {event.chat.full_name} ({event.chat.id}) was added")
            else:
                logging.debug(f"Admin {i.user.full_name} in {event.chat.full_name} already exists in db")

    # Send a message with rules
    await bot.send_message(
        chat_id=event.chat.id,
        text=json_data['RU']['RULES']['rules_GROUP'],
        disable_web_page_preview=True
    )


async def bot_kicked_from_chat_logic(event: chat_member_updated.ChatMemberUpdated, reason: str | None = None):
    # Notify admins that bot was kicked
    admins = database.get_chat_admins(chat_id=event.chat.id)
    if not admins:
        database.remove_chat(event.chat.id)
        return

    if admins[0]:
        for i in admins:
            admin = i[0]
            try:
                if not reason:
                    await bot.send_message(
                        text=f"Бот был удален из канала {event.chat.full_name}",
                        chat_id=admin
                    )
                else:
                    await bot.send_message(
                        text=f"Бот был удален из канала {event.chat.full_name} по причине: {reason}",
                        chat_id=admin
                    )
            except (TelegramForbiddenError, TelegramBadRequest):
                logging.warning(f"Cannot send DM to {admin}")

    # And then remove chat and all its members from DB
    database.remove_chat(event.chat.id)


async def someone_added_to_chat_logic(event: chat_member_updated.ChatMemberUpdated):
    # Check if bot was added
    # If not send greetings message
    if not event.new_chat_member.user.is_bot:
        await bot.send_message(
            text=f"Здарова, {event.new_chat_member.user.first_name}\\!",
            chat_id=event.chat.id
        )

    # Add user to database and check if they are admin
    user_info = await bot.get_chat_member(chat_id=event.chat.id, user_id=event.new_chat_member.user.id)
    admin_status = int(isinstance(user_info, ChatMemberAdministrator))
    database.add_new_user(
        user_id=event.new_chat_member.user.id,
        chat_id=event.chat.id, admin=admin_status
    )


async def someone_kicked_from_chat_logic(event: chat_member_updated.ChatMemberUpdated):
    # Press F to pay respects
    if not event.new_chat_member.user.is_bot:
        await bot.send_message(
            text=f"Press F for, {event.new_chat_member.user.first_name}\\!",
            chat_id=event.chat.id
        )
    
    # Then, delete user from DB
    database.remove_user(user_id=event.new_chat_member.user.id, chat_id=event.chat.id)


async def user_privelege_escalated_logic(event: chat_member_updated.ChatMemberUpdated):
    database.set_group_admin(id=event.new_chat_member.user.id, chat_id=event.chat.id)
    logging.debug(f"{event.new_chat_member.user.full_name} ({event.new_chat_member.user.id}) \
is now admin in {event.chat.full_name} {event.chat.id}")


async def user_privelege_downgrade_logic(event: chat_member_updated.ChatMemberUpdated):
    # If this bot lost admin privelegies - leave the chat and notify admins
    if event.new_chat_member.user.id == bot.id:
        await bot.leave_chat(chat_id=event.chat.id)
        await bot_kicked_from_chat_logic(event=event, reason="бот больше не является админом")
    
    # Remove info about ex-admin
    database.revoke_admin(user_id=event.new_chat_member.user.id, chat_id=event.chat.id)
    logging.debug(f"{event.new_chat_member.user.full_name} ({event.new_chat_member.user.id}) \
is no longer admin in {event.chat.full_name} {event.chat.id}")


async def mute_logic(msg: Message) -> bool:
    """
        #### Mute logic core
        Increases mute counter. 
        
        When reaches to 3, warns player, on 5 mutes them
        - Returns `False` if user were not warned
        - Returns `True` if user are warned
    """
    player_id = msg.from_user.id
    database.add_spam_progress(player_id, msg.chat.id)
    flood_messages = database.get_spam_progress(player_id, msg.chat.id)

    if flood_messages > 5:
        # Mute player from 3 to 7 hours
        mute_delta = randint(3,12)
        mute_date = datetime.now() + timedelta(hours=mute_delta)

        database.mute_player(
            till_date=mute_date.strftime("%Y-%m-%d/%H:%M"),
            player_id=player_id,
            chat_id=msg.chat.id
        )

        text_to_send: str = json_data['RU']['GAME_PROCESS']['PLAYER_MUTED'][f'mute_{randint(1,3)}']
        text_to_send = text_to_send.replace("{time}", str(mute_delta))

        await msg.answer(
            text=text_to_send,
            disable_notification=True,
            reply_to_message_id=msg.message_id,
            allow_sending_without_reply=True
        )
        return True

    elif flood_messages > 3:
        text_to_send: str = json_data['RU']['GAME_PROCESS']['MUTE_WARNINGS'][f'warn_{randint(1,2)}']

        if not text_to_send == "Нияз хватит":
            text_to_send = text_to_send.replace("{username}", msg.from_user.first_name)

        await msg.answer(
            text=text_to_send,
            disable_notification=True,
            reply_to_message_id=msg.message_id,
            allow_sending_without_reply=True
        )
        return True
    return False


def check_if_muted(player_id: int, chat_id: int) -> bool:
    if not database.check_user_in_spam(player_id, chat_id):
        return False

    current_date = datetime.now()
    till_date = datetime.strptime(database.get_muted_date(player_id, chat_id), "%Y-%m-%d/%H:%M")

    muted = database.check_user_is_muted(player_id=player_id, chat_id=chat_id)

    if current_date >= till_date and muted:
        database.unmute_player(player_id, chat_id)
        return False

    return bool(muted)


def clean_mute_warnings(player_id: int, chat_id: int):
    if not database.check_user_in_spam(player_id, chat_id):
        return

    database.unmute_player(player_id, chat_id)



#  ██████╗  █████╗ ███╗   ███╗███████╗    ██╗  ██╗ █████╗ ███╗   ██╗██████╗ ██╗     ███████╗██████╗ ███████╗
# ██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██║  ██║██╔══██╗████╗  ██║██╔══██╗██║     ██╔════╝██╔══██╗██╔════╝
# ██║  ███╗███████║██╔████╔██║█████╗      ███████║███████║██╔██╗ ██║██║  ██║██║     █████╗  ██████╔╝███████╗
# ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██╔══██║██╔══██║██║╚██╗██║██║  ██║██║     ██╔══╝  ██╔══██╗╚════██║
# ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ██║  ██║██║  ██║██║ ╚████║██████╔╝███████╗███████╗██║  ██║███████║
#  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝    


def may_grow_today(growth_date_str: str) -> bool:
    """
        ### Displays tomorrow/today
        - If user may grow raifa only tomorrow, returns `false`
        - Else returns `true`
    """
    today = datetime.now()
    growth_date = datetime.strptime(growth_date_str, "%Y-%m-%d") + timedelta(days=1)

    return \
        today.day == growth_date.day and \
        today.month == growth_date.month and \
        today.year == growth_date.year


def check_time(user_id: int, chat_id: int) -> bool:
    """
        ### Checks if 24h are passed since user executed command `N`
        - Returns `true` if there is "`newbie`" recording in the DB 
        (a new user attempts to grow raifa for the first time)
        - Returns `true` if 24h passed
        - Returns `false` if not

        **Note:** comparation performed thanks to `datetime` instances
    """
    # Obtain date on server and last registered user's date
    current_time = datetime.now()
    last_growth_time_str = database.get_raifa_growth_date(id=user_id, chat_id=chat_id)
    if last_growth_time_str != "newbie":
        last_growth_time = datetime.strptime(last_growth_time_str, "%Y-%m-%d/%H:%M")

    logging.debug(f"User {user_id} requested growth/attack. Last growth {last_growth_time_str}, today is {current_time.strftime('%Y-%m-%d/%H:%M')}")

    if last_growth_time_str == "newbie" or \
        (last_growth_time and \
        current_time > (last_growth_time + timedelta(days=1))):
        logging.debug(f"Growth granted")
        return True
    
    logging.debug(f"Growth denied")
    return False


def position_in_top(id: int, chat_id: int) -> int:
    """
        ### Specifies the current player's rating in the top
        Note: returns index in human style (i.e first index would be `1`, not `0`)
    """
    players = database.get_raifa_statistics(chat_id=chat_id)
    if players:
        players_sorted = sorted(players, key=lambda x: x[1], reverse=True)

    index = 0
    for i in players_sorted:
        index += 1
        if i[0] == id:
            break
    
    return index


def pick_a_victim(victims: list[int]) -> int:
    """
        Here is where victims list assembled
    """
    # Dont touch people with smallest raifa - they already suffer a lot
    victims_pool_counter = round(2/3 * len(victims))        
    victims_pool: list[int] = []

    # If there is only 1 player you can attack - its you
    if victims_pool_counter > 2:
        for i in range(0,victims_pool_counter):
            victims_pool.append(victims[i])
    else:
        victims_pool = victims

    # Observe difference between raifa sizes
    total_difference = 0
    if victims_pool_counter != 1:
        for i in range(0, victims_pool_counter-1):
            total_difference += abs(victims_pool[i] - victims_pool[i+1])
    else:
        total_difference = victims_pool[0]
    
    # Define occurance frequency for each user
    # That is based on difference between raifa sizes
    array_of_probability = []
    for i in victims_pool:
        if i == 0:
            continue

        array_of_probability.append(round(i/total_difference))

    # And produce a final array
    total_probability_array = []
    user_position = 0
    for i in array_of_probability:
        for j in range(0, i):
            total_probability_array.append(user_position)
        user_position += 1

    return choice(total_probability_array)


def success_attack_chances(
        victim_id: int, attacker_id: int,
        total_value: int, members_count: int
    ) -> list[int]:
    """
        ### Here is where success chances computed
        **Mechanic:** Luck is accumulated when user's raifa size decreases
    """
    victim_luck = database.get_player_luck(victim_id)
    attacker_luck = database.get_player_luck(attacker_id)
    
    # Dont let chanses to be 0
    if total_value % members_count == 0:
        total_value += randint(1, members_count)

    victim_chances = total_value % members_count * victim_luck
    attacker_chances = total_value % members_count * attacker_luck

    total_chances = list( 
        [victim_id for i in range(0, victim_chances)] + \
        [attacker_id for i in range(0, attacker_chances)] 
    )

    if not total_chances:
        return 0
    return total_chances


def get_delta_size(victim_current_size: int) -> int:
    """
        Computes the size of raifa attacker has stolen from victim
    """
    if victim_current_size > 10:
        return randint(5,10)
    else:
        return randint(1, victim_current_size)


async def grow_raifa_logic(msg: Message) -> None:
    """
        ### Basically the main purpose of this bot
        Grows/decreases user's raifa
    """
    user_id = msg.from_user.id
    chat_id = msg.chat.id

    if not database.check_user_exist(id=user_id, chat_id=chat_id) and \
        not msg.from_user.is_bot:
        admin_status = database.get_admin_status(id=user_id, chat_id=chat_id)

        database.add_new_user(user_id=user_id, chat_id=chat_id, admin=admin_status)

    # If < 24h passed
    # Warn player not to spam
    if not check_time(msg.from_user.id, chat_id):
        if not await mute_logic(msg):
            text_to_send = json_data['RU']['GAME_PROCESS']['RAIFA_COMMAND']['TIME_LIMIT'][f'tl_{randint(1,3)}']

            growth_date = database.get_raifa_growth_date(id=user_id, chat_id=chat_id).split('/')
            text_to_send = text_to_send.replace("{time}", growth_date[1]) \
                                       .replace("{dayMark}", json_data['RU']['GAME_PROCESS']['IS_TODAY'][str(may_grow_today(growth_date[0]))])

            await msg.answer(text=text_to_send)
        return
    
    # After success time verification we should clear warns
    # To avoid unwanted player's mute
    clean_mute_warnings(user_id, chat_id)
    
    # Get user's luck
    luck = 2 ** database.get_player_luck(id=user_id)

    current_raifa_size = database.get_raifa_size(user_id, chat_id)
    if current_raifa_size < 10:
        if luck > current_raifa_size:
            luck = current_raifa_size + 1

        increment = randint(-current_raifa_size+luck, 10)
    else:
        if luck > 10:
            luck = 11

        increment = randint(-10+luck, 10)

    increased = True

    if increment == 0:
        increment = randint(luck, 10)

    current_size = database.get_raifa_size(user_id, chat_id)
    new_size = current_size + increment

    # Size of raifa >= 0
    if new_size < 0:
        new_size = 0
    
    if increment < 0:
        increased = False
    
    # Record new growth time for this user
    current_time_str = datetime.now().strftime("%Y-%m-%d/%H:%M")
    database.set_raifa_size(id=user_id, chat_id=chat_id, new_size=new_size, date=current_time_str, increased=increased)

    # Place in the top
    new_user_position = position_in_top(id=user_id, chat_id=chat_id)
    text_to_send = "прогер еьлан"

    if increment > 0:
        text_to_send: str = json_data['RU']['GAME_PROCESS']['RAIFA_COMMAND']['INCREASED'][f'size_increased_{randint(1,3)}']
    else:
        text_to_send: str = json_data['RU']['GAME_PROCESS']['RAIFA_COMMAND']['DECREASED'][f'size_decreased_{randint(1,3)}']

   
    text_to_send = text_to_send.replace("{username}", msg.from_user.first_name) \
                .replace("{kmDelta}", str(abs(increment))) \
                .replace("{kmNew}", str(new_size)) \
                .replace("{topPlace}", str(new_user_position))
    
    await msg.answer(text=text_to_send)


async def show_statistics_logic(chat_id: int) -> None:
    """
        ### Shows top raifas in this chat
    """
    players = database.get_raifa_statistics(chat_id=chat_id)
    if players:
        # Sort all players based on sizes
        players = sorted(players, key=lambda x: x[1], reverse=True)

        # And send this to chat
        stat = f"<i><u>{json_data['RU']['GAME_PROCESS']['STAT_COMMAND'][f'stat_{randint(1,2)}']}</u>:</i>\n"

        # Display only first 10 players
        counter = 1
        for i in players:
            if counter == 11:
                break

            player_id = i[0]
            try:
                player_info = await bot.get_chat_member(user_id=player_id, chat_id=chat_id)
            except TelegramBadRequest:
                continue
            
            player_nick = player_info.user.full_name
            if len(player_nick) > 10:
                player_nick = f"{player_nick[0:9]}..."

            stat += f"<b>{counter}</b> | <i>{player_nick}</i> - <b>{i[1]}</b> км\n"

            counter += 1

        # If no one executed /raifa yest
        if not database.inspect_raifa_command_execution(chat_id=chat_id):
            await bot.send_message(
                text=json_data['RU']['GAME_PROCESS']['STAT_COMMAND']['no_one_played'],
                chat_id=chat_id
            )
            return
        
        await bot.send_message(
            text=stat,
            chat_id=chat_id,
            parse_mode="HTML"
        )
        return
    
    await bot.send_message(
        text=json_data['RU']['GAME_PROCESS']['STAT_COMMAND']['no_one_played'],
        chat_id=chat_id
    )
    return


async def attack_logic(msg: Message) -> None:
    chat_id = msg.chat.id
    attacker_id = msg.from_user.id

    victims_list = database.get_raifa_statistics(chat_id=chat_id)
    # If no victims exist - exit
    if not victims_list:
        text_to_send: str = json_data['RU']['GAME_PROCESS']['ATTACK_COMMAND']['no_players_to_attack']
        text_to_send = text_to_send.replace("{username}", msg.from_user.first_name)

        await bot.send_message(
            chat_id=chat_id,
            text=text_to_send
        )
        return
    
    # This command may be executed once after 24h. Check the time!
    if not check_time(attacker_id, chat_id):
        if not await mute_logic(msg):
            text_to_send = json_data['RU']['GAME_PROCESS']['ATTACK_COMMAND']['TIME_LIMIT'][f'tl_{randint(1,2)}']
            growth_date = database.get_raifa_growth_date(id=attacker_id, chat_id=chat_id).split('/')
            text_to_send = text_to_send.replace("{time}", growth_date[1]) \
                                       .replace("{dayMark}", json_data['RU']['GAME_PROCESS']['IS_TODAY'][str(may_grow_today(growth_date[0]))])

            await msg.answer(text=text_to_send)
        return
    
    clean_mute_warnings(attacker_id, chat_id)
    
    # Obtain only raifa sizes and sort them
    victims_list_v = map(lambda x: x[1], database.get_raifa_statistics(chat_id=chat_id))
    victims_list_sorted = sorted(victims_list, key=lambda x: x[1], reverse=True)
    victims_list_v_sorted = sorted(victims_list_v, reverse=True)

    raifa_size_attacker = database.get_raifa_size(attacker_id, chat_id)
    current_date = datetime.now().strftime("%Y-%m-%d/%H:%M")

    # Player can attack iff their size > 10 km
    if raifa_size_attacker < 1:
        text_to_send = json_data['RU']['GAME_PROCESS']['ATTACK_COMMAND']['raifa_too_small']
        text_to_send = text_to_send.replace("{username}", msg.from_user.first_name)

        await msg.answer(text=text_to_send)
        return

    # Then pick a random victim
    victim_index = pick_a_victim(victims_list_v_sorted)
    victim_id = victims_list_sorted[victim_index][0]
    victim_info = await bot.get_chat_member(chat_id=chat_id, user_id=victim_id)
    raifa_size_victim = database.get_raifa_size(victim_id, chat_id)

        
    """
        Perform an attack
        1. User attacked himself
        2. User successfully attacked
        3. User lost their attack
    """
    if victim_id == attacker_id:
        # User attakced himself. Exit
        text_to_send = json_data['RU']['GAME_PROCESS']['ATTACK_COMMAND']['SELF_ATTACK'][f'sf_{randint(1,3)}']
        text_to_send = text_to_send.replace("{username}", msg.from_user.first_name)

        await msg.answer(text=text_to_send)
        database.set_raifa_size(id=attacker_id, chat_id=chat_id, new_size=raifa_size_attacker, date=current_date, increased=False)
        return
    
    total_size = sum(victims_list_v_sorted)

    # Obtain success chances for attacker
    chances = success_attack_chances(
        victim_id=victim_id, attacker_id=attacker_id,
        total_value=total_size, members_count=len(victims_list)
    )

    # Finally obtain winner id
    winner_id = choice(chances)
    text_to_send = "хых"

    if winner_id == attacker_id:
        # Attacker won
        delta_size = get_delta_size(victim_current_size=database.get_raifa_size(victim_id, chat_id))
        text_to_send = json_data['RU']['GAME_PROCESS']['ATTACK_COMMAND']['ATTACK_SUCCEED'][f'success_{randint(1,3)}']
    else:
        # Attacker lost
        delta_size = -get_delta_size(victim_current_size=database.get_raifa_size(attacker_id, chat_id))
        text_to_send = json_data['RU']['GAME_PROCESS']['ATTACK_COMMAND']['ATTACK_FAILED'][f'fail_{randint(1,3)}']
    

    # Record new growth time for this user
    current_time_str = datetime.now().strftime("%Y-%m-%d/%H:%M")
    database.set_raifa_size(id=attacker_id, chat_id=chat_id, new_size=(raifa_size_attacker + delta_size), date=current_time_str, increased=(delta_size>0))

    # For victim dont record the new time
    old_victim_time = database.get_raifa_growth_date(id=victim_id, chat_id=chat_id)
    database.set_raifa_size(id=victim_id, chat_id=chat_id, new_size=(raifa_size_victim - delta_size), date=old_victim_time, increased=(delta_size<0))
    
    # Get new positions of players in the top
    new_attacker_position = position_in_top(id=attacker_id, chat_id=chat_id)
    new_victim_position = position_in_top(id=victim_id, chat_id=chat_id)
    
    # Format the text and send to the chat
    text_to_send = text_to_send.replace("{username}", msg.from_user.first_name) \
                                .replace("{victim}", victim_info.user.first_name) \
                                .replace("{deltaSize}", str(abs(delta_size))) \
                                .replace("{topPlaceAttacker}", str(new_attacker_position)) \
                                .replace("{topPlaceVictim}", str(new_victim_position))

    await msg.answer(text=text_to_send)