import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Токен бота (получить у @BotFather)
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

# Путь к базе данных
DATABASE_PATH = 'budget_bot.db'

# Категории расходов по умолчанию
DEFAULT_EXPENSE_CATEGORIES = [
    'Продукты',
    'Транспорт',
    'Развлечения',
    'Здоровье',
    'Одежда',
    'Связь',
    'Коммунальные услуги',
    'Другое'
]

# Категории доходов по умолчанию
DEFAULT_INCOME_CATEGORIES = [
    'Зарплата',
    'Фриланс',
    'Инвестиции',
    'Подарки',
    'Другое'
]
