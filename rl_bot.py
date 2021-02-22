# -*- coding: utf-8 -*-
"""
@author: koka
"""
import telebot
import urllib.request
from telebot import types
from bs4 import BeautifulSoup
import time
import logging
value_cool = 0
value_like = 0
em_yes = '👍'
em_no = '👎'
em_no_answhere = 0
em_yes_answhere = 0
RUN_STOP = 1
user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
logging.basicConfig(level=logging.ERROR, filename='app.log', filemode='a')
bot = telebot.AsyncTeleBot('1284244676:AAFfRz8swAeI_JCVBL-kIdIvm_avxuPEcc4')  # основной рл бот
#bot = telebot.AsyncTeleBot("1412707995:AAGulak0VRA4rMRgD2UC-b7FRpwJzaGE0ko") # мой хом бот
WHITE_LIST_ID = [359445822, -1001383208264]

def info():
    url = 'https://www.rl.kiev.ua/'
    headers={'User-Agent':user_agent,} 
    request=urllib.request.Request(url,None,headers) 
    response = urllib.request.urlopen(request)
    data = response.read() 
    soup = BeautifulSoup(data, "lxml")
    info = soup.find('div', {'class': 'ppc'}).find('li').find('a')
    header = info.text
    link = info.get('href')
    return header, link

def info_syte(u):
    url = u
    headers={'User-Agent':user_agent,} 
    request=urllib.request.Request(url,None,headers) 
    response = urllib.request.urlopen(request)
    data = response.read() 
    soup = BeautifulSoup(data, "lxml")
    postheader = soup.find("h1", { "class" : "art-postheader" }).text  # by time
    try:
        text_code = soup.find('div', {'class': 'art-postcontent'})
        text = ''
        for t in text_code.findAll('p'):
            text = text + t.text + "\n"
        image = soup.find('div', {'class': 'art-layout-cell art-content'}).find('img').get('src')
        return postheader, image, text
    except :
        return postheader, text

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id,
                     'Команда /help для того чтобы узнать больше о командах и что они делают\n\n' +
                     'Команда /run использовать один раз, вначале, для запуска поста новостей каждые 2 часа\n\n')
        
@bot.message_handler(commands=['run'])
def handle_run(message):
    bot.send_message(message.chat.id, "Процес постинга сообщений начат, чтобы остановить напишите /stop")
    while True:
        task = bot.get_me()
        global RUN_STOP
        if RUN_STOP:
            correlate_news()
        #time.sleep(5)
        time.sleep(7200)  #это 2 часа, а это 86400 - 1 день
        result = task.wait()
         
@bot.message_handler(commands=['stop'])
def handle_stop(message):
    bot.send_message(message.chat.id, "Процес постинга сообщений остановлен, чтобы продолжить напишите /continue")
    global RUN_STOP
    RUN_STOP = 0
    
@bot.message_handler(commands=['continue'])
def handle_continue(message):
    bot.send_message(message.chat.id, "Процес постинга сообщений продолжен, чтобы остановить напишите /stop")
    global RUN_STOP
    RUN_STOP = 1
        
@bot.message_handler(commands=['help'])
def handle_help(message):
    task = bot.get_me()
    bot.send_message(message.chat.id, 
    "/stop - останавливает постинг сообщений в канал до момента использование команды продолжения\n\n" +
    "/continue - продолжает постинг сообщений в канал, если он был остановлен с помощью команды /stop\n\n" +               
    "/menu - вызывает меню доступных команд (смена емодзи, очистка последнего поста и тд..)\n\n" +
    'Остальные команды вызываються через меню, то есть вначале меню и там нажать на кнопку:\n\n' +
    'ChangeEmotions - команда для смены емодзи, присылаете по 1 стикеру и на посте будут имеено эти стикеры\n\n' +
    'show - покажет какие стикеры на данный момент будут прикрепляться к посту\n\n' + 
    'clear - очистит файл заголовка и последний пост который есть в канале перешлеться заново(можно использовать чтобы поставить нужные емодзи к определенному посту)')
    result = task.wait()
             
def clasick_keyboard(message):
    markup = types.ReplyKeyboardMarkup()
    markup.row('ChangeEmotions')
    markup.row('clear','show')
    bot.send_message(message.chat.id, "Choose:", reply_markup=markup)        

def correlate_news():
    head_syte, link_syte = info()
    with open('last_post.txt', 'rt') as file:
        head_file = file.read()
        if head_file == head_syte:
            pass
        else:
            head_file = head_syte
            send_post(link_syte)
    with open('last_post.txt', 'w') as file:
        file.write(head_file)
            
def send_post(link_syte):
    u = link_syte
    try:
        postheader, image, text = info_syte(u)
        url = image
        headers={'User-Agent':user_agent,} 
        request=urllib.request.Request(url,None,headers) 
        response = urllib.request.urlopen(request)
        data = response.read() 
        text = (text[:500] + '...') if len(data) > 500 else text
        keyboard = new_butts(0)
        bot.send_photo(WHITE_LIST_ID[1], data, caption = postheader + "\n" + u + "\n" + text, reply_markup=keyboard)
        bot.send_photo(WHITE_LIST_ID[0], data, caption = postheader + "\n" + u + "\n" + text, reply_markup=keyboard)
    except :
        postheader, text = info_syte(u)
        text = (text[:500] + '...') if len(text) > 500 else text
        keyboard = new_butts(0)
        bot.send_message(WHITE_LIST_ID[0], postheader + "\n" + u + "\n" + text, reply_markup=keyboard)
        bot.send_message(WHITE_LIST_ID[1], postheader + "\n" + u + "\n" + text, reply_markup=keyboard)
        
def new_butts(n):
    global value_cool
    global value_like
    if n == 0:
        value_cool = value_cool
        value_like = value_like
    elif n == 1:
        value_cool = value_cool + 1
        value_like = value_like
    elif n == 2:
        value_cool = value_cool
        value_like = value_like + 1
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text = str(value_cool) + ' ' + em_yes, callback_data="cool")
    key_no = types.InlineKeyboardButton(text = str(value_like) + ' ' + em_no, callback_data='like')
    keyboard.add(key_yes, key_no)
    return keyboard
    
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    task = bot.get_me()
    if call.data == "cool": 
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = new_butts(1))
    elif call.data == "like":
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup = new_butts(2))
    result = task.wait()
          
def listener(messages):
    for m in messages:
        if m.text == "/menu":
            clasick_keyboard(m)
        elif m.text == "ChangeEmotions":
            bot.send_message(m.chat.id, 'Submit the first sticker')
            global em_yes_answhere
            global em_no_answhere
            em_yes_answhere += 1
            em_no_answhere += 1
        elif em_yes_answhere == 1:
            bot.send_message(m.chat.id, 'Submit a second sticker')
            global em_yes
            em_yes = m.text
            em_yes_answhere = 0
        elif em_no_answhere == 1:
            global em_no
            em_no = m.text
            em_no_answhere = 0
            bot.send_message(m.chat.id, 'Stickers Accepted')
        elif m.text == "show":
            bot.send_message(m.chat.id, em_yes + em_no)
        elif m.text == "clear":
            bot.send_message(m.chat.id, 'File overwritten')
            with open('last_post.txt', 'w') as file:
                file.write('')

bot.set_update_listener(listener)
bot.polling(none_stop=True, interval=0)    