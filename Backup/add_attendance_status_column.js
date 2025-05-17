const sqlite3 = require('sqlite3').verbose();

const db = new sqlite3.Database('wedding.db');

db.serialize(() => {
  db.get("PRAGMA table_info(guests)", (err, row) => {
    if (err) {
      console.error('Error reading table info:', err.message);
      db.close();
      return;
    }
    db.all("PRAGMA table_info(guests)", (err, columns) => {
      if (err) {
        console.error('Error reading table info:', err.message);
        db.close();
        return;
      }
      const hasAttendanceStatus = columns.some(col => col.name === 'attendance_status');
      if (hasAttendanceStatus) {
        console.log("Column 'attendance_status' already exists.");
        db.close();
      } else {
        db.run("ALTER TABLE guests ADD COLUMN attendance_status TEXT", (err) => {
          if (err) {
            console.error('Error adding column:', err.message);
          } else {
            console.log("Column 'attendance_status' added successfully.");
          }
          db.close();
        });
      }
    });
  });
}); 