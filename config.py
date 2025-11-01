# config.py

import json

with open('config.json') as config_file:
    config = json.load(config_file)

TELEGRAM_BOT_API_TOKEN = config['TELEGRAM_BOT_API_TOKEN']
GROUP_CHAT_ID = config['GROUP_CHAT_ID']



