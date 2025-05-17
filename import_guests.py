import sqlite3
import csv

db_path = 'database.db'
csv_path = 'Data.csv'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open(csv_path, encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cursor.execute("""
            INSERT OR IGNORE INTO guests (code, name, num, tell, attendance_status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            row['CODE'],
            row['NAME'],
            int(row['NUM']),
            row['TELL'],
            'pending'  # وضعیت پیش‌فرض
        ))

conn.commit()
conn.close()
print("وارد کردن داده‌ها با موفقیت انجام شد.") 