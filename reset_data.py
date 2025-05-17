import sqlite3
from datetime import datetime

def reset_data():
    conn = sqlite3.connect('wedding.db')
    cursor = conn.cursor()
    
    try:
        # غیرفعال کردن محدودیت‌های کلید خارجی
        cursor.execute('PRAGMA foreign_keys = OFF')
        
        # حذف جدول‌های guests و visits
        cursor.execute('DROP TABLE IF EXISTS visits')
        cursor.execute('DROP TABLE IF EXISTS guests')
        
        # فعال کردن مجدد محدودیت‌های کلید خارجی
        cursor.execute('PRAGMA foreign_keys = ON')
        
        # ساخت مجدد جدول guests
        cursor.execute('''
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
        
        # ساخت مجدد جدول visits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                visit_type TEXT DEFAULT 'بازدید',
                FOREIGN KEY (code) REFERENCES guests(code)
            )
        ''')
        
        conn.commit()
        print("داده‌های بازدید و حضور با موفقیت پاک شدند.")
        print("جدول‌های guests و visits با ساختار جدید ساخته شدند.")
        print("جدول users و اطلاعات کاربران حفظ شد.")
        
    except Exception as e:
        print("خطا در ریست کردن داده‌ها:", str(e))
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    reset_data() 