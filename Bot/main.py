# from random import randint
# import time
# import telebot
# from VkParser import *
# from Telegram_.Bot.data.DataMemes import DataMemes
# import threading
# import requests
 
# import logging
# logger = telebot.logger
# telebot.logger.setLevel(logging.DEBUG)


TOKEN = '1627581809:AAF5s-1uy_3PdaJJhXNpe8Un_kiybFXSoP8'
CHAT_ID = -1001414786953
AUHTOR_CHAT_ID = 818238749
bot = telebot.TeleBot(TOKEN, parse_mode=None)
types = telebot.types


# Advanced funcs
def thread_mailing(t: int):
    while True:
        time.sleep(t)
        send_meme('')


def thread_parsing(t):
    while True:
        try:
            memes = get_posts(DataMemes.GROUPS)
            [DataMemes.memes.append(m) for m in memes if
             m['date'] not in DataMemes.used_memes and m['date'] not in [m_date['date'] for m_date in DataMemes.memes]]
            time.sleep(t)
        except TimeoutError as tm:
            print(f'Thread parsing: Error \n{tm}')
            time.sleep(10)

def get_photo_from_link(url_photo: str, chunk_size=2):
    url = url_photo
    r = requests.get(url)

    with open('photo.jpg', 'wb') as fd:
        for chunk in r.iter_content(chunk_size):
            fd.write(chunk)
    fd.close()
    return open(fd.name, 'rb')


def get_posts(groups, count=10, atts_max=1) -> list:
    '''
    :param groups:
    :param count:
    :param atts_max:
    :return: list of posts (['', ''])
    '''
    parser = VkGroupPostsParser(groups)
    posts = parser.get_posts(count=count, atts_max=atts_max)
    return posts


# Bot's funcs
@bot.message_handler(commands=['start'])
def start(msg):
    rmk = types.ReplyKeyboardMarkup()
    btns = ['/start', '/test', '/memes']
    [rmk.add(types.KeyboardButton(btn)) for btn in btns]
    bot.send_message(AUHTOR_CHAT_ID, '?', reply_markup=rmk)


@bot.message_handler(commands=['memes'])
def get_all_memes(msg):
    memes = DataMemes.memes
    if len(memes) is 0:
        bot.send_message(AUHTOR_CHAT_ID, '!!!NO MEMES!!!')
    rmk = types.ReplyKeyboardMarkup()
    btns = [f'{i}' for i in range(len(memes))]
    rmk.add('/start')
    [rmk.add(types.KeyboardButton(btn)) for btn in btns]
    bot.send_message(AUHTOR_CHAT_ID, 'What num?', reply_markup=rmk)
    bot.register_next_step_handler(msg, get_meme_step)


def get_meme_step(msg):
    try:
        i = int(msg.text)
        DataMemes.meme_to_show_index = i
        bot.send_message(AUHTOR_CHAT_ID, str(DataMemes.memes[DataMemes.meme_to_show_index]))
        rmk = types.ReplyKeyboardMarkup()
        rmk.add('<<')
        rmk.add('>>')
        rmk.add('make it first in line')
        rmk.add('delete this meme')
        rmk.add('back')
        bot.send_message(AUHTOR_CHAT_ID, text='.', reply_markup=rmk)
        bot.register_next_step_handler(msg, get_meme_next_step)
    except ValueError:
        bot.send_message(AUHTOR_CHAT_ID, 'ooooooops')
        start(msg)


def get_meme_next_step(msg):
    try:
        i = DataMemes.meme_to_show_index

        if msg.text == '>>':
            if i >= len(DataMemes.memes)-1:
                i=0
            else:
                i += 1
            msg.text = i
            get_meme_step(msg)

        elif msg.text == '<<':
            i -= 1
            msg.text = i
            get_meme_step(msg)

        elif msg.text == 'make it first in line':
            msg.text = i
            DataMemes.cur_meme_index = i
            bot.send_message(AUHTOR_CHAT_ID, 'ok')
            get_meme_step(msg)

        elif msg.text == 'delete this meme':
            msg.text = 0
            DataMemes.used_memes.append(DataMemes.memes[i]['date'])
            DataMemes.memes.pop(i)
            bot.send_message(AUHTOR_CHAT_ID, 'was deleted')
            get_meme_step(msg)

        elif msg.text == 'back':
            get_all_memes(msg)

        else:
            start(msg)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['meme'])
def send_meme(msg):
    try:
        meme: dict = DataMemes.memes[DataMemes.cur_meme_index]

        DataMemes.used_memes.append(meme['date'])
        DataMemes.memes.pop(DataMemes.cur_meme_index)

        bot.send_photo(CHAT_ID, get_photo_from_link(meme['attachments'][0]))
        DataMemes.cur_meme_index = 0
    except IndexError:
        return bot.send_message(AUHTOR_CHAT_ID, f'!!!NO MEMES!!!')


@bot.message_handler(commands=['len_memes'])
def get_len_of_memes(msg):
    return bot.send_message(AUHTOR_CHAT_ID, f'{len(DataMemes.memes)}')


@bot.message_handler(commands=['del_cur_meme'])
def del_meme(msg):
    cur_meme = DataMemes.memes[0]
    DataMemes.used_memes.append(cur_meme['date'])
    DataMemes.memes.remove(cur_meme)
    bot.reply_to(msg, 'cur meme was delited.')
    return bot.send_message(AUHTOR_CHAT_ID, f'NEXT MEME:\n'
                                            f'{DataMemes.memes[0]}')


@bot.message_handler(commands=['cur_meme'])
def cur_meme(msg):
    return bot.reply_to(msg, 'cur meme: %s' % DataMemes.memes[DataMemes.cur_meme_index])


@bot.message_handler(commands=['test'])
def test(msg):
    bot.reply_to(msg, 'testing...\n'
                      "THat's OK.")
    # bot.register_next_step_handler(msg, test)


'''
@bot.message_handler(func=lambda m: True)
def echo_all(msg):
    bot.reply_to(msg, msg.text)


@bot.message_handler(regexp="ok,then")
def handle_message(message):
    print('detected')'''


def start_bot():
    def start_thread_funcs():
        thread_funcs = [threading.Thread(target=thread_parsing, args=([5])),
                        threading.Thread(target=thread_mailing, args=([1500]))]
        return [func.start() for func in thread_funcs]

    bot.send_message(AUHTOR_CHAT_ID, 'online')
    start_thread_funcs()
    bot.polling()


def main():
    print('AUF')
#     start_bot()


if __name__ == '__main__':
    main()

    '''    # start_bot()
        # t1 = threading.Thread(target=thread_parsing, args=([50]))
        # t1.start()
        # t2 = threading.Thread(target=thread_mailing, args=([150]))
        # t2.start()
        # while True:
        #     time.sleep(4)
        #     print(len(DataMemes.memes))'''
