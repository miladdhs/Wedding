import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # ایجاد جدول کاربران
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        permission_level TEXT CHECK(permission_level IN ('admin', 'limited')) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ایجاد جدول مهمان‌ها
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS guests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        num INTEGER DEFAULT 1,
        tell TEXT,
        attendance_status TEXT CHECK(attendance_status IN ('attending', 'not_attending', 'pending')) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ایجاد جدول بازدیدها
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        visit_type TEXT DEFAULT 'بازدید',
        FOREIGN KEY (code) REFERENCES guests(code)
    )
    ''')

    # اضافه کردن کاربر پیش‌فرض
    cursor.execute('''
    INSERT OR IGNORE INTO users (username, password, full_name, permission_level)
    VALUES (?, ?, ?, ?)
    ''', ('Milad', hash_password('11051386'), 'Milad', 'admin'))

    conn.commit()
    conn.close()
    print("دیتابیس با موفقیت ایجاد شد.")

if __name__ == '__main__':
    init_db() 