from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu():
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить доход"), KeyboardButton(text="➖ Добавить расход")],
            [KeyboardButton(text="💰 Баланс"), KeyboardButton(text="📊 Отчет")],
            [KeyboardButton(text="📝 Долги"), KeyboardButton(text="⚙️ Настройки")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_category_keyboard(categories: list):
    """Клавиатура выбора категории"""
    # Создаем кнопки по 2 в ряд для удобства
    buttons = []
    for i in range(0, len(categories), 2):
        row = [KeyboardButton(text=categories[i]['name'])]
        if i + 1 < len(categories):
            row.append(KeyboardButton(text=categories[i + 1]['name']))
        buttons.append(row)

    # Кнопки управления
    buttons.append([KeyboardButton(text="➕ Добавить категорию")])
    buttons.append([KeyboardButton(text="❌ Отмена")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_skip_keyboard():
    """Клавиатура с кнопкой пропуска"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Пропустить")],
            [KeyboardButton(text="❌ Отмена")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_report_period_keyboard():
    """Клавиатура выбора периода отчета"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Сегодня", callback_data="report_today"),
                InlineKeyboardButton(text="Неделя", callback_data="report_week")
            ],
            [
                InlineKeyboardButton(text="Месяц", callback_data="report_month"),
                InlineKeyboardButton(text="Весь период", callback_data="report_all")
            ]
        ]
    )
    return keyboard


def get_debt_menu_keyboard():
    """Меню управления долгами"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Мне должны"), KeyboardButton(text="➖ Я должен")],
            [KeyboardButton(text="📋 Список долгов"), KeyboardButton(text="✅ Закрыть долг")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_debt_type_keyboard():
    """Клавиатура типа долга для отображения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Мне должны", callback_data="debts_lent"),
                InlineKeyboardButton(text="Я должен", callback_data="debts_owe")
            ],
            [
                InlineKeyboardButton(text="Все долги", callback_data="debts_all")
            ]
        ]
    )
    return keyboard


def get_settings_keyboard():
    """Клавиатура настроек"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📂 Управление категориями")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_category_management_keyboard():
    """Клавиатура управления категориями"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📈 Категории доходов"), KeyboardButton(text="📉 Категории расходов")],
            [KeyboardButton(text="🏠 Главное меню")]
        ],
        resize_keyboard=True
    )
    return keyboard
