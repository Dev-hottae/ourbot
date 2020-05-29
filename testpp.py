import telegram

from account.keys import *

msg_bot = telegram.Bot(token=tg_token)
msg_bot.send_message(chat_id=tg_my_id, text="hi")