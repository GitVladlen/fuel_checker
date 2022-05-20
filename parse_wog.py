import telebot
from pprint import pprint
from bs4 import BeautifulSoup
import requests
import json
import time
import threading

def getInfo(id, bot, chat_id):
	url = 'https://api.wog.ua/fuel_stations/' + id
	headers = { 'User-Agent': 'Generic user agent' }
	page = requests.get(url, headers=headers)
	soup = BeautifulSoup(page.text, 'html.parser')
	page_info = json.loads(soup.text)
	notification = page_info["data"]["city"] + "\n " + page_info["data"]["workDescription"]
	pprint(notification)
	
	look_string = "М95 - Пальне відсутнє"
	if look_string not in page_info["data"]["workDescription"]:
		bot.send_message(chat_id, notification)

	look_string = "А95 - Готівка"
	if look_string in page_info["data"]["workDescription"]:
		bot.send_message(chat_id, notification)

# Program startup
TOKEN = 'YOUR_TOKEN_HERE'
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Hey, you may check by yourself!\nhttps://api.wog.ua/fuel_stations/1044\nhttps://api.wog.ua/fuel_stations/1072\nStarting to poll")
	thread = threading.Thread(name='run', target=run(message.chat.id))
	thread.start()
	
def run(chat_id):
	ping_time = 0

	while (True):
		try:
			getInfo("1044", bot, chat_id)
			getInfo("1072", bot, chat_id)
		except:
			pass
		time.sleep(60)
		ping_time = ping_time + 60
		if (ping_time > 3600):
			bot.send_message(chat_id, "Still working.")
			ping_time = 0

bot.infinity_polling()

