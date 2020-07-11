import telebot
from telebot import types
from database import DataBase
from alice import Chatbot
import time

db = DataBase()

while True:

    tkn = ""  # Requires a telegram bot token
    bot = telebot.TeleBot(tkn)

    alice = Chatbot()

    def req_alice(message):
        return True

    @bot.message_handler(commands=["start"])
    def start(message):
        global user
        bot.send_chat_action(message.chat.id, "typing")
        msg = "Olá! Eu sou a Alice, chatbot pessoal do Thales Freitaz. Como posso te ajudar hoje?"
        bot.send_message(message.chat.id, msg)
        alice.user = db.get_telegram_user(message.chat.id)
        print(f"Usuário conectado: {alice.user[2]}")

    @bot.message_handler(func=req_alice)
    def alice_response(message):
        if not alice.user:
            alice.user = db.get_telegram_user(message.chat.id)
        get = True
        while get:
            get = False
            bot.send_chat_action(message.chat.id, "typing")
            answers = alice.get_response(message.text)
            for answer in answers:
                if len(answer) == 0:
                    get = True
                elif answer[0] == "msg":
                    # print(message.chat.id)
                    bot.send_message(message.chat.id, answer[1])
                elif answer[0] == "img":
                    bot.send_photo(message.chat.id, photo=answer[1])
                elif answer[0] == "doc":
                    bot.send_document(message.chat.id, document=answer[1])

    # print('Alice: Olá! Já estou disponível no Telegram através do link https://t.me/alice_zbot.')
    # bot.polling()
    try:
        print("Alice: Olá! Já estou disponível no Telegram através do link https://t.me/alice_zbot.")
        bot.infinity_polling(True)
        # bot.pooling()
    except:
        data = time.localtime()
        print(f"Reconectando às {data.tm_hour}:{data.tm_min}:{data.tm_sec}")

