import re
import requests
import json
import time
import importlib
import config
from datetime import datetime

def get_binance():
	r = requests.get(config.BINANCE_URL)
	data = json.loads(r.text)
	with open(config.PRICE_FILE, 'w') as outfile:
		json.dump(data, outfile)

def get_price():
	with open(config.PRICE_FILE, 'r') as file:
		data = json.load(file)
		for i in config.SYMBOLS:
			for pair in data:
				if i in pair['symbol']:
					check_price(i, float(pair['price']), config.SYMBOLS[i])
					
def check_price(symbol, current, required):
	delta_price = round(abs(required - current), 2)
	print(f'[LOG] {datetime.now().strftime("%H:%M:%S")} {symbol} | PRICE: {current} | REQUIRED_PRICE: {required} | DELTA_PRICE: {delta_price} | DELTA_MAX: {config.ALERT_LEVEL*required}')
	if delta_price < config.ALERT_LEVEL*required:
		print(f'[LOG] {datetime.now().strftime("%H:%M:%S")} {symbol} is near required price!')
		check_last_alert(symbol, current)

def check_last_alert(symbol, current):
	with open(config.UPDATES_FILE, 'r') as updates:
		data = json.load(updates)
		delta_time = time.time() - float(data[symbol])
		if delta_time/60 > config.ALERT_FREQ:
			telegram(f'{symbol} price is {current}')
			print('[TG] Message sent')
			for item in data:
				if item == symbol:
					data[item] = time.time()
			with open(config.UPDATES_FILE, 'w') as updates:
				json.dump(data, updates)
		else:
			print('[TG] Alert limit')

def telegram_id():
	r = requests.get(f'https://api.telegram.org/bot{config.TOKEN}/getUpdates')
	data = json.loads(r.text)
	global chat_id
	chat_id = data['result'][0]['message']['chat']['id']
	
def telegram(msg):
	url = f'https://api.telegram.org/bot{config.TOKEN}/sendMessage?chat_id={str(chat_id)}&text={msg}'
	requests.get(url)

def main():
	while True:
		importlib.reload(config)
		get_binance()
		telegram_id()
		get_price()
		time.sleep(config.UPDATE_FREQ*60)
	
if __name__ == '__main__':
	main()
	