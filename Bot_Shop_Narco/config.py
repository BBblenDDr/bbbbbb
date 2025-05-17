from dotenv import load_dotenv
import os

# Здесь мы загружаем .env
load_dotenv()

# Тут получаем данные из файла .env
token = os.getenv('token')
admin_ids = os.getenv('admin_ids')
welcome_dict = os.getenv('welcome_dict')