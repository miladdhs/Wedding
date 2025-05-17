import sqlite3
import os
import csv
from datetime import datetime
import hashlib

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    print("در حال ایجاد دیتابیس...")
    conn = get_db_connection()
    
    # ایجاد جداول
    conn.executescript('''
        -- Create users table
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            permission_level TEXT CHECK(permission_level IN ('admin', 'limited')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create guests table
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            num INTEGER NOT NULL,
            tell TEXT,
            attendance_status TEXT CHECK(attendance_status IN ('attending', 'not_attending', 'pending')) DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Create visits table
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            visit_type TEXT DEFAULT 'page_view',
            FOREIGN KEY (code) REFERENCES guests(code)
        );
    ''')
    
    # اضافه کردن کاربر ادمین
    admin_password = hashlib.sha256('11051386'.encode()).hexdigest()
    conn.execute('''
        INSERT OR IGNORE INTO users (username, password, full_name, permission_level)
        VALUES (?, ?, ?, ?)
    ''', ('Milad', admin_password, 'میلاد', 'admin'))
    
    conn.commit()
    print("دیتابیس با موفقیت ایجاد شد.")
    return conn

def import_guests(conn):
    print("در حال وارد کردن اطلاعات مهمان‌ها...")
    try:
        with open('Data.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    conn.execute('''
                        INSERT OR IGNORE INTO guests (code, name, num, tell)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        row['CODE'],
                        row['NAME'],
                        int(row['NUM']),
                        row['TELL']
                    ))
                except Exception as e:
                    print(f"خطا در وارد کردن مهمان {row.get('NAME', 'نامشخص')}: {str(e)}")
        
        conn.commit()
        print("اطلاعات مهمان‌ها با موفقیت وارد شد.")
    except Exception as e:
        print(f"خطا در خواندن فایل CSV: {str(e)}")

def main():
    # حذف دیتابیس قبلی اگر وجود دارد
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("دیتابیس قبلی حذف شد.")
    
    # ایجاد دیتابیس جدید
    conn = init_db()
    
    # وارد کردن اطلاعات مهمان‌ها
    import_guests(conn)
    
    conn.close()
    print("\nراه‌اندازی سیستم با موفقیت انجام شد!")
    print("حالا می‌توانید سرور را با دستور 'python server.py' اجرا کنید.")

if __name__ == '__main__':
    main() 