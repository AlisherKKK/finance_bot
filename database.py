import aiosqlite
from datetime import datetime
from config import DATABASE_PATH


class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH

    async def create_tables(self):
        """Создание таблиц в базе данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Таблица транзакций (доходы и расходы)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Таблица долгов
            await db.execute('''
                CREATE TABLE IF NOT EXISTS debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('owe', 'lent')),
                    person_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    is_paid BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # Таблица категорий
            await db.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type TEXT NOT NULL CHECK(type IN ('income', 'expense')),
                    name TEXT NOT NULL,
                    is_default BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, type, name)
                )
            ''')

            await db.commit()

    async def add_user(self, user_id: int, username: str):
        """Добавление нового пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)',
                (user_id, username)
            )
            await db.commit()

    async def init_default_categories(self, user_id: int):
        """Инициализация категорий по умолчанию для нового пользователя"""
        from config import DEFAULT_EXPENSE_CATEGORIES, DEFAULT_INCOME_CATEGORIES

        async with aiosqlite.connect(self.db_path) as db:
            # Добавление категорий расходов
            for category in DEFAULT_EXPENSE_CATEGORIES:
                await db.execute(
                    'INSERT OR IGNORE INTO categories (user_id, type, name, is_default) VALUES (?, ?, ?, ?)',
                    (user_id, 'expense', category, 1)
                )

            # Добавление категорий доходов
            for category in DEFAULT_INCOME_CATEGORIES:
                await db.execute(
                    'INSERT OR IGNORE INTO categories (user_id, type, name, is_default) VALUES (?, ?, ?, ?)',
                    (user_id, 'income', category, 1)
                )

            await db.commit()

    async def get_categories(self, user_id: int, cat_type: str):
        """Получение категорий пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                'SELECT * FROM categories WHERE user_id = ? AND type = ? ORDER BY is_default DESC, name',
                (user_id, cat_type)
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def add_category(self, user_id: int, cat_type: str, name: str):
        """Добавление новой категории"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute(
                    'INSERT INTO categories (user_id, type, name) VALUES (?, ?, ?)',
                    (user_id, cat_type, name)
                )
                await db.commit()
                return True
            except aiosqlite.IntegrityError:
                return False

    async def delete_category(self, user_id: int, cat_type: str, name: str):
        """Удаление категории (только пользовательские, не дефолтные)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'DELETE FROM categories WHERE user_id = ? AND type = ? AND name = ? AND is_default = 0',
                (user_id, cat_type, name)
            )
            await db.commit()

    async def add_transaction(self, user_id: int, trans_type: str, amount: float,
                            category: str, description: str = None):
        """Добавление транзакции (дохода или расхода)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO transactions (user_id, type, amount, category, description)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, trans_type, amount, category, description)
            )
            await db.commit()

    async def add_debt(self, user_id: int, debt_type: str, person_name: str,
                      amount: float, description: str = None):
        """Добавление долга"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                '''INSERT INTO debts (user_id, type, person_name, amount, description)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, debt_type, person_name, amount, description)
            )
            await db.commit()

    async def get_transactions(self, user_id: int, trans_type: str = None,
                              start_date: str = None, end_date: str = None):
        """Получение транзакций пользователя с фильтрацией"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM transactions WHERE user_id = ?'
            params = [user_id]

            if trans_type:
                query += ' AND type = ?'
                params.append(trans_type)

            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)

            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)

            query += ' ORDER BY date DESC'

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_debts(self, user_id: int, is_paid: bool = None):
        """Получение долгов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = 'SELECT * FROM debts WHERE user_id = ?'
            params = [user_id]

            if is_paid is not None:
                query += ' AND is_paid = ?'
                params.append(1 if is_paid else 0)

            query += ' ORDER BY created_at DESC'

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def mark_debt_paid(self, debt_id: int):
        """Отметить долг как оплаченный"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                'UPDATE debts SET is_paid = 1, paid_at = CURRENT_TIMESTAMP WHERE id = ?',
                (debt_id,)
            )
            await db.commit()

    async def get_balance(self, user_id: int, start_date: str = None, end_date: str = None):
        """Получение баланса (доходы - расходы)"""
        async with aiosqlite.connect(self.db_path) as db:
            query = '''
                SELECT
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as total_income,
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as total_expense
                FROM transactions
                WHERE user_id = ?
            '''
            params = [user_id]

            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)

            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)

            async with db.execute(query, params) as cursor:
                row = await cursor.fetchone()
                income = row[0] or 0
                expense = row[1] or 0
                return {'income': income, 'expense': expense, 'balance': income - expense}

    async def get_category_stats(self, user_id: int, trans_type: str,
                                 start_date: str = None, end_date: str = None):
        """Получение статистики по категориям"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = '''
                SELECT category, SUM(amount) as total, COUNT(*) as count
                FROM transactions
                WHERE user_id = ? AND type = ?
            '''
            params = [user_id, trans_type]

            if start_date:
                query += ' AND date >= ?'
                params.append(start_date)

            if end_date:
                query += ' AND date <= ?'
                params.append(end_date)

            query += ' GROUP BY category ORDER BY total DESC'

            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
