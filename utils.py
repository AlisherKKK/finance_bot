def format_currency(amount: float) -> str:
    """Форматирование суммы в валюту"""
    return f"{amount:,.2f} ₸".replace(',', ' ')


def generate_report_text(period: str, balance: dict, income_stats: list, expense_stats: list) -> str:
    """Генерация текста отчета"""
    text = f"📊 <b>Отчет: {period}</b>\n\n"

    # Баланс
    text += f"💰 <b>Общий баланс:</b>\n"
    text += f"📈 Доходы: {format_currency(balance['income'])}\n"
    text += f"📉 Расходы: {format_currency(balance['expense'])}\n"
    text += f"{'➖' * 25}\n"
    text += f"💵 Итого: {format_currency(balance['balance'])}\n\n"

    # Доходы по категориям
    if income_stats:
        text += f"📈 <b>Доходы по категориям:</b>\n"
        for stat in income_stats:
            percentage = (stat['total'] / balance['income'] * 100) if balance['income'] > 0 else 0
            text += f"  • {stat['category']}: {format_currency(stat['total'])} ({percentage:.1f}%)\n"
        text += "\n"

    # Расходы по категориям
    if expense_stats:
        text += f"📉 <b>Расходы по категориям:</b>\n"
        for stat in expense_stats:
            percentage = (stat['total'] / balance['expense'] * 100) if balance['expense'] > 0 else 0
            text += f"  • {stat['category']}: {format_currency(stat['total'])} ({percentage:.1f}%)\n"
        text += "\n"

    if not income_stats and not expense_stats:
        text += "Нет данных за выбранный период."

    return text
