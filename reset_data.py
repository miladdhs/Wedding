import sqlite3

def reset_data():
    conn = sqlite3.connect('wedding.db')
    cursor = conn.cursor()
    try:
        # پاک کردن همه داده‌های مهمانان و بازدیدها
        cursor.execute('DELETE FROM visits')
        cursor.execute('DELETE FROM guests')
        conn.commit()
        print("همه مهمانان و بازدیدها پاک شدند. ساختار جدول‌ها دست‌نخورده باقی ماند.")
    except Exception as e:
        print("خطا در ریست کردن داده‌ها:", str(e))
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    reset_data() 