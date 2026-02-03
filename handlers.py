from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from database import Database
from states import TransactionStates, DebtStates, CategoryStates
from keyboards import (
    get_main_menu,
    get_category_keyboard,
    get_skip_keyboard,
    get_report_period_keyboard,
    get_debt_menu_keyboard,
    get_debt_type_keyboard,
    get_settings_keyboard,
    get_category_management_keyboard
)
from utils import format_currency, generate_report_text


def register_handlers(dp, db: Database):
    """Регистрация всех обработчиков"""
    router = Router()

    # Команды
    @router.message(Command("start"))
    async def cmd_start(message: Message):
        await db.add_user(message.from_user.id, message.from_user.username or "Unknown")
        await db.init_default_categories(message.from_user.id)
        await message.answer(
            f"Привет, {message.from_user.first_name}!\n\n"
            "Я помогу тебе управлять личным бюджетом.\n\n"
            "Используй меню ниже для работы с ботом:",
            reply_markup=get_main_menu()
        )

    @router.message(Command("help"))
    async def cmd_help(message: Message):
        help_text = """
📖 <b>Справка по командам:</b>

➕ <b>Добавить доход</b> - записать поступление денег
➖ <b>Добавить расход</b> - записать трату

💰 <b>Баланс</b> - посмотреть текущий баланс
📊 <b>Отчет</b> - получить детальный отчет за период

📝 <b>Долги</b> - управление долгами
⚙️ <b>Настройки</b> - настройки бота и категорий

<b>Команды:</b>
/start - начать работу
/help - справка
/cancel - отменить текущее действие
        """
        await message.answer(help_text, parse_mode="HTML")

    @router.message(Command("cancel"))
    @router.message(F.text == "❌ Отмена")
    async def cmd_cancel(message: Message, state: FSMContext):
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=get_main_menu()
        )

    # Добавление дохода
    @router.message(F.text == "➕ Добавить доход")
    async def add_income_start(message: Message, state: FSMContext):
        await state.set_state(TransactionStates.waiting_for_amount)
        await state.update_data(trans_type="income")
        await message.answer(
            "Введите сумму дохода:",
            reply_markup=get_skip_keyboard()
        )

    # Добавление расхода
    @router.message(F.text == "➖ Добавить расход")
    async def add_expense_start(message: Message, state: FSMContext):
        await state.set_state(TransactionStates.waiting_for_amount)
        await state.update_data(trans_type="expense")
        await message.answer(
            "Введите сумму расхода:",
            reply_markup=get_skip_keyboard()
        )

    # Обработка суммы
    @router.message(TransactionStates.waiting_for_amount)
    async def process_amount(message: Message, state: FSMContext):
        try:
            amount = float(message.text.replace(',', '.'))
            if amount <= 0:
                await message.answer("Сумма должна быть положительной. Попробуйте еще раз:")
                return

            await state.update_data(amount=amount)
            data = await state.get_data()
            trans_type = data['trans_type']

            # Получаем категории из БД
            categories = await db.get_categories(message.from_user.id, trans_type)
            keyboard = get_category_keyboard(categories)

            text = "Выберите категорию дохода:" if trans_type == "income" else "Выберите категорию расхода:"

            await state.set_state(TransactionStates.waiting_for_category)
            await message.answer(text, reply_markup=keyboard)

        except ValueError:
            await message.answer("Неверный формат. Введите число (например: 1000 или 1500.50):")

    # Обработка добавления новой категории из выбора
    @router.message(TransactionStates.waiting_for_category, F.text == "➕ Добавить категорию")
    async def add_category_from_transaction(message: Message, state: FSMContext):
        data = await state.get_data()
        # Сохраняем текущее состояние транзакции
        await state.update_data(return_to_transaction=True)
        await state.set_state(CategoryStates.waiting_for_new_category_name)
        await message.answer(
            "Введите название новой категории:",
            reply_markup=get_skip_keyboard()
        )

    # Обработка категории
    @router.message(TransactionStates.waiting_for_category)
    async def process_category(message: Message, state: FSMContext):
        await state.update_data(category=message.text)
        await state.set_state(TransactionStates.waiting_for_description)
        await message.answer(
            "Введите описание (или нажмите 'Пропустить'):",
            reply_markup=get_skip_keyboard()
        )

    # Обработка описания
    @router.message(TransactionStates.waiting_for_description)
    async def process_description(message: Message, state: FSMContext):
        description = None if message.text == "⏭ Пропустить" else message.text

        data = await state.get_data()
        await db.add_transaction(
            user_id=message.from_user.id,
            trans_type=data['trans_type'],
            amount=data['amount'],
            category=data['category'],
            description=description
        )

        trans_type_text = "доход" if data['trans_type'] == "income" else "расход"
        await message.answer(
            f"✅ {trans_type_text.capitalize()} успешно добавлен!\n\n"
            f"Сумма: {format_currency(data['amount'])}\n"
            f"Категория: {data['category']}\n"
            f"Описание: {description or 'не указано'}",
            reply_markup=get_main_menu()
        )
        await state.clear()

    # Баланс
    @router.message(F.text == "💰 Баланс")
    async def show_balance(message: Message):
        balance_data = await db.get_balance(message.from_user.id)

        text = f"""
💰 <b>Ваш баланс:</b>

📈 Доходы: {format_currency(balance_data['income'])}
📉 Расходы: {format_currency(balance_data['expense'])}
{'➖' * 20}
💵 Баланс: {format_currency(balance_data['balance'])}
        """
        await message.answer(text, parse_mode="HTML")

    # Отчет
    @router.message(F.text == "📊 Отчет")
    async def show_report_menu(message: Message):
        await message.answer(
            "Выберите период для отчета:",
            reply_markup=get_report_period_keyboard()
        )

    @router.callback_query(F.data.startswith("report_"))
    async def process_report(callback: CallbackQuery):
        period = callback.data.split("_")[1]
        user_id = callback.from_user.id

        # Определение дат
        end_date = datetime.now()
        if period == "today":
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            period_text = "Сегодня"
        elif period == "week":
            start_date = end_date - timedelta(days=7)
            period_text = "За неделю"
        elif period == "month":
            start_date = end_date - timedelta(days=30)
            period_text = "За месяц"
        else:
            start_date = None
            period_text = "За весь период"

        # Получение данных
        balance = await db.get_balance(
            user_id,
            start_date.isoformat() if start_date else None,
            end_date.isoformat()
        )
        expense_stats = await db.get_category_stats(
            user_id,
            "expense",
            start_date.isoformat() if start_date else None,
            end_date.isoformat()
        )
        income_stats = await db.get_category_stats(
            user_id,
            "income",
            start_date.isoformat() if start_date else None,
            end_date.isoformat()
        )

        report_text = generate_report_text(period_text, balance, income_stats, expense_stats)
        await callback.message.answer(report_text, parse_mode="HTML")
        await callback.answer()

    # Долги
    @router.message(F.text == "📝 Долги")
    async def show_debt_menu(message: Message):
        await message.answer(
            "Управление долгами:",
            reply_markup=get_debt_menu_keyboard()
        )

    @router.message(F.text == "➕ Мне должны")
    async def add_lent_debt(message: Message, state: FSMContext):
        await state.set_state(DebtStates.waiting_for_person_name)
        await state.update_data(debt_type="lent")
        await message.answer(
            "Введите имя человека, который должен вам:",
            reply_markup=get_skip_keyboard()
        )

    @router.message(F.text == "➖ Я должен")
    async def add_owe_debt(message: Message, state: FSMContext):
        await state.set_state(DebtStates.waiting_for_person_name)
        await state.update_data(debt_type="owe")
        await message.answer(
            "Введите имя человека, которому вы должны:",
            reply_markup=get_skip_keyboard()
        )

    @router.message(DebtStates.waiting_for_person_name)
    async def process_debt_person(message: Message, state: FSMContext):
        await state.update_data(person_name=message.text)
        await state.set_state(DebtStates.waiting_for_amount)
        await message.answer("Введите сумму долга:")

    @router.message(DebtStates.waiting_for_amount)
    async def process_debt_amount(message: Message, state: FSMContext):
        try:
            amount = float(message.text.replace(',', '.'))
            if amount <= 0:
                await message.answer("Сумма должна быть положительной. Попробуйте еще раз:")
                return

            await state.update_data(amount=amount)
            await state.set_state(DebtStates.waiting_for_description)
            await message.answer(
                "Введите описание (или нажмите 'Пропустить'):",
                reply_markup=get_skip_keyboard()
            )
        except ValueError:
            await message.answer("Неверный формат. Введите число:")

    @router.message(DebtStates.waiting_for_description)
    async def process_debt_description(message: Message, state: FSMContext):
        description = None if message.text == "⏭ Пропустить" else message.text

        data = await state.get_data()
        await db.add_debt(
            user_id=message.from_user.id,
            debt_type=data['debt_type'],
            person_name=data['person_name'],
            amount=data['amount'],
            description=description
        )

        debt_type_text = "вам должен" if data['debt_type'] == "lent" else "вы должны"
        await message.answer(
            f"✅ Долг добавлен!\n\n"
            f"{data['person_name']} {debt_type_text}\n"
            f"Сумма: {format_currency(data['amount'])}\n"
            f"Описание: {description or 'не указано'}",
            reply_markup=get_debt_menu_keyboard()
        )
        await state.clear()

    @router.message(F.text == "📋 Список долгов")
    async def show_debts_list(message: Message):
        await message.answer(
            "Выберите тип долгов:",
            reply_markup=get_debt_type_keyboard()
        )

    @router.callback_query(F.data.startswith("debts_"))
    async def process_debts_list(callback: CallbackQuery):
        debt_type = callback.data.split("_")[1]
        user_id = callback.from_user.id

        if debt_type == "all":
            debts = await db.get_debts(user_id, is_paid=False)
            title = "📋 Все непогашенные долги:"
        elif debt_type == "lent":
            debts = await db.get_debts(user_id, is_paid=False)
            debts = [d for d in debts if d['type'] == 'lent']
            title = "📋 Вам должны:"
        else:
            debts = await db.get_debts(user_id, is_paid=False)
            debts = [d for d in debts if d['type'] == 'owe']
            title = "📋 Вы должны:"

        if not debts:
            await callback.message.answer("Долгов не найдено!")
            await callback.answer()
            return

        text = f"<b>{title}</b>\n\n"
        total = 0
        for debt in debts:
            debt_symbol = "➕" if debt['type'] == 'lent' else "➖"
            text += f"{debt_symbol} <b>{debt['person_name']}</b>\n"
            text += f"   Сумма: {format_currency(debt['amount'])}\n"
            if debt['description']:
                text += f"   Описание: {debt['description']}\n"
            text += f"   ID: {debt['id']}\n\n"
            total += debt['amount'] if debt['type'] == 'lent' else -debt['amount']

        text += f"\n💰 Итого: {format_currency(abs(total))}"

        await callback.message.answer(text, parse_mode="HTML")
        await callback.answer()

    # Настройки
    @router.message(F.text == "⚙️ Настройки")
    async def settings(message: Message):
        await message.answer(
            "⚙️ Настройки:",
            reply_markup=get_settings_keyboard()
        )

    @router.message(F.text == "📂 Управление категориями")
    async def category_management(message: Message):
        await message.answer(
            "Управление категориями:",
            reply_markup=get_category_management_keyboard()
        )

    @router.message(F.text == "📈 Категории доходов")
    async def show_income_categories(message: Message):
        categories = await db.get_categories(message.from_user.id, "income")

        if not categories:
            await message.answer("Категории доходов не найдены. Добавьте новые категории!")
            return

        text = "📈 <b>Категории доходов:</b>\n\n"
        for cat in categories:
            default_mark = " (по умолчанию)" if cat['is_default'] else ""
            text += f"• {cat['name']}{default_mark}\n"

        await message.answer(text, parse_mode="HTML")

    @router.message(F.text == "📉 Категории расходов")
    async def show_expense_categories(message: Message):
        categories = await db.get_categories(message.from_user.id, "expense")

        if not categories:
            await message.answer("Категории расходов не найдены. Добавьте новые категории!")
            return

        text = "📉 <b>Категории расходов:</b>\n\n"
        for cat in categories:
            default_mark = " (по умолчанию)" if cat['is_default'] else ""
            text += f"• {cat['name']}{default_mark}\n"

        await message.answer(text, parse_mode="HTML")

    # Обработка добавления новой категории
    @router.message(CategoryStates.waiting_for_new_category_name)
    async def process_new_category_name(message: Message, state: FSMContext):
        if message.text == "⏭ Пропустить":
            data = await state.get_data()
            if data.get('return_to_transaction'):
                # Возврат к выбору категории для транзакции
                trans_type = data['trans_type']
                categories = await db.get_categories(message.from_user.id, trans_type)
                keyboard = get_category_keyboard(categories)
                text = "Выберите категорию дохода:" if trans_type == "income" else "Выберите категорию расхода:"
                await state.set_state(TransactionStates.waiting_for_category)
                await message.answer(text, reply_markup=keyboard)
            else:
                await state.clear()
                await message.answer("Действие отменено.", reply_markup=get_main_menu())
            return

        category_name = message.text
        data = await state.get_data()

        # Определяем тип категории
        if data.get('return_to_transaction'):
            cat_type = data['trans_type']
        else:
            # Если пришли не из транзакции, нужно спросить тип
            await message.answer("Ошибка: не указан тип категории")
            await state.clear()
            return

        # Добавляем категорию
        success = await db.add_category(message.from_user.id, cat_type, category_name)

        if success:
            await message.answer(f"✅ Категория '{category_name}' добавлена!")

            # Возврат к выбору категории для транзакции
            if data.get('return_to_transaction'):
                categories = await db.get_categories(message.from_user.id, cat_type)
                keyboard = get_category_keyboard(categories)
                text = "Выберите категорию дохода:" if cat_type == "income" else "Выберите категорию расхода:"
                await state.set_state(TransactionStates.waiting_for_category)
                await message.answer(text, reply_markup=keyboard)
            else:
                await state.clear()
                await message.answer("Готово!", reply_markup=get_main_menu())
        else:
            await message.answer(
                "❌ Категория с таким названием уже существует. Попробуйте другое название:",
                reply_markup=get_skip_keyboard()
            )

    @router.message(F.text == "🏠 Главное меню")
    async def back_to_main(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Главное меню:", reply_markup=get_main_menu())

    dp.include_router(router)
