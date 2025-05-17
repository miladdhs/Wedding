const express = require('express');
const path = require('path');
const db = require('./database');
const app = express();
const port = 3001;

// Middleware for parsing JSON
app.use(express.json());

// Serve static files
app.use(express.static(path.join(__dirname)));

// API endpoint to get all guests
app.get('/api/guests', async (req, res) => {
    try {
        const guests = await db.getAllGuests();
        res.json(guests);
    } catch (error) {
        res.status(500).json({ error: 'خطا در دریافت اطلاعات' });
    }
});

// API endpoint to get guest by code
app.get('/api/guest/:code', async (req, res) => {
    try {
        const guest = await db.getGuestByCode(req.params.code, true);
        if (guest) {
            res.json(guest);
        } else {
            res.status(404).json({ error: 'مهمان یافت نشد' });
        }
    } catch (error) {
        res.status(500).json({ error: 'خطا در دریافت اطلاعات' });
    }
});

// API endpoint to get visit status
app.get('/api/visits', async (req, res) => {
    try {
        const visits = await db.getVisitStatus();
        res.json(visits);
    } catch (error) {
        res.status(500).json({ error: 'خطا در دریافت اطلاعات' });
    }
});

// API endpoint to get attendance status
app.get('/api/attendance', async (req, res) => {
    try {
        const status = await db.getAttendanceStatus();
        res.json(status);
    } catch (error) {
        res.status(500).json({ error: 'خطا در دریافت اطلاعات' });
    }
});

// API endpoint to update attendance status
app.post('/api/attendance/:code', async (req, res) => {
    try {
        const { status } = req.body;
        const { code } = req.params;

        if (!code) {
            return res.status(400).json({ error: 'کد مهمان الزامی است' });
        }

        if (!['attending', 'not_attending', 'pending'].includes(status)) {
            return res.status(400).json({ error: 'وضعیت نامعتبر است' });
        }

        // بررسی وجود مهمان - بدون ثبت بازدید
        const guest = await db.getGuestByCode(code, false);
        if (!guest) {
            return res.status(404).json({ error: 'مهمان یافت نشد' });
        }

        // آپدیت وضعیت حضور بدون ثبت بازدید
        await db.updateAttendanceStatus(code, status);
        
        res.json({ 
            message: 'وضعیت با موفقیت بروزرسانی شد',
            status: status,
            guest: guest
        });
    } catch (error) {
        console.error('Error updating attendance status:', error);
        res.status(500).json({ error: 'خطا در بروزرسانی وضعیت' });
    }
});

// API endpoint برای دریافت آمار کلی
app.get('/api/statistics', async (req, res) => {
    try {
        const stats = await db.getStatistics();
        res.json(stats);
    } catch (error) {
        console.error('Error getting statistics:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Debug endpoint to show database status
app.get('/api/debug', async (req, res) => {
    try {
        const guests = await db.getAllGuests();
        const count = await db.getRecordCount();
        res.json({
            totalRecords: count,
            records: guests,
            message: 'اطلاعات از دیتابیس SQLite خوانده شده است'
        });
    } catch (error) {
        res.status(500).json({ error: 'خطا در دریافت اطلاعات' });
    }
});

// API endpoint to record a 'change opinion' visit
app.post('/api/change-opinion/:code', async (req, res) => {
    try {
        const { code } = req.params;
        const guest = await db.getGuestByCode(code, false);
        if (!guest) {
            return res.status(404).json({ error: 'مهمان یافت نشد' });
        }
        // تغییر وضعیت حضور به "نظر نداده"
        await db.updateAttendanceStatus(code);
        res.json({ message: 'تغییر نظر ثبت شد و وضعیت به "نظر نداده" تغییر کرد' });
    } catch (error) {
        res.status(500).json({ error: 'خطا در ثبت تغییر نظر' });
    }
});

// Admin page route
app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'admin.html'));
});

// Status page route
app.get('/status', (req, res) => {
    res.sendFile(path.join(__dirname, 'status.html'));
});

// Handle all routes
app.get('/:code', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Initialize database and start server
async function startServer() {
    try {
        await db.initialize();
        app.listen(port, () => {
            console.log(`Server running at http://localhost:${port}`);
            console.log(`Admin panel: http://localhost:${port}/admin`);
            console.log(`Status page: http://localhost:${port}/status`);
            console.log(`Debug endpoint: http://localhost:${port}/api/debug`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

startServer(); 