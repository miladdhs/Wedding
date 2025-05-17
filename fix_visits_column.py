import sqlite3

conn = sqlite3.connect('wedding.db')
cursor = conn.cursor()

# اضافه کردن فیلد visit_type اگر وجود ندارد
try:
    cursor.execute("ALTER TABLE visits ADD COLUMN visit_type TEXT DEFAULT 'بازدید'")
    print("ستون visit_type اضافه شد.")
except Exception as e:
    print("ستون visit_type قبلاً وجود دارد یا خطا:", e)

conn.commit()
conn.close() 