
> Your Own Telegram control bot


## What can this bot do?

* The bot controls a telegram chat to send only voice messages by participants.
* Send info message every day in chat by cron.

## How to use bot?

* Install requiremenets from pip-requirements.txt by command "pip3 install -r pip-requirements.txt"
* Create mysql database and table with 3 columns: id (int 11), user_id (bigint), chat_id (bigint)
* Set database settings in config.py

## How to set cron work to send info message in chat?

* Set cron "0 0 * * *  /usr/local/bin/python3.5 /../cron.py >> /var/log/cron.log 2>&1"
* Set CHAT_ID of your chat in cron.py#15