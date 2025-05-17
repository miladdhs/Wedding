# پروژه دعوتنامه عروسی

این پروژه یک وب‌سایت دعوتنامه عروسی است که با HTML، CSS و JavaScript ساخته شده است و از یک سرور پایتون برای مدیریت داده‌ها استفاده می‌کند.

## ویژگی‌ها

- طراحی زیبا و ریسپانسیو
- فونت نستعلیق برای نمایش شعر
- امکان ثبت حضور یا عدم حضور مهمانان
- نمایش اطلاعات مراسم
- انیمیشن‌های زیبا
- پشتیبانی از زبان فارسی و راست به چپ (RTL)
- سرور پایتون برای مدیریت داده‌ها

## پیش‌نیازها

- پایتون 3.8 یا بالاتر
- یک مرورگر وب مدرن
- اتصال به اینترنت (برای لود فونت‌ها و آیکون‌ها)

## نحوه استفاده

1. پروژه را کلون کنید:
```bash
git clone https://github.com/miladdhs/Wedding.git
```

2. وارد پوشه پروژه شوید:
```bash
cd Wedding
```

3. محیط مجازی پایتون را ایجاد و فعال کنید:
```bash
# در ویندوز
python -m venv venv
.\venv\Scripts\activate

# در لینوکس/مک
python3 -m venv venv
source venv/bin/activate
```

4. وابستگی‌های پایتون را نصب کنید:
```bash
pip install -r requirements.txt
```

5. سرور پایتون را اجرا کنید:
```bash
python server.py
```

6. در مرورگر خود به آدرس `http://localhost:5000` بروید.

## ساختار پروژه

```
Wedding/
├── index.html          # فایل اصلی پروژه
├── server.py          # سرور پایتون
├── requirements.txt   # وابستگی‌های پایتون
├── README.md         # مستندات پروژه
├── LICENSE          # لایسنس پروژه
└── .gitignore      # فایل‌های نادیده گرفته شده توسط گیت
```

## تکنولوژی‌های استفاده شده

### Frontend
- HTML5
- CSS3
- JavaScript
- Font Awesome (برای آیکون‌ها)
- Vazirmatn Font (فونت اصلی)
- IranNastaliq Font (فونت شعر)

### Backend
- Python 3.8+
- Flask (وب فریمورک)
- SQLite (پایگاه داده)

## نحوه مشارکت

1. پروژه را فورک کنید
2. یک شاخه جدید ایجاد کنید (`git checkout -b feature/AmazingFeature`)
3. تغییرات خود را کامیت کنید (`git commit -m 'Add some AmazingFeature'`)
4. به شاخه خود پوش کنید (`git push origin feature/AmazingFeature`)
5. یک Pull Request ایجاد کنید

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است. برای اطلاعات بیشتر به فایل `LICENSE` مراجعه کنید.

## تماس با ما

- میلاد دهقان - [@miladdhs](https://github.com/miladdhs)

## تشکر و قدردانی

- از تمام کسانی که در ساخت این پروژه مشارکت داشتند تشکر می‌کنیم
- از Font Awesome برای آیکون‌های زیبا
- از Google Fonts برای فونت Vazirmatn
- از IranNastaliq برای فونت نستعلیق 