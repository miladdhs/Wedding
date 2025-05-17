import sqlite3
from datetime import datetime

def add_test_data():
    conn = sqlite3.connect('wedding.db')
    cursor = conn.cursor()
    
    # اضافه کردن مهمان‌های تستی
    test_guests = [
        ('100100', 'MMD', 2, '9945137621', 'pending'),
        ('101244', 'HOSSEIN', 3, '9945137622', 'pending'),
        ('102144', 'YALDA', 4, '9945137623', 'pending'),
        ('103278', 'FATI', 6, '9945137624', 'pending'),
        ('104574', 'BARAN', 1, '9945137625', 'pending'),
        ('105297', 'MERSA', 2, '9945137626', 'pending'),
        ('106369', 'MEHRAD', 5, '9945137627', 'pending'),
        ('107659', 'ASIYEH', 2, '9945137628', 'pending'),
        ('108926', 'MILAD', 2, '9945137629', 'pending')
    ]
    
    cursor.executemany('''
        INSERT OR REPLACE INTO guests (code, name, num, tell, attendance_status)
        VALUES (?, ?, ?, ?, ?)
    ''', test_guests)
    
    # اضافه کردن بازدیدهای تستی
    test_visits = [
        ('100100', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'بازدید'),
        ('101244', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'بازدید'),
        ('102144', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'بازدید'),
        ('103278', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'بازدید'),
        ('104574', datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'بازدید')
    ]
    try:
        cursor.executemany('''
            INSERT INTO visits (code, visit_time, visit_type)
            VALUES (?, ?, ?)
        ''', test_visits)
    except Exception as e:
        print('خطا در افزودن بازدیدها:', e)
    
    conn.commit()
    conn.close()
    print("داده‌های تستی با موفقیت اضافه شدند.")

if __name__ == "__main__":
    add_test_data() 