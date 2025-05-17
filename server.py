from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__, static_folder='.')
CORS(app)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open('database.sql') as f:
        conn.executescript(f.read())
    conn.close()

# Add JWT secret key
JWT_SECRET = "your-secret-key-here"  # Change this to a secure secret key

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(token):
    return None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/admin')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'نام کاربری و رمز عبور الزامی است'})
    
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
    
    return jsonify({'success': False, 'message': 'نام کاربری یا رمز عبور اشتباه است'})

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
    conn = get_db_connection()
    visits = conn.execute('''
        SELECT v.*, g.name 
        FROM visits v 
        LEFT JOIN guests g ON v.code = g.code 
        ORDER BY v.visit_time DESC
    ''').fetchall()
    conn.close()
    
    return jsonify([dict(visit) for visit in visits])

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
        return jsonify({'error': 'وضعیت نامعتبر است'}), 400
    
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE code = ?', (code,)).fetchone()
    
    if not guest:
        conn.close()
        return jsonify({'error': 'مهمان یافت نشد'}), 404
    
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
        return jsonify({'error': 'مهمان یافت نشد'}), 404
    
    conn.execute('UPDATE guests SET attendance_status = ? WHERE code = ?', ('pending', code))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'وضعیت به نظر نداده تغییر کرد'})

@app.route('/api/record-visit/<code>', methods=['POST'])
def record_visit(code):
    conn = get_db_connection()
    guest = conn.execute('SELECT * FROM guests WHERE code = ?', (code,)).fetchone()
    
    if not guest:
        conn.close()
        return jsonify({'error': 'مهمان یافت نشد'}), 404
    
    # ثبت بازدید جدید
    conn.execute('''
        INSERT INTO visits (code, visit_time, visit_type)
        VALUES (?, ?, ?)
    ''', (
        code,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'page_view'
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'بازدید با موفقیت ثبت شد'})

if __name__ == '__main__':
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=True) 