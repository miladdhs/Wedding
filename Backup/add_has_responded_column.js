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
      const hasRespondedColumn = columns.some(col => col.name === 'has_responded');
      if (hasRespondedColumn) {
        console.log("Column 'has_responded' already exists.");
        db.close();
      } else {
        db.run("ALTER TABLE guests ADD COLUMN has_responded BOOLEAN DEFAULT 0", (err) => {
          if (err) {
            console.error('Error adding column:', err.message);
          } else {
            console.log("Column 'has_responded' added successfully.");
          }
          db.close();
        });
      }
    });
  });
}); 