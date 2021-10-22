from telegram import Bot
import mysql.connector

from config import *


def main():
    bot = Bot(
        token = TG_TOKEN,
        base_url = TG_API_URL,
    )
    dataBase  = mysql.connector.connect(
        host = MYSQL_HOST,
        user = MYSQL_USER,
        passwd = MYSQL_PASS
    )
    dbCmd = dataBase.cursor()
    dbCmd.execute("use " + MYSQL_DB)
    dbCmd.execute("SELECT * from " + MYSQL_TABLE_WELCOME)
    row = dbCmd.fetchall()
    for user in row:
        user_id = str(user[0])
        count = int(user[1])
        chat_id = str(user[2])
        if count < 4:            
            dbCmd.execute("UPDATE " + MYSQL_TABLE_WELCOME + " set count=" + str(count + 1) + " where user_id = " + user_id + " and chat_id = " + chat_id)
        else:
            dbCmd.execute("DELETE FROM " + MYSQL_TABLE_WELCOME +
                            " where user_id=" + user_id + " and chat_id = " + chat_id)
                            
            bot.kick_chat_member(
                chat_id=chat_id,
                user_id=user_id,
            )
    dataBase.commit()
    dataBase.close()

if __name__ == '__main__':
    main()
