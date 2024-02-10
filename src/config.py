from dotenv import load_dotenv
import json
import os
import dacite
import yaml
from typing import Dict, List

load_dotenv()
print(os.environ["DISCORD_BOT_TOKEN"])

DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
DISCORD_CLIENT_ID = os.environ["DISCORD_CLIENT_ID"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

ALLOWED_SERVER_IDS: List[int] = []
server_ids = os.environ["ALLOWED_SERVER_IDS"].split(",")
for s in server_ids:
    ALLOWED_SERVER_IDS.append(int(s))


CONFIG_FILE_PATH = 'src/configs/bot_config.json'

def save_config(config, file_path=CONFIG_FILE_PATH):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

def load_config(file_path=CONFIG_FILE_PATH):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Initialize or load configurations
bot_config = load_config()

# Send Messages, Send Messages in Threads, Manage Messages, Read Message History
BOT_INVITE_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&permissions=328565073920&scope=bot"