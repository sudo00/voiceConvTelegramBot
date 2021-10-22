from telegram import Bot
from telegram import Update
from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import mysql.connector


from config import *


def warningToUser(user_id, chat_id):
    dataBase = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASS
    )
    answer = ""
    dbCmd = dataBase.cursor()
    dbCmd.execute("use " + MYSQL_DB)
    dbCmd.execute("SELECT count from " + MYSQL_TABLE_ATTENTION +
                  " where user_id = " + user_id + " and chat_id = " + chat_id)
    row = dbCmd.fetchone()
    if row is None:
        dbCmd.execute("INSERT INTO " + MYSQL_TABLE_ATTENTION +
                      " (user_id, chat_id, count) values(" + user_id + "," + chat_id + ",1)")
        answer = FIRST
    else:
        count = row[0]
        count += 1
        dbCmd.execute("UPDATE " + MYSQL_TABLE_ATTENTION + " set count=" + format(count) +
                      " where user_id = " + user_id + " and chat_id = " + chat_id)
        if count >= 3:
            dbCmd.execute("DELETE FROM " + MYSQL_TABLE_ATTENTION +
                          " where user_id = " + user_id + " and chat_id = " + chat_id)
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
        kicked = warningToUser(
            format(update.message.from_user.id), format(update.message.chat_id))
        if (kicked == THIRD):
            bot.send_message(
                chat_id=update.message.chat_id,
                text=THIRD,
                reply_to_message_id=update.message.message_id,
                parse_mode="HTML"
            )
            bot.kick_chat_member(
                chat_id=update.message.chat_id,
                user_id=update.message.from_user.id,
            )
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text=kicked,
                reply_to_message_id=update.message.message_id,
                parse_mode="HTML"
            )


def welcome(bot: Bot, update: Update):
    dataBase = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASS
    )
    user_id = str(update.message.new_chat_members[0].id)
    chat_id = str(update.message.chat_id)
    dbCmd = dataBase.cursor()
    dbCmd.execute("use " + MYSQL_DB)
    dbCmd.execute("DELETE FROM " + MYSQL_TABLE_WELCOME +
                  " where user_id=" + user_id + " and chat_id = " + chat_id)
    dbCmd.execute("INSERT INTO " + MYSQL_TABLE_WELCOME +
                  " (user_id, count, chat_id) values(" + user_id + ", 1, " + chat_id + ")")

    dataBase.commit()
    dataBase.close()
    bot.send_message(
        chat_id=update.message.chat_id,
        text='👋🏼 Привет, [' + str(update.message.new_chat_members[0].first_name) + '](tg://user?id=' + str(
            update.message.new_chat_members[0].id) + '), у тебя 3 минуты чтобы представиться голосом 🗣🗣🗣\n🎯 ...Кратко о том кто ты и чем занимаешься... 🎯',
        parse_mode="markdown"
    )


def welcome_voice(bot: Bot, update: Update):
    dataBase = mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        passwd=MYSQL_PASS
    )
    user_id = str(update.message.from_user.id)
    chat_id = str(update.message.chat.id)
    dbCmd = dataBase.cursor()
    dbCmd.execute("use " + MYSQL_DB)
    dbCmd.execute("SELECT * FROM " + MYSQL_TABLE_WELCOME +
                  " where user_id = " + user_id + " and chat_id = " + chat_id)
    row = dbCmd.fetchone()
    if row is None:
        pass
    else:
        dbCmd.execute("DELETE FROM " + MYSQL_TABLE_WELCOME +
                      " where user_id=" + user_id + " and chat_id = " + chat_id)
    dataBase.commit()
    dataBase.close()


def main():
    bot = Bot(
        token=TG_TOKEN,
        base_url=TG_API_URL,
    )
    updater = Updater(
        bot=bot,
    )
    notvoice_handler = MessageHandler(
        ~Filters.voice & ~Filters.status_update, attention)
    joined_handler = MessageHandler(
        Filters.status_update.new_chat_members, welcome)
    voice_handler = MessageHandler(Filters.voice, welcome_voice)
    updater.dispatcher.add_handler(notvoice_handler)
    updater.dispatcher.add_handler(joined_handler)
    updater.dispatcher.add_handler(voice_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
