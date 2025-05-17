from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime
import hashlib
import csv
import io

app = Flask(__name__, static_folder='.')
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('wedding.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # ایجاد جدول حضور
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            num_guests INTEGER DEFAULT 1,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ایجاد جدول بازدیدها
    c.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            visit_type TEXT,
            FOREIGN KEY (code) REFERENCES guests(code)
        )
    ''')
    
    # ایجاد جدول کاربران
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            permission_level TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ایجاد کاربر پیش‌فرض ادمین
    try:
        c.execute('''
            INSERT INTO users (username, password, full_name, permission_level)
            VALUES (?, ?, ?, ?)
        ''', ('admin', hash_password('admin123'), 'مدیر سیستم', 'admin'))
    except sqlite3.IntegrityError:
        # اگر کاربر قبلاً وجود داشته باشد، این خطا را نادیده می‌گیریم
        pass
    
    conn.commit()
    conn.close()

# Add JWT secret key
JWT_SECRET = "your-secret-key-here"  # Change this to a secure secret key

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(token):
    return None

@app.route('/')
def index():
    return send_from_directory('.', 'error.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'نام کاربری و رمز عبور الزامی است'
            })
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and user['password'] == hash_password(password):
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'permission_level': user['permission_level']
                }
            })
        
        return jsonify({
            'success': False,
            'message': 'نام کاربری یا رمز عبور اشتباه است'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    conn = get_db_connection()
    
    # تعداد کل مهمان‌ها
    total_guests = conn.execute('SELECT COUNT(*) as count FROM guests').fetchone()['count']
    
    # تعداد کل افراد
    total_people = conn.execute('SELECT SUM(num) as total FROM guests').fetchone()['total'] or 0
    
    # تعداد کل افرادی که می‌آیند
    total_attending = conn.execute('''
        SELECT SUM(num) as total 
        FROM guests 
        WHERE attendance_status = 'attending'
    ''').fetchone()['total'] or 0
    
    # تعداد کل بازدیدها
    total_visits = conn.execute('SELECT COUNT(*) as count FROM visits').fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'totalGuests': total_guests,
        'totalPeople': total_people,
        'totalAttending': total_attending,
        'totalVisits': total_visits
    })

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests ORDER BY id').fetchall()
    conn.close()
    
    return jsonify([dict(guest) for guest in guests])

@app.route('/api/visits', methods=['GET'])
def get_visits():
    try:
        conn = get_db_connection()
        visits = conn.execute('''
            SELECT v.id, v.code, v.visit_time, 
                   COALESCE(v.visit_type, 'بازدید') as visit_type, 
                   g.name as guest_name
            FROM visits v
            INNER JOIN guests g ON v.code = g.code
            ORDER BY v.visit_time DESC
        ''').fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'visits': [dict(zip(visit.keys(), visit)) for visit in visits]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, full_name, permission_level, created_at FROM users').fetchall()
    conn.close()
    
    return jsonify([dict(user) for user in users])

@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    
    if not all(k in data for k in ['username', 'password', 'full_name', 'permission_level']):
        return jsonify({'success': False, 'message': 'تمام فیلدها الزامی هستند'})
    
    conn = get_db_connection()
    
    # چک کردن تکراری نبودن نام کاربری
    existing_user = conn.execute('SELECT id FROM users WHERE username = ?', (data['username'],)).fetchone()
    if existing_user:
        conn.close()
        return jsonify({'success': False, 'message': 'این نام کاربری قبلاً استفاده شده است'})
    
    # اضافه کردن کاربر جدید
    conn.execute('''
        INSERT INTO users (username, password, full_name, permission_level, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['username'],
        hash_password(data['password']),
        data['full_name'],
        data['permission_level'],
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'کاربر با موفقیت اضافه شد'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    
    # چک کردن وجود کاربر
    user = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'کاربر یافت نشد'})
    
    # حذف کاربر
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'کاربر با موفقیت حذف شد'})

@app.route('/<code>')
def guest_page(code):
    return send_from_directory('.', 'index.html')

@app.route('/api/guest/<code>')
def get_guest_info(code):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE code = ?', (code,)).fetchone()
    conn.close()
    
    if guest:
        return jsonify(dict(guest))
    else:
        return jsonify({'error': 'مهمان یافت نشد'}), 404

@app.route('/api/attendance/<code>', methods=['POST'])
def update_attendance(code):
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['attending', 'not_attending']:
        return jsonify({'success': False, 'error': 'وضعیت نامعتبر است'}), 400
    
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE code = ?', (code,)).fetchone()
    
    if not guest:
        conn.close()
        return jsonify({'success': False, 'error': 'مهمان یافت نشد'}), 404
    
    conn.execute('UPDATE guests SET attendance_status = ? WHERE code = ?', (status, code))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'وضعیت حضور با موفقیت ثبت شد'})

@app.route('/api/change-opinion/<code>', methods=['POST'])
def change_opinion(code):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE code = ?', (code,)).fetchone()
    
    if not guest:
        conn.close()
        return jsonify({'success': False, 'error': 'مهمان یافت نشد'}), 404
    
    conn.execute('UPDATE guests SET attendance_status = ? WHERE code = ?', ('pending', code))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'وضعیت به نظر نداده تغییر کرد'})

@app.route('/api/record-visit', methods=['POST'])
def record_visit():
    try:
        code = request.args.get('code')
        if not code:
            return jsonify({'success': False, 'error': 'کد مهمان الزامی است'}), 400

        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO visits (code, visit_time, visit_type)
            VALUES (?, ?, ?)
        ''', (code, datetime.now(), 'بازدید'))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/attendance', methods=['POST'])
def record_attendance():
    try:
        data = request.json
        status = data.get('status')
        
        if status not in ['attending', 'not_attending']:
            return jsonify({'success': False, 'error': 'وضعیت نامعتبر است'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO attendance (status, created_at)
            VALUES (?, ?)
        ''', (status, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'وضعیت حضور با موفقیت ثبت شد'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/attendance/stats', methods=['GET'])
def get_stats():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # تعداد کل پاسخ‌ها
        c.execute('SELECT COUNT(*) as total FROM attendance')
        total = c.fetchone()['total']
        
        # تعداد افرادی که می‌آیند
        c.execute('SELECT COUNT(*) as attending FROM attendance WHERE status = ?', ('attending',))
        attending = c.fetchone()['attending']
        
        # تعداد افرادی که نمی‌آیند
        c.execute('SELECT COUNT(*) as not_attending FROM attendance WHERE status = ?', ('not_attending',))
        not_attending = c.fetchone()['not_attending']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'attending': attending,
                'not_attending': not_attending
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/import-csv', methods=['POST'])
def import_csv():
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'فایل CSV انتخاب نشده است'
            })
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'فایل CSV انتخاب نشده است'
            })
        
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'message': 'لطفا فقط فایل CSV آپلود کنید'
            })
        
        # Read the CSV file
        stream = io.StringIO(file.stream.read().decode("UTF-8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get the column names from the CSV file
        fieldnames = csv_reader.fieldnames
        if not fieldnames:
            return jsonify({
                'success': False,
                'message': 'فایل CSV خالی است'
            })
        
        # Required fields
        required_fields = ['ID', 'NAME', 'NUM', 'TELL', 'CODE']
        missing_fields = [field for field in required_fields if field not in fieldnames]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'فیلدهای الزامی در فایل CSV وجود ندارند: {", ".join(missing_fields)}'
            })
        
        # Process each row
        success_count = 0
        error_count = 0
        
        for row in csv_reader:
            try:
                # Clean and validate the data
                name = row['NAME'].strip()
                phone = row['TELL'].strip()
                num_guests = int(row['NUM'])
                code = row['CODE'].strip()
                
                if not name or not phone or not code:
                    error_count += 1
                    continue
                
                # Insert into database
                cursor.execute('''
                    INSERT INTO guests (code, name, num, tell, attendance_status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (code, name, num_guests, phone, 'pending'))
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                print(f"Error processing row: {e}")
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'تعداد {success_count} مهمان با موفقیت وارد شد. تعداد {error_count} خطا در وارد کردن.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در پردازش فایل: {str(e)}'
        }), 500

if __name__ == '__main__':
    init_db()  # اطمینان از ایجاد دیتابیس در شروع برنامه
    app.run(debug=True) 