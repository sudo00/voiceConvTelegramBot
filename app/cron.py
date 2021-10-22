from telegram import Bot
import mysql.connector

from config import *


GROUPS = [
        [
            "CHAT_ID",
            "Welcome!\n\n" +
            "Rules:\n" +
            "1) Use voice messages, if you send other message(text,image,video) I'll remove you from chat!"
        ]
    ]

def main():
    bot = Bot(
        token = TG_TOKEN,
        base_url = TG_API_URL,
    )
    for key in GROUPS:
        bot.send_message(
            chat_id = key[0],
            text = key[1],
            parse_mode="HTML"
        )
    dataBase  = mysql.connector.connect(
        host = MYSQL_HOST,
        user = MYSQL_USER,
        passwd = MYSQL_PASS
    )
    dbCmd = dataBase.cursor()
    dbCmd.execute("use " + MYSQL_DB)
    dbCmd.execute("DELETE FROM " + MYSQL_TABLE_ATTENTION)    
    dataBase.commit()
    dataBase.close()

if __name__ == '__main__':
    main()
