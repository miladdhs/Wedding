import sqlite3

def check_database():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    print("=== محتوای جدول مهمان‌ها ===")
    cursor.execute("SELECT * FROM guests")
    guests = cursor.fetchall()
    for guest in guests:
        print(f"ID: {guest[0]}, Code: {guest[1]}, Name: {guest[2]}, Num: {guest[3]}, Tell: {guest[4]}, Status: {guest[5]}")
    
    print("\n=== محتوای جدول بازدیدها ===")
    cursor.execute("SELECT * FROM visits")
    visits = cursor.fetchall()
    for visit in visits:
        print(f"ID: {visit[0]}, Code: {visit[1]}, Time: {visit[2]}, Type: {visit[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_database() 