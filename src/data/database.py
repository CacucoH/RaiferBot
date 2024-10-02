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
            user_id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            admin INTEGER
        )""",

        """CREATE TABLE IF NOT EXISTS user_data(
            user_id INTEGER PRIMARY KEY,
            raifa_size INTEGER,
            chat_id INTEGER,
            last_grown STRING
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


def check_user_exist(id: int) -> bool:
    user = c.execute("SELECT user_id FROM usr_chan_connection WHERE user_id=?",
                     (id,)).fetchall()
    
    if user:
        return True
    return False


def get_admin_status(id: int, chat_id: int) -> bool:
    if not check_user_exist(id):
        return False
    
    user_is_admin = c.execute("SELECT admin FROM usr_chan_connection WHERE user_id=? AND chat_id=?",
                     (id, chat_id)).fetchall()
    return user_is_admin[0][0] == 1


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
    if not check_user_exist(id=id):
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
    logging.info(f"Admin priv. was removed from {user_id} in {chat_id}")


def add_new_user(user_id: int, chat_id: int, admin: int):
    if check_user_exist(id=user_id):
        return

    c.execute("INSERT INTO usr_chan_connection (user_id, chat_id, admin) VALUES (?, ?, ?)",
              (user_id, chat_id, admin))
    c.execute("INSERT INTO user_data (user_id, chat_id, raifa_size, last_grown) VALUES (?, ?, ?, ?)",
              (user_id, chat_id ,0, "newbie"))

    connection.commit()
    
    if admin == 0:
        logging.info(f"User {user_id} wants to play the game and was aded!")
        return
    logging.info(f"Admin {user_id} of chat {chat_id} was added successfully")


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


#    ___                                                                      _             
#   / __|   __ _    _ __     ___      o O O   ___    __ __    ___    _ _     | |_     ___   
#  | (_ |  / _` |  | '  \   / -_)    o       / -_)   \ V /   / -_)  | ' \    |  _|   (_-<   
#   \___|  \__,_|  |_|_|_|  \___|   TS__[O]  \___|   _\_/_   \___|  |_||_|   _\__|   /__/_  
# _|"""""|_|"""""|_|"""""|_|"""""| {======|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""|_|"""""| 
# "`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'./o--000'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-'"`-0-0-' 


def get_raifa_size(id: int) -> int:
    size = c.execute("SELECT raifa_size FROM user_data WHERE user_id=?",
                     (id,)).fetchall()
    
    return size[0][0]


def get_raifa_growth_date(id: int) -> str | None:
    date = c.execute("SELECT last_grown FROM user_data WHERE user_id=?",
                     (id,)).fetchall()
    
    return date[0][0]


def set_raifa_size(id: int, new_size: int, date: str) -> None:
    c.execute("UPDATE user_data SET raifa_size=?, last_grown=? WHERE user_id=?",
              (new_size, date, id))
    
    connection.commit()


def get_raifa_statistics(chat_id: int) -> list[dict[str, int]] | None:
    players = c.execute("SELECT user_id, raifa_size FROM user_data WHERE chat_id = ?",
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
    
    newbie_players = c.execute("SELECT user_id FROM user_data WHERE last_grown = ?",
                        ("newbie",)).fetchall()
    
    if not all_players or \
        len(all_players) == len(newbie_players):
        return False
    return True