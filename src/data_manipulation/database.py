"""
    ### This file is responsible for database interactions
    All calls made to database are handled here
"""
import sqlite3
import logging


# Connect to db
connection = sqlite3.connect(r"./src/data/raifa.db")
c = connection.cursor()


"""
    Create database if it is not (yet) exist
"""

def create_database() -> None:
    sql_statements = [
        """CREATE TABLE IF NOT EXISTS usr_chan_connection(
            user_id INTEGER,
            chat_id INTEGER,
            admin INTEGER
        )""",

        """CREATE TABLE IF NOT EXISTS user_data(
            user_id INTEGER,
            raifa_size INTEGER,
            chat_id INTEGER,
            last_grown STRING,
            luck INTEGER
        )""",

        """CREATE TABLE IF NOT EXISTS spammers(
            user_id INTEGER,
            chat_id INTEGER,
            messages_count INTEGER,
            muted INTEGER,
            till_date STRING
        )"""
    ]

    for i in sql_statements:
        c.execute(i)

create_database()

"""
    Interaction with database:
    1. **System events**
    2. **Game events**
"""


#    ___     _  _            _                                                                _             
#   / __|   | || |   ___    | |_     ___    _ __      o O O   ___    __ __    ___    _ _     | |_     ___   
#   \__ \    \_, |  (_-<    |  _|   / -_)  | '  \    o       / -_)   \ V /   / -_)  | ' \    |  _|   (_-<   
#   |___/   _|__/   /__/_   _\__|   \___|  |_|_|_|  TS__[O]  \___|   _\_/_   \___|  |_||_|   _\__|   /__/_  
# _|"""""|_| """"|_|"""""|_|"""""|_|"""""|_|"""""| {======|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| 
# "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' 


def check_user_exist(id: int, chat_id: int) -> bool:
    """ONLY FOR CHATS"""
    user = c.execute("SELECT user_id FROM usr_chan_connection WHERE user_id=? AND chat_id=?",
                     (id, chat_id,)).fetchall()
    
    if user:
        return True
    return False


def check_user_exist_v2(id: int) -> bool:
    """CHECK IF USER EXIST IN DB"""#
    user = c.execute("SELECT user_id FROM usr_chan_connection WHERE user_id=?",
                     (id,)).fetchall()
    
    if user:
        return True
    return False


def get_admin_status(id: int, chat_id: int) -> bool:
    if not check_user_exist(id=id, chat_id=chat_id):
        return False
    
    user_is_admin = c.execute("SELECT admin FROM usr_chan_connection WHERE user_id=? AND chat_id=?",
                     (id, chat_id)).fetchall()
    if user_is_admin:
        return user_is_admin[0][0] == 1
    return False


def get_chat_admins(chat_id: int) -> list[tuple[int]] | None:
    admins_list = c.execute("SELECT user_id FROM usr_chan_connection WHERE chat_id=?",
                            (chat_id,)).fetchall()
    
    return admins_list


def get_chats_for_user(user_id: int) -> list[tuple[int]] | None:
    chats_list = c.execute("SELECT chat_id FROM usr_chan_connection WHERE user_id=?",
                           (user_id,)).fetchall()
    if not chats_list:
        return
    return chats_list


def set_group_admin(id: int, chat_id: int) -> bool:
    if not check_user_exist(id=id, chat_id=chat_id):
        add_new_user(user_id=id, chat_id=chat_id, admin=1)
        return True
    
    if not get_admin_status(id=id, chat_id=chat_id):
        c.execute("UPDATE usr_chan_connection SET admin=1")
        connection.commit()
        return True
    
    return False


def revoke_admin(user_id: int, chat_id: int):
    c.execute("UPDATE usr_chan_connection SET admin=0 WHERE user_id=? AND chat_id=?",
              (user_id, chat_id,))
    
    connection.commit()
    logging.debug(f"Admin priv. was removed from {user_id} in {chat_id}")


def add_new_user(user_id: int, chat_id: int, admin: int):
    if check_user_exist(id=user_id, chat_id=chat_id):
        return

    c.execute("INSERT INTO usr_chan_connection (user_id, chat_id, admin) VALUES (?, ?, ?)",
              (user_id, chat_id, admin))
    c.execute("INSERT INTO user_data (user_id, chat_id, raifa_size, last_grown, luck) VALUES (?, ?, ?, ?, ?)",
              (user_id, chat_id, 0, "newbie", 228))

    connection.commit()
    
    if admin == 0:
        logging.debug(f"User {user_id} wants to play the game and were added!")


def remove_user(user_id: int, chat_id: int):
    c.execute("DELETE FROM usr_chan_connection WHERE user_id=? AND chat_id=?",
              (user_id, chat_id,))
    c.execute("DELETE FROM user_data WHERE user_id=? AND chat_id=?",
              (user_id, chat_id,))

    connection.commit()
    logging.warning(f"User {user_id} was removed from the {chat_id}!")


def remove_chat(chat_id: int):
    c.execute("DELETE FROM usr_chan_connection WHERE chat_id=?",
              (chat_id,))
    c.execute("DELETE FROM user_data WHERE chat_id=?",
              (chat_id,))

    connection.commit()


