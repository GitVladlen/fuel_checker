import telebot
from pprint import pprint
from bs4 import BeautifulSoup
import requests
import json
import time
import threading

FUEL_STATION_BASE_URL = "https://api.wog.ua/fuel_stations/"

# Setup your bot here
TOKEN = "YOUR_BOT_TOKEN"
FUEL_STATIONS = [
    # ids of fuel station for check
    # you can find it on https://api.wog.ua/fuel_stations/
]

# Or setup your bot from config.json file
with open("config.json") as f:
    data = json.load(f)
    TOKEN = data["TOKEN"]
    FUEL_STATIONS = data["FUEL_STATIONS"]

bot = telebot.TeleBot(TOKEN)


def getInfo(id, bot, chat_id):
    url = FUEL_STATION_BASE_URL + id
    headers = {'User-Agent': 'Generic user agent'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    page_info = json.loads(soup.text)
    
    position = "https://maps.google.com/?q={lat},{lng}".format(
        lat = page_info["data"]["coordinates"]["latitude"],
        lng = page_info["data"]["coordinates"]["longitude"]
    )
    
    notification = page_info["data"]["city"] + "\n" \
                   + page_info["data"]["name"] + "\n" \
                   + position + "\n" \
                   + page_info["data"]["workDescription"]
    
    pprint(notification)
    
    work_desc = page_info["data"]["workDescription"]
    
    strings_in = [
        "А95 - Готівка"
    ]
    
    for look_string in strings_in:
        if look_string in work_desc:
            bot.send_message(chat_id, notification)
            return
    
    strings_out = [
        "М95 - Пальне відсутнє",
        "А95 - Пальне відсутнє"
    ]
    
    for look_string in strings_out:
        if look_string not in work_desc:
            bot.send_message(chat_id, notification)
            return


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    answer = "Hey, you may check by yourself!\n"
    for fuel_station_id in FUEL_STATIONS:
        answer += FUEL_STATION_BASE_URL + fuel_station_id + "\n"
    answer += "Starting to poll"

    bot.reply_to(message, answer)

    thread = threading.Thread(name='run', target=run(message.chat.id))
    thread.start()


def run(chat_id):
    pprint("Started polling")
    ping_time = 0

    while True:
        try:
            for fuel_station_id in FUEL_STATIONS:
                getInfo(fuel_station_id, bot, chat_id)
        except Exception as e:
            pprint(e)
            pass
            
        time.sleep(60)
        ping_time = ping_time + 60
        if ping_time > 3600:
            bot.send_message(chat_id, "Still working.")
            ping_time = 0


bot.infinity_polling()
