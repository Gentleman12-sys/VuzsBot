import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup

token = 'BotAPI'
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(content_types=['text'])
def vuzs(message):
    code = message.text
    kb = types.InlineKeyboardMarkup(row_width=1)
    response = requests.get(f'https://vuzlist.com/msk/spec/{code}')
    soup = BeautifulSoup(response.text, 'lxml')
    for i in soup.find_all('a', attrs={'class': 'page-cities-menu-link'}):
        txt = str(i.text.replace(' ', ''))
        i = str(i)
        data = i[i.rfind('.com/')+5:i.rfind('"')].replace(' ', '')
        new_soup = BeautifulSoup(requests.get(f'https://vuzlist.com/{data}/spec/{code}').text, 'lxml')
        card_list = new_soup.find_all('div', attrs={'class': 'card-title'})
        txt += ' ('+str(len(card_list))+')'
        if new_soup.find('div', attrs={'class': 'card-title'}):
            btn = types.InlineKeyboardButton(text=txt, callback_data=data+' '+code)
            kb.add(btn)
    if kb.keyboard == []:
        bot.send_message(message.chat.id, 'Вузы не найдены(')
    else:
        kb.add(types.InlineKeyboardButton(text='Все вузы', callback_data=('allVuzs '+code)))
        bot.send_message(message.chat.id, 'Вузы найдены', reply_markup=kb)

@bot.callback_query_handler(func=lambda callback: callback.data)
def all_vuzs(callback):
    if 'allVuzs' in callback.data:
        code = callback.data.split()[1]
        citys = []
        country = []
        response = requests.get('https://vuzlist.com/msk/spec/09.02.07')
        soup = BeautifulSoup(response.text, 'lxml')
        for i in soup.find_all('li', attrs={'class': 'page-cities-menu-item'}):
            i = str(i)
            citys.append(i[i.find('https://'):i.rfind('"')])
        for i in soup.find_all('a', attrs={'class': 'page-cities-menu-link'}):
            txt = i.text.replace(' ', '')
            country.append(txt)
        for i, city in enumerate(citys):
            site = f'{city}/spec/{code}'
            soup = BeautifulSoup(requests.get(site).text, 'lxml')
            card_list = soup.find_all('div', attrs={'class': 'card-title'})
            if card_list != []: bot.send_message(callback.message.chat.id, 'г.'+country[i])
            else: continue
            for card in card_list:
                vuz = card.find('a').text
                bot.send_message(callback.message.chat.id, vuz)
    else:
        response = requests.get(f'https://vuzlist.com/{callback.data.split()[0]}/spec/{callback.data.split()[1]}')
        soup = BeautifulSoup(response.text, 'lxml')
        card_list = soup.find_all('div', attrs={'class': 'card-title'})
        bot.send_message(callback.message.chat.id, 'г.'+soup.find('li', attrs={'class': 'page-cities-menu-item active'}).find('a').text)
        for card in card_list:
            vuz = card.find('a').text
            bot.send_message(callback.message.chat.id, vuz)

bot.polling(none_stop=True)