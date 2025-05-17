import sqlite3
from datetime import datetime
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('wedding.db')
    c = conn.cursor()

    # جدول مهمان‌ها
    c.execute('''
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            num INTEGER NOT NULL,
            tell TEXT,
            attendance_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # جدول بازدیدها
    c.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            visit_type TEXT DEFAULT 'بازدید',
            FOREIGN KEY (code) REFERENCES guests(code)
        )
    ''')

    # جدول کاربران
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            permission_level TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # کاربر پیش‌فرض ادمین
    try:
        c.execute('''
            INSERT INTO users (username, password, full_name, permission_level)
            VALUES (?, ?, ?, ?)
        ''', ('admin', '21232f297a57a5a743894a0e4a801fc3', 'مدیر سیستم', 'admin'))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()
    print('دیتابیس wedding.db و جدول‌ها ساخته شدند.')

if __name__ == "__main__":
    init_db() 