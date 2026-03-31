from dotenv import load_dotenv
import os

load_dotenv('/var/www/app/.env')

TG_TOKEN = os.getenv('TG_TOKEN')
ADMIN_CHAT_ID = int(os.getenv('TG_ADMIN_CHAT_ID'))
DB_PATH = '/var/www/app/storage/db.sqlite'
SITE_URL = os.getenv('SITE_URL', 'http://localhost:8080')