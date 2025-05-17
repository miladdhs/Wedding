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
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT,
            num INTEGER DEFAULT 1,
            tell TEXT,
            attendance_status TEXT DEFAULT 'pending',
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # ایجاد جدول بازدیدها
    c.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            visit_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            visit_type TEXT,
            user_id INTEGER,
            FOREIGN KEY (code) REFERENCES guests(code),
            FOREIGN KEY (user_id) REFERENCES users(id)
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
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    conn = get_db_connection()
    
    # تعداد کل مهمان‌ها
    total_guests = conn.execute('SELECT COUNT(*) as count FROM guests WHERE user_id = ?', (user_id,)).fetchone()['count']
    
    # تعداد کل افراد
    total_people = conn.execute('SELECT SUM(num) as total FROM guests WHERE user_id = ?', (user_id,)).fetchone()['total'] or 0
    
    # تعداد کل افرادی که می‌آیند
    total_attending = conn.execute('''
        SELECT SUM(num) as total 
        FROM guests 
        WHERE attendance_status = 'attending' AND user_id = ?
    ''', (user_id,)).fetchone()['total'] or 0
    
    # تعداد کل بازدیدها
    total_visits = conn.execute('SELECT COUNT(*) as count FROM visits WHERE user_id = ?', (user_id,)).fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'totalGuests': total_guests,
        'totalPeople': total_people,
        'totalAttending': total_attending,
        'totalVisits': total_visits
    })

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    conn = get_db_connection()
    guests = conn.execute('SELECT * FROM guests WHERE user_id = ? ORDER BY id', (user_id,)).fetchall()
    conn.close()
    
    return jsonify([dict(guest) for guest in guests])

@app.route('/api/visits', methods=['GET'])
def get_visits():
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        conn = get_db_connection()
        visits = conn.execute('''
            SELECT v.id, v.code, v.visit_time, 
                   COALESCE(v.visit_type, 'بازدید') as visit_type, 
                   g.name as guest_name
            FROM visits v
            INNER JOIN guests g ON v.code = g.code
            WHERE v.user_id = ?
            ORDER BY v.visit_time DESC
        ''', (user_id,)).fetchall()
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
    data = request.get_json()
    code = data.get('code')
    visit_type = data.get('visit_type', 'بازدید')
    user_id = data.get('user_id')
    
    if not code or not user_id:
        return jsonify({'success': False, 'message': 'کد و شناسه کاربر الزامی است'})
    
    conn = get_db_connection()
    
    # چک کردن وجود مهمان
    guest = conn.execute('SELECT code FROM guests WHERE code = ? AND user_id = ?', (code, user_id)).fetchone()
    if not guest:
        conn.close()
        return jsonify({'success': False, 'message': 'مهمان یافت نشد'})
    
    # ثبت بازدید
    conn.execute('''
        INSERT INTO visits (code, visit_type, user_id)
        VALUES (?, ?, ?)
    ''', (code, visit_type, user_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'بازدید با موفقیت ثبت شد'})

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
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'فایل یافت نشد'})
    
    user_id = request.form.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'شناسه کاربر الزامی است'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'فایلی انتخاب نشده است'})
    
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'message': 'فقط فایل CSV پشتیبانی می‌شود'})
    
    try:
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_data = csv.DictReader(stream)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for row in csv_data:
            try:
                cursor.execute('''
                    INSERT INTO guests (code, name, num, tell, user_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    row.get('CODE', ''),
                    row.get('NAME', ''),
                    int(row.get('NUM', 1)),
                    row.get('TELL', ''),
                    user_id
                ))
            except sqlite3.IntegrityError:
                # اگر کد تکراری باشد، آن را نادیده می‌گیریم
                continue
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'اطلاعات با موفقیت وارد شد'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'خطا در وارد کردن اطلاعات: {str(e)}'
        }), 500

if __name__ == '__main__':
    init_db()  # اطمینان از ایجاد دیتابیس در شروع برنامه
    app.run(debug=True) 