const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const { parse } = require('csv-parse/sync');
const path = require('path');

// ایجاد اتصال به دیتابیس
const db = new sqlite3.Database('wedding.db');

// ایجاد جدول مهمانان
function createTable() {
    return new Promise((resolve, reject) => {
        db.run(`
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY,
                name TEXT,
                num INTEGER,
                tell TEXT,
                code TEXT UNIQUE,
                attendance_status TEXT DEFAULT NULL,
                has_responded INTEGER DEFAULT 0
            )
        `, (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
}

// ایجاد جدول بازدیدها
function createVisitsTable() {
    return new Promise((resolve, reject) => {
        db.run(`
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                name TEXT,
                visit_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_status_change INTEGER DEFAULT 0
            )
        `, (err) => {
            if (err) reject(err);
            else resolve();
        });
    });
}

// ثبت بازدید جدید
function recordVisit(code, name) {
    return new Promise((resolve, reject) => {
        db.run(
            'INSERT INTO visits (code, name, visit_time) VALUES (?, ?, datetime("now", "localtime"))',
            [code, name],
            (err) => {
                if (err) reject(err);
                else resolve();
            }
        );
    });
}

// ثبت بازدید با تغییر وضعیت
function recordStatusChangeVisit(code, name) {
    return new Promise((resolve, reject) => {
        db.run(
            'INSERT INTO visits (code, name, visit_time, is_status_change) VALUES (?, ?, datetime("now", "localtime"), 1)',
            [code, name],
            (err) => {
                if (err) reject(err);
                else resolve();
            }
        );
    });
}

// دریافت مهمان با کد و ثبت بازدید
async function getGuestByCode(code, shouldRecordVisit = true) {
    return new Promise((resolve, reject) => {
        db.get('SELECT * FROM guests WHERE code = ?', [code], async (err, guest) => {
            if (err) {
                reject(err);
            } else if (guest) {
                try {
                    if (shouldRecordVisit) {
                        await recordVisit(guest.code, guest.name);
                    }
                    resolve(guest);
                } catch (error) {
                    reject(error);
                }
            } else {
                resolve(null);
            }
        });
    });
}

// دریافت وضعیت بازدیدها
function getVisitStatus() {
    return new Promise((resolve, reject) => {
        db.all(`
            SELECT 
                code,
                name,
                visit_time,
                CASE 
                    WHEN is_status_change = 1 THEN 'تغییر نظر'
                    ELSE 'بازدید'
                END as visit_type
            FROM visits
            ORDER BY visit_time DESC
        `, (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
}

// آپدیت وضعیت حضور
function updateAttendanceStatus(code, status) {
    return new Promise((resolve, reject) => {
        db.run(
            'UPDATE guests SET attendance_status = ?, has_responded = 1 WHERE code = ?',
            [status, code],
            (err) => {
                if (err) reject(err);
                else resolve();
            }
        );
    });
}

// دریافت وضعیت حضور
function getAttendanceStatus() {
    return new Promise((resolve, reject) => {
        db.all(`
            SELECT 
                g.id,
                g.code,
                g.name,
                g.num,
                g.tell,
                g.attendance_status,
                CASE 
                    WHEN g.attendance_status = 'attending' THEN 'می‌آید'
                    WHEN g.attendance_status = 'not_attending' THEN 'نمی‌آید'
                    ELSE 'نظر نداده'
                END as status_text
            FROM guests g
            ORDER BY g.id
        `, (err, rows) => {
            if (err) {
                console.error('Error in getAttendanceStatus:', err);
                reject(err);
            } else {
                resolve(rows);
            }
        });
    });
}

// خواندن داده‌ها از CSV و ذخیره در دیتابیس
async function importFromCSV() {
    try {
        const fileContent = fs.readFileSync('Data.csv', 'utf-8');
        const records = parse(fileContent, {
            columns: true,
            skip_empty_lines: true,
            trim: true,
            delimiter: ','
        });
        
        console.log(`Found ${records.length} records in CSV file`);
        
        // پاک کردن داده‌های قبلی
        await new Promise((resolve, reject) => {
            db.run('DELETE FROM guests', (err) => {
                if (err) reject(err);
                else resolve();
            });
        });

        // درج داده‌های جدید
        const stmt = db.prepare('INSERT INTO guests (id, name, num, tell, code) VALUES (?, ?, ?, ?, ?)');
        
        for (const record of records) {
            try {
                await new Promise((resolve, reject) => {
                    stmt.run(
                        parseInt(record.ID),
                        record.NAME,
                        parseInt(record.NUM),
                        record.TELL,
                        record.CODE,
                        (err) => {
                            if (err) {
                                console.error('Error inserting record:', record, err);
                                reject(err);
                            } else {
                                resolve();
                            }
                        }
                    );
                });
            } catch (error) {
                console.error('Error processing record:', record, error);
            }
        }
        
        stmt.finalize();
        console.log(`Successfully imported ${records.length} records`);
        
    } catch (error) {
        console.error('Error importing data:', error);
        throw error;
    }
}

// دریافت همه مهمانان
function getAllGuests() {
    return new Promise((resolve, reject) => {
        db.all('SELECT * FROM guests', (err, rows) => {
            if (err) reject(err);
            else resolve(rows);
        });
    });
}

// دریافت تعداد رکوردهای موجود در دیتابیس
function getRecordCount() {
    return new Promise((resolve, reject) => {
        db.get('SELECT COUNT(*) as count FROM guests', (err, row) => {
            if (err) reject(err);
            else resolve(row.count);
        });
    });
}

// نمایش محتوای دیتابیس
async function showDatabaseContents() {
    try {
        const guests = await getAllGuests();
        const count = await getRecordCount();
        console.log('\nDatabase Contents:');
        console.log('------------------');
        console.log(`Total Records: ${count}`);
        console.log('\nRecords:');
        guests.forEach(guest => {
            console.log(`ID: ${guest.id}, Name: ${guest.name}, Num: ${guest.num}, Tell: ${guest.tell}, Code: ${guest.code}`);
        });
        console.log('------------------\n');
    } catch (error) {
        console.error('Error showing database contents:', error);
    }
}

// راه‌اندازی اولیه دیتابیس
async function initialize() {
    try {
        await createTable();
        await createVisitsTable();
        
        // پاک کردن جدول بازدیدها
        await new Promise((resolve, reject) => {
            db.run('DELETE FROM visits', (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
        
        await importFromCSV();
        await showDatabaseContents();
    } catch (error) {
        console.error('Error initializing database:', error);
        throw error;
    }
}

// دریافت آمار کلی
function getStatistics() {
    return new Promise((resolve, reject) => {
        db.get(`
            SELECT 
                COUNT(*) as totalGuests,
                SUM(num) as totalPeople,
                SUM(CASE WHEN attendance_status = 'attending' THEN 1 ELSE 0 END) as totalAttending,
                (SELECT COUNT(*) FROM visits) as totalVisits
            FROM guests
        `, (err, stats) => {
            if (err) {
                console.error('Error getting statistics:', err);
                reject(err);
            } else {
                resolve(stats);
            }
        });
    });
}

module.exports = {
    createTable,
    createVisitsTable,
    importFromCSV,
    getAllGuests,
    getGuestByCode,
    getRecordCount,
    getVisitStatus,
    getAttendanceStatus,
    updateAttendanceStatus,
    showDatabaseContents,
    initialize,
    getStatistics,
    recordVisit,
    recordStatusChangeVisit
}; 