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


def write_bot_data(data={}):
    with open('bot_data.json', 'w') as outfile:
        json.dump(data, outfile)


def read_bot_data():
    with open("bot_data.json") as f:
        data = json.load(f)
    return data


write_bot_data()


def getInfo(id):
    url = FUEL_STATION_BASE_URL + id
    headers = {'User-Agent': 'Generic user agent'}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    page_info = json.loads(soup.text)
    
    position = "https://maps.google.com/?q={lat},{lng}".format(
        lat=page_info["data"]["coordinates"]["latitude"],
        lng=page_info["data"]["coordinates"]["longitude"]
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
            return notification
    
    strings_out = [
        "М95 - Пальне відсутнє",
        "А95 - Пальне відсутнє"
    ]
    
    for look_string in strings_out:
        if look_string not in work_desc:
            return notification


@bot.message_handler(commands=['stations'])
def stations_handler(message):
    pprint(message.text)
    nodes_str = message.text[message.text.find('/stations')+len('/stations'):]
    print(nodes_str)
    nodes = nodes_str.split(',')
    ids = [node.strip(", ") for node in nodes]
    pprint(ids)
    pprint(message.chat.id)
    bot_data = read_bot_data()
    bot_data[message.chat.id] = {
        "CheckStations": ids,
        "ActiveStations": []
    }
    write_bot_data(bot_data)


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
            pprint("!!! Info for chat id'{}:'".format(chat_id))
            bot_data = read_bot_data()
            chat_id_in_data = str(chat_id)
            if str(chat_id_in_data) not in bot_data:
                bot_data[chat_id_in_data] = {
                    "Stations": []
                }
                stations = []
            else:
                stations = bot_data[chat_id_in_data]["Stations"]

            new_stations = []
            for fuel_station_id in FUEL_STATIONS:
                message = getInfo(fuel_station_id)
                if not message:
                    continue

                new_stations.append(fuel_station_id)

                if fuel_station_id not in stations:
                    bot.send_message(chat_id, message)

            if set(new_stations) != set(stations):
                bot_data[chat_id_in_data] = {
                    "Stations": new_stations
                }
                write_bot_data(bot_data)

        except Exception as e:
            pprint(e)
            pass
            
        time.sleep(60)
        ping_time = ping_time + 60
        if ping_time > 3600:
            bot.send_message(chat_id, "Still working.")
            ping_time = 0


bot.infinity_polling()
