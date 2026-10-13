# Phishing Email Analyzer

A Python desktop application for analyzing local `.eml` files and generating professional PDF reports (both fillable and print-ready).

## Features
- Parses `.eml` files locally (no data sent externally)
- Extracts standard email headers, URLs, and attachment hashes (MD5, SHA1, SHA256)
- Extracts SPF, DKIM, and DMARC results
- Generates two types of PDF reports:
  - Print-ready report (with blank spaces for handwriting)
  - Interactive fillable report (with editable form fields)
- Supports Persian RTL text via `Vazirmatn` font

## راهنمای نصب و اجرا در ویندوز ۱۱ (Windows 11)

### پیش‌نیازها
مطمئن شوید که **Python 3.10** یا بالاتر روی سیستم شما نصب شده است.

### مراحل نصب با استفاده از PowerShell

۱. **باز کردن PowerShell:**
منوی استارت را باز کرده و `PowerShell` را جستجو و اجرا کنید.

۲. **ورود به مسیر پروژه:**
با استفاده از دستور `cd` به پوشه پروژه بروید:
```powershell
cd مسیر\به\پوشه\پروژه\phishing_email_analyzer
```

۳. **ساخت محیط مجازی (Virtual Environment):**
این کار باعث می‌شود کتابخانه‌های پروژه جدا از کتابخانه‌های سیستم نصب شوند:
```powershell
python -m venv venv
```

۴. **فعال‌سازی محیط مجازی:**
برای استفاده از محیط مجازی ساخته شده، دستور زیر را اجرا کنید:
```powershell
.\venv\Scripts\Activate.ps1
```
*نکته:* اگر با خطای اجرای اسکریپت مواجه شدید، ابتدا دستور `Set-ExecutionPolicy Unrestricted -Scope CurrentUser` را اجرا کنید و سپس دوباره تلاش کنید.

۵. **نصب نیازمندی‌ها (Dependencies):**
```powershell
pip install -r requirements.txt
```

### اجرای برنامه

برای اجرای برنامه، در حالی که محیط مجازی فعال است، دستور زیر را وارد کنید:
```powershell
python phishing_email_analyzer.py
```

### راهنمای استفاده

۱. پس از اجرای برنامه، پنجره‌ای باز می‌شود.
۲. با کلیک روی دکمه `Browse` در قسمت **Select EML File**، فایل `.eml` مورد نظر را انتخاب کنید.
۳. با کلیک روی دکمه `Browse` دوم، پوشه مقصد برای ذخیره خروجی‌ها را انتخاب کنید.
۴. روی دکمه **Analyze & Generate Reports** کلیک کنید.
۵. دو فایل PDF در مسیر انتخاب شده ایجاد خواهد شد.

### محدودیت‌ها و نکات امنیتی
- **امنیت فایل‌های مخرب:** این برنامه به صورت محلی کار می‌کند. به هیچ وجه ضمیمه‌های ایمیل اجرا نمی‌شوند و لینک‌ها باز نمی‌شوند. هیچ داده‌ای به اینترنت یا API های خارجی ارسال نمی‌گردد.
- **پشتیبانی زبان فارسی در فرم‌های تعاملی PDF:** در فایل تعاملی (Fillable)، فرم‌ها از طریق ReportLab ساخته می‌شوند. بسته به نرم‌افزار پی‌دی‌اف خوان (مانند Adobe Acrobat یا Foxit Reader) ممکن است تایپ فارسی راست-به-چپ (RTL) در فیلدها به درستی نمایش داده نشود یا حروف جدا از هم ظاهر شوند. با این حال، نسخه قابل چاپ (Print) به خوبی فارسی را پشتیبانی می‌کند.
- **صحت داده‌ها:** اطلاعات استخراج شده از هدرهای `Received` مانند آدرس IP و Hostname تضمین‌کننده منبع اصلی نیستند و قابلیت جعل دارند (Unverified).
