from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import mysql.connector


from config import TG_TOKEN
from config import TG_API_URL
from config import FIRST
from config import SECOND
from config import THIRD 
from config import MYSQL_USER
from config import MYSQL_HOST
from config import MYSQL_PASS
from config import MYSQL_DB
from config import MYSQL_TABLE


def warningToUser(user_id, chat_id):
    dataBase  = mysql.connector.connect(
        host = MYSQL_HOST,
        user = MYSQL_USER,
        passwd = MYSQL_PASS
    )
    answer = ""
    dbCmd = dataBase.cursor()
    dbCmd.execute("use " + MYSQL_DB)
    dbCmd.execute("SELECT count from " + MYSQL_TABLE + " where user_id = " + user_id + " and chat_id = " + chat_id)
    row = dbCmd.fetchone()
    if row is None:
        dbCmd.execute("INSERT INTO " + MYSQL_TABLE + " (user_id, chat_id, count) values(" + user_id + "," + chat_id + ",1)")
        answer = FIRST
    else:    
        count = row[0]
        count += 1
        dbCmd.execute("UPDATE " + MYSQL_TABLE + " set count=" + format(count) + " where user_id = " + user_id + " and chat_id = " + chat_id)
        if count >= 3:
            dbCmd.execute("DELETE FROM " + MYSQL_TABLE + " where user_id = " + user_id + " and chat_id = " + chat_id)
            answer = THIRD
        else:
            answer = SECOND
    dataBase.commit()
    dataBase.close()
    return answer


def attention(bot: Bot, update: Update):
    getChatAdmins = bot.get_chat_administrators(update.message.chat.id)
    for key in getChatAdmins:
        if (key.user.id == update.message.from_user.id):
            isAdmin = True
            break
        else:
            isAdmin = False
    if isAdmin == False:
        kicked = warningToUser(format(update.message.from_user.id), format(update.message.chat_id))
        if (kicked == THIRD): 
            bot.send_message(
                chat_id = update.message.chat_id,
                text = THIRD,
                reply_to_message_id=update.message.message_id,
                parse_mode="HTML"
            )
            bot.kick_chat_member(
                chat_id = update.message.chat_id,
                user_id = update.message.from_user.id,
            )
        else:     
            bot.send_message(
                chat_id = update.message.chat_id,
                text = kicked,
                reply_to_message_id=update.message.message_id,
                parse_mode="HTML"   
            )



def main():
    bot = Bot(
        token = TG_TOKEN,
        base_url = TG_API_URL,
    )
    updater = Updater(
        bot = bot,
    )
    notvoice_handler = MessageHandler(~Filters.voice & ~Filters.status_update , attention)
    updater.dispatcher.add_handler(notvoice_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()