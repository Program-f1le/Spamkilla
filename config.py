from dotenv import load_dotenv
import os

load_dotenv()
DB_URL = os.getenv('DB_URL')
API_KEY = os.getenv('API_KEY')
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
ADM_GROUP_ID = int(os.getenv('ADM_GROUP_ID'))