# 🏨 Hotel Management System — Project 11
**Nguyen Phuong Linh - 11247186**

---
This project is a Hotel Management System designed to simplify and automate daily hotel operations such as room booking, guest management, and billing. The system provides an intuitive interface and integrates a database to ensure efficient data handling and improved service quality. It is suitable for learning purposes as well as small-scale hotel management applications.

## 📁 Project Structure

```
hotel_management/
├── sql/
│   ├── schema.sql          ← Tables, indexes, views, procedures, triggers, users
│   └── sample_data.sql     ← 5–10 rows per table (Rooms×20, Guests×10, etc.)
└── python/
    ├── main.py             ← GUI Application (Tkinter, Santorini theme)
    ├── database.py         ← All DB queries & helpers (mysql-connector)
    └── requirements.txt
```

---

## ⚙️ Setup

### 1. MySQL Database

```sql
-- In MySQL Workbench or terminal:
SOURCE /path/to/sql/schema.sql;
SOURCE /path/to/sql/sample_data.sql;
```

### 2. Python Dependencies

```bash
pip install mysql-connector-python
```

### 3. Configure Connection

Edit `python/database.py`:
```python
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",       # ← Your MySQL user
    "password": "yourpass",   # ← Your MySQL password
    "database": "hotel_management",
}
```

### 4. Run the App

```bash
cd python/
python main.py
```

> **Demo Mode**: If MySQL is not connected, the app runs with demo data automatically.

---

## 🗃️ Database Objects

| Object | Name | Purpose |
|--------|------|---------|
| Table | Guests | Guest profiles |
| Table | Rooms | Room info & pricing |
| Table | Bookings | Reservations |
| Table | Services | Hotel services |
| Table | BookingServices | Services used per booking |
| Table | Invoices | Payment records |
| View | vw_RoomOccupancy | Current occupancy |
| View | vw_GuestHistory | Guest visit history |
| View | vw_UnpaidInvoices | Pending payments |
| Procedure | sp_CheckIn | Check-in a guest |
| Procedure | sp_CheckOut | Check-out + invoice |
| Procedure | sp_MakeBooking | Create a booking |
| Function | fn_BookingCost | Calculate total cost |
| Function | fn_ApplyDiscount | Apply stay discounts |
| Trigger | trg_AfterBookingUpdate | Auto-update room status |
| User | receptionist | Limited access |
| User | manager | Full access |
| User | accountant | Invoice access only |

---

## 🖥️ Application Pages

- **Dashboard** — Stats, recent bookings, quick actions
- **Guests** — CRUD guest profiles, search
- **Rooms** — Room list, filter by status, update status
- **Bookings** — Create, check-in, check-out, cancel, add services
- **Services** — View all hotel services
- **Invoices** — View and mark invoices as paid
- **Reports** — Revenue chart, guest history, occupancy

---

## 👤 DB User Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | root | (your root password) |
| Receptionist | receptionist | Recept!on2024 |
| Manager | manager | M@nager2024! |
| Accountant | accountant | Acc0unt!2024 |