def add_spam_progress(player_id: int, chat_id: int) -> None:
    """
        Keep track of users that are spamming commands
    """
    if check_user_in_spam(player_id, chat_id):
        messages_count = get_spam_progress(player_id, chat_id)
        c.execute("UPDATE spammers SET messages_count=? WHERE user_id=? AND chat_id=?",
                  (messages_count+1, player_id, chat_id,))
        
    else:
        c.execute("INSERT INTO spammers (user_id, chat_id, messages_count, muted, till_date) VALUES (?,?,?,?,?)",
                (player_id, chat_id, 1, 0, "1970-01-01/12:00:00"))

    connection.commit()


def get_spam_progress(player_id: int, chat_id: int) -> int:
    """
        Counts user's spam messages 
    """
    messages = c.execute("SELECT messages_count FROM spammers WHERE user_id=? AND chat_id=?",
              (player_id, chat_id,)).fetchall()
    
    if messages[0]:
        return messages[0][0]
    return 0


def check_user_in_spam(player_id: int, chat_id: int) -> bool:
    user_in_base = c.execute("SELECT user_id FROM spammers WHERE user_id=? AND chat_id=?",
                             (player_id, chat_id,)).fetchall()
    if user_in_base:
        return True
    return False


def check_user_is_muted(player_id: int, chat_id: int) -> bool:
    muted = c.execute("SELECT muted FROM spammers WHERE user_id=? AND chat_id=?",
                             (player_id, chat_id,)).fetchall()
    return muted[0][0]


def get_muted_date(player_id: int, chat_id: int) -> str:
    date = c.execute("SELECT till_date FROM spammers WHERE user_id=? AND chat_id=?",
                             (player_id, chat_id,)).fetchall()
    return date[0][0]


def mute_player(till_date: str, player_id: int, chat_id: int):
    c.execute("UPDATE spammers SET muted=?, till_date=? WHERE user_id=? AND chat_id=?",
              (1, till_date, player_id, chat_id,))
    
    connection.commit()


def unmute_player(player_id: int, chat_id: int):
    c.execute("UPDATE spammers SET muted=0, messages_count=0 WHERE user_id=? AND chat_id=?",
              (player_id, chat_id,))
    
    connection.commit()


#    ___                                                                      _             
#   / __|   __ _    _ __     ___      o O O   ___    __ __    ___    _ _     | |_     ___   
#  | (_ |  / _` |  | '  \   / -_)    o       / -_)   \ V /   / -_)  | ' \    |  _|   (_-<   
#   \___|  \__,_|  |_|_|_|  \___|   TS__[O]  \___|   _\_/_   \___|  |_||_|   _\__|   /__/_  
# _|"""""|_|"""""|_|"""""|_|"""""| {======|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| 
# "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' 


def get_raifa_size(id: int, chat_id: int) -> int:
    size = c.execute("SELECT raifa_size FROM user_data WHERE user_id=? AND chat_id=?",
                     (id, chat_id,)).fetchall()
    
    return size[0][0]


def get_raifa_growth_date(id: int, chat_id: int) -> str | None:
    date = c.execute("SELECT last_grown FROM user_data WHERE user_id=? AND chat_id=?",
                     (id, chat_id,)).fetchall()
    
    return date[0][0]


def set_raifa_size(id: int, chat_id: int, new_size: int, date: str, increased: bool) -> None:
    # The luck mechanic is described in logic.py
    luck = c.execute("SELECT luck FROM user_data WHERE user_id=? AND chat_id=?",
                     (id, chat_id,)).fetchall()
    if not increased:
        luck = luck[0][0]
        luck += 1
    else:
        luck = 1

    c.execute("UPDATE user_data SET raifa_size=?, last_grown=?, luck=? WHERE user_id=? AND chat_id=?",
              (new_size, date, luck, id, chat_id))
    
    connection.commit()


def get_raifa_statistics(chat_id: int) -> list[dict[int, int]] | None:
    players = c.execute("SELECT user_id, raifa_size FROM user_data WHERE chat_id = ?",
                        (chat_id,)).fetchall()

    if players:
        return players
    return


def get_players(chat_id: int):
    players = c.execute("SELECT user_id FROM user_data WHERE chat_id = ?",
                        (chat_id,)).fetchall()

    if players:
        return players
    return


def inspect_raifa_command_execution(chat_id: int) -> bool:
    """
        ### Just a very optional and almost useless command
        I just wanted bot to say `"Никто еще не растил раифу"` iff no one played yet
        - Returns `false` if command wasn't executed yet
        - Returns `true` if ~virginity lost~ command executed sometime
    """
    all_players = c.execute("SELECT user_id FROM user_data WHERE chat_id = ?",
                        (chat_id,)).fetchall()
    
    newbie_players = c.execute("SELECT user_id FROM user_data WHERE last_grown = ? AND chat_id=?",
                        ("newbie", chat_id,)).fetchall()
    
    if not all_players or \
        len(all_players) == len(newbie_players):
        return False
    return True


def get_player_luck(id: int) -> int:
    luck = c.execute("SELECT luck FROM user_data WHERE user_id=?",
              (id,)).fetchall()
    
    return luck[0][0]