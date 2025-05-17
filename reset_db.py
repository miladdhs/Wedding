import sqlite3

conn = sqlite3.connect('wedding.db')
cursor = conn.cursor()

# وضعیت حضور همه مهمان‌ها را به NULL برگردان
cursor.execute("UPDATE guests SET attendance_status = NULL")

# جدول بازدیدها را خالی کن
cursor.execute("DELETE FROM visits")

conn.commit()
conn.close()

print('وضعیت حضور همه مهمان‌ها ریست شد و جدول بازدیدها پاک شد. کاربران دست‌نخورده باقی ماندند.') 