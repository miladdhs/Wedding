import sqlite3
from datetime import datetime

def test_visits_api():
    try:
        conn = sqlite3.connect('wedding.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # بررسی محتوای جدول guests
        print("\n=== محتوای جدول guests ===")
        try:
            guests = cursor.execute('SELECT * FROM guests').fetchall()
            print("تعداد مهمان‌ها:", len(guests))
            for guest in guests:
                print(dict(guest))
        except Exception as e:
            print("خطا در خواندن جدول guests:", str(e))
        
        # بررسی محتوای جدول visits
        print("\n=== محتوای جدول visits ===")
        try:
            visits = cursor.execute('SELECT * FROM visits').fetchall()
            print("تعداد بازدیدها:", len(visits))
            for visit in visits:
                print(dict(visit))
        except Exception as e:
            print("خطا در خواندن جدول visits:", str(e))
        
        # تست کوئری بازدیدها
        print("\n=== تست کوئری بازدیدها ===")
        try:
            visits = cursor.execute('''
                SELECT v.id, v.code, v.visit_time, 
                       COALESCE(v.visit_type, 'بازدید') as visit_type, 
                       g.name as guest_name
                FROM visits v
                LEFT JOIN guests g ON v.code = g.code
                ORDER BY v.visit_time DESC
            ''').fetchall()
            print("تعداد بازدیدها:", len(visits))
            for visit in visits:
                print(dict(visit))
        except Exception as e:
            print("خطا در کوئری بازدیدها:", str(e))
        
        # بررسی ساختار جدول visits
        print("\n=== ساختار جدول visits ===")
        try:
            cursor.execute("PRAGMA table_info(visits)")
            columns = cursor.fetchall()
            for col in columns:
                print(col)
        except Exception as e:
            print("خطا در بررسی ساختار جدول visits:", str(e))
        
        # بررسی ساختار جدول guests
        print("\n=== ساختار جدول guests ===")
        try:
            cursor.execute("PRAGMA table_info(guests)")
            columns = cursor.fetchall()
            for col in columns:
                print(col)
        except Exception as e:
            print("خطا در بررسی ساختار جدول guests:", str(e))
        
        conn.close()
        
    except Exception as e:
        print("خطای کلی:", str(e))

if __name__ == "__main__":
    test_visits_api() 