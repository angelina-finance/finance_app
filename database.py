import sqlite3
from config import DB_PATH

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                email TEXT,
                is_admin INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('income', 'expense')),
                amount REAL NOT NULL,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            from utils import hash_password
            salt, pwd_hash = hash_password("admin")
            cursor.execute('''
                INSERT INTO users (username, password_hash, salt, email, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', ("admin", pwd_hash, salt, "", 1))
            conn.commit()
            print("Создан администратор: admin / admin")

def get_user_by_username(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password_hash, salt, email, is_admin FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "username": row[1],
                "password_hash": row[2],
                "salt": row[3],
                "email": row[4],
                "is_admin": bool(row[5])
            }
        return None

def create_user(username, password_hash, salt, email, is_admin=False):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (username, password_hash, salt, email, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, salt, email, 1 if is_admin else 0))
        return cursor.lastrowid

def delete_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0

def get_all_users():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, created_at, is_admin FROM users ORDER BY id")
        return cursor.fetchall()

def add_transaction(user_id, date, category, trans_type, amount, description):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (user_id, date, category, type, amount, description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, date, category, trans_type, amount, description))
        return cursor.lastrowid

def get_transactions(user_id, search_text=None, date_from=None, date_to=None, trans_type=None):
    query = "SELECT id, date, category, type, amount, description FROM transactions WHERE user_id = ?"
    params = [user_id]
    if search_text:
        query += " AND (category LIKE ? OR description LIKE ?)"
        like = f"%{search_text}%"
        params.extend([like, like])
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND date <= ?"
        params.append(date_to)
    if trans_type and trans_type != "all":
        query += " AND type = ?"
        params.append(trans_type)
    query += " ORDER BY date DESC, id DESC"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

def get_transaction_by_id(trans_id, user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, category, type, amount, description FROM transactions WHERE id = ? AND user_id = ?",
                       (trans_id, user_id))
        return cursor.fetchone()

def update_transaction(trans_id, user_id, date, category, trans_type, amount, description):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE transactions
            SET date = ?, category = ?, type = ?, amount = ?, description = ?
            WHERE id = ? AND user_id = ?
        ''', (date, category, trans_type, amount, description, trans_id, user_id))
        return cursor.rowcount > 0

def delete_transaction(trans_id, user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (trans_id, user_id))
        return cursor.rowcount > 0

def get_balance(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT SUM(CASE WHEN type = 'income' THEN amount ELSE -amount END)
            FROM transactions WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()[0]
        return result if result is not None else 0.0

def get_stats_data(user_id, date_from, date_to, group_by='day'):
    if group_by == 'day':
        query = '''
            SELECT date,
                   SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE user_id = ? AND date >= ? AND date <= ?
            GROUP BY date
            ORDER BY date
        '''
    else:
        query = '''
            SELECT category,
                   SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
                   SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
            FROM transactions
            WHERE user_id = ? AND date >= ? AND date <= ?
            GROUP BY category
            ORDER BY category
        '''
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id, date_from, date_to))
        return cursor.fetchall()