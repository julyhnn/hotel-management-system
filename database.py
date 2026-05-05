"""
database.py - Database connection and ORM-style helpers
Hotel Management System | Nguyen Phuong Linh | 11247186
"""

import mysql.connector
from mysql.connector import Error
from datetime import date, datetime
from contextlib import contextmanager

# ─── Connection config ────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     3306,
    "database": "hotel_management",
    "user":     "root",             # Change to your MySQL user
    "password": "your_password",    # Change to your MySQL password
    "charset":  "utf8mb4",
    "autocommit": False,
    "connection_timeout": 10,
}

def get_connection():
    """Return a new MySQL connection (caller must close it)."""
    return mysql.connector.connect(**DB_CONFIG)

@contextmanager
def db_cursor(commit: bool = False):
    """Context manager: yields (conn, cursor), auto-commits/rolls-back."""
    conn = get_connection()
    cur  = conn.cursor(dictionary=True)
    try:
        yield conn, cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

# ─── GUEST helpers ────────────────────────────────────────────────────────────

def get_all_guests():
    with db_cursor() as (_, cur):
        cur.execute("SELECT * FROM Guests ORDER BY GuestName")
        return cur.fetchall()

def search_guests(keyword: str):
    kw = f"%{keyword}%"
    with db_cursor() as (_, cur):
        cur.execute(
            "SELECT * FROM Guests WHERE GuestName LIKE %s OR PhoneNumber LIKE %s OR Email LIKE %s",
            (kw, kw, kw)
        )
        return cur.fetchall()

def add_guest(name, phone, email, address, id_number, nationality="Vietnamese"):
    with db_cursor(commit=True) as (_, cur):
        cur.execute(
            "INSERT INTO Guests (GuestName, PhoneNumber, Email, Address, IDNumber, Nationality) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (name, phone, email, address, id_number, nationality)
        )
        return cur.lastrowid

def update_guest(guest_id, name, phone, email, address, id_number, nationality):
    with db_cursor(commit=True) as (_, cur):
        cur.execute(
            "UPDATE Guests SET GuestName=%s, PhoneNumber=%s, Email=%s, "
            "Address=%s, IDNumber=%s, Nationality=%s WHERE GuestID=%s",
            (name, phone, email, address, id_number, nationality, guest_id)
        )

def delete_guest(guest_id):
    with db_cursor(commit=True) as (_, cur):
        cur.execute("DELETE FROM Guests WHERE GuestID=%s", (guest_id,))

# ─── ROOM helpers ─────────────────────────────────────────────────────────────

def get_all_rooms():
    with db_cursor() as (_, cur):
        cur.execute("SELECT * FROM Rooms ORDER BY RoomNumber")
        return cur.fetchall()

def get_available_rooms(checkin: str, checkout: str):
    with db_cursor() as (_, cur):
        cur.execute("""
            SELECT * FROM Rooms
            WHERE Status NOT IN ('Maintenance')
              AND RoomID NOT IN (
                  SELECT RoomID FROM Bookings
                  WHERE Status IN ('Reserved','CheckedIn')
                    AND NOT (CheckOutDate <= %s OR CheckInDate >= %s)
              )
            ORDER BY RoomType, Price
        """, (checkin, checkout))
        return cur.fetchall()

def get_room_occupancy():
    with db_cursor() as (_, cur):
        cur.execute("SELECT * FROM vw_RoomOccupancy ORDER BY Floor, RoomNumber")
        return cur.fetchall()

def update_room(room_id, room_type, status, price, description):
    with db_cursor(commit=True) as (_, cur):
        cur.execute(
            "UPDATE Rooms SET RoomType=%s, Status=%s, Price=%s, Description=%s WHERE RoomID=%s",
            (room_type, status, price, description, room_id)
        )

def add_room(room_number, room_type, floor, price, max_occ, description):
    with db_cursor(commit=True) as (_, cur):
        cur.execute(
            "INSERT INTO Rooms (RoomNumber,RoomType,Floor,Price,MaxOccupancy,Description) "
            "VALUES (%s,%s,%s,%s,%s,%s)",
            (room_number, room_type, floor, price, max_occ, description)
        )
        return cur.lastrowid

# ─── BOOKING helpers ──────────────────────────────────────────────────────────

def get_all_bookings():
    with db_cursor() as (_, cur):
        cur.execute("""
            SELECT b.*, g.GuestName, g.PhoneNumber, r.RoomNumber, r.RoomType
            FROM Bookings b
            JOIN Guests g ON b.GuestID = g.GuestID
            JOIN Rooms  r ON b.RoomID  = r.RoomID
            ORDER BY b.CreatedAt DESC
        """)
        return cur.fetchall()

def make_booking(guest_id, room_id, checkin, checkout, adults, children=0, notes=""):
    with db_cursor(commit=True) as (conn, cur):
        cur.callproc("sp_MakeBooking", [guest_id, room_id, checkin, checkout, adults, 0, ""])
        conn.commit()
        # Re-fetch last booking for this guest+room
        cur.execute("""
            SELECT BookingID FROM Bookings 
            WHERE GuestID=%s AND RoomID=%s AND CheckInDate=%s
            ORDER BY BookingID DESC LIMIT 1
        """, (guest_id, room_id, checkin))
        row = cur.fetchone()
        return row["BookingID"] if row else None

def checkin_booking(booking_id):
    with db_cursor(commit=True) as (conn, cur):
        cur.execute("UPDATE Bookings SET Status='CheckedIn' WHERE BookingID=%s", (booking_id,))
        cur.execute("UPDATE Rooms SET Status='Occupied' WHERE RoomID=(SELECT RoomID FROM Bookings WHERE BookingID=%s)", (booking_id,))

def checkout_booking(booking_id):
    with db_cursor(commit=True) as (conn, cur):
        # Get booking info
        cur.execute("""
            SELECT b.GuestID, b.RoomID, DATEDIFF(b.CheckOutDate, b.CheckInDate) AS Nights,
                   r.Price
            FROM Bookings b JOIN Rooms r ON b.RoomID=r.RoomID
            WHERE b.BookingID=%s
        """, (booking_id,))
        bk = cur.fetchone()
        if not bk:
            return None
        room_charges = float(bk["Price"]) * int(bk["Nights"])
        cur.execute("""
            SELECT IFNULL(SUM(s.Price * bs.Quantity),0) AS svc
            FROM BookingServices bs JOIN Services s ON bs.ServiceID=s.ServiceID
            WHERE bs.BookingID=%s
        """, (booking_id,))
        svc = cur.fetchone()
        svc_charges = float(svc["svc"]) if svc else 0.0
        total = room_charges + svc_charges

        cur.execute("UPDATE Bookings SET Status='CheckedOut' WHERE BookingID=%s", (booking_id,))
        cur.execute("UPDATE Rooms SET Status='Available' WHERE RoomID=%s", (bk["RoomID"],))
        cur.execute("""
            INSERT INTO Invoices (BookingID, GuestID, RoomCharges, ServiceCharges, TotalAmount)
            VALUES (%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
                RoomCharges=%s, ServiceCharges=%s, TotalAmount=%s
        """, (booking_id, bk["GuestID"], room_charges, svc_charges, total,
              room_charges, svc_charges, total))
        return total

def cancel_booking(booking_id):
    with db_cursor(commit=True) as (_, cur):
        cur.execute("UPDATE Bookings SET Status='Cancelled' WHERE BookingID=%s", (booking_id,))
        cur.execute("UPDATE Rooms SET Status='Available' WHERE RoomID=(SELECT RoomID FROM Bookings WHERE BookingID=%s)", (booking_id,))


# ─── SERVICE helpers ──────────────────────────────────────────────────────────

def get_all_services():
    with db_cursor() as (_, cur):
        cur.execute("SELECT * FROM Services WHERE IsActive=1 ORDER BY Category, ServiceName")
        return cur.fetchall()

def add_service_to_booking(booking_id, service_id, quantity=1):
    with db_cursor(commit=True) as (_, cur):
        cur.execute(
            "INSERT INTO BookingServices (BookingID, ServiceID, Quantity) VALUES (%s,%s,%s)",
            (booking_id, service_id, quantity)
        )

def get_booking_services(booking_id):
    with db_cursor() as (_, cur):
        cur.execute("""
            SELECT bs.*, s.ServiceName, s.Price, s.Category,
                   (s.Price * bs.Quantity) AS Subtotal
            FROM BookingServices bs
            JOIN Services s ON bs.ServiceID=s.ServiceID
            WHERE bs.BookingID=%s
        """, (booking_id,))
        return cur.fetchall()

# ─── INVOICE helpers ──────────────────────────────────────────────────────────

def get_all_invoices():
    with db_cursor() as (_, cur):
        cur.execute("""
            SELECT i.*, g.GuestName, r.RoomNumber, r.RoomType,
                   b.CheckInDate, b.CheckOutDate
            FROM Invoices i
            JOIN Guests   g ON i.GuestID=g.GuestID
            JOIN Bookings b ON i.BookingID=b.BookingID
            JOIN Rooms    r ON b.RoomID=r.RoomID
            ORDER BY i.CreatedAt DESC
        """)
        return cur.fetchall()

def mark_invoice_paid(invoice_id, method="Cash"):
    with db_cursor(commit=True) as (_, cur):
        cur.execute(
            "UPDATE Invoices SET PaymentStatus='Paid', PaymentMethod=%s, PaymentDate=NOW() WHERE InvoiceID=%s",
            (method, invoice_id)
        )

def get_invoice(booking_id):
    with db_cursor() as (_, cur):
        cur.execute("""
            SELECT i.*, g.GuestName, g.PhoneNumber, g.Email,
                   r.RoomNumber, r.RoomType, b.CheckInDate, b.CheckOutDate,
                   DATEDIFF(b.CheckOutDate, b.CheckInDate) AS Nights
            FROM Invoices i
            JOIN Guests g ON i.GuestID=g.GuestID
            JOIN Bookings b ON i.BookingID=b.BookingID
            JOIN Rooms r ON b.RoomID=r.RoomID
            WHERE i.BookingID=%s
        """, (booking_id,))
        return cur.fetchone()

# ─── REPORTING ────────────────────────────────────────────────────────────────

def get_dashboard_stats():
    with db_cursor() as (_, cur):
        cur.execute("SELECT COUNT(*) AS n FROM Rooms WHERE Status='Available'")
        available = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM Rooms WHERE Status='Occupied'")
        occupied = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM Bookings WHERE Status='Reserved'")
        reserved = cur.fetchone()["n"]
        cur.execute("SELECT IFNULL(SUM(TotalAmount),0) AS rev FROM Invoices WHERE PaymentStatus='Paid' AND MONTH(PaymentDate)=MONTH(NOW())")
        revenue = cur.fetchone()["rev"]
        cur.execute("SELECT COUNT(*) AS n FROM Guests")
        guests = cur.fetchone()["n"]
        cur.execute("SELECT COUNT(*) AS n FROM Invoices WHERE PaymentStatus='Pending'")
        pending = cur.fetchone()["n"]
        return {
            "available": available,
            "occupied": occupied,
            "reserved": reserved,
            "revenue": float(revenue),
            "guests": guests,
            "pending_invoices": pending,
        }

def get_revenue_report():
    with db_cursor() as (_, cur):
        cur.execute("""
            SELECT DATE_FORMAT(PaymentDate,'%Y-%m') AS Month,
                   SUM(TotalAmount) AS Revenue,
                   COUNT(*) AS Invoices
            FROM Invoices WHERE PaymentStatus='Paid'
            GROUP BY Month ORDER BY Month DESC LIMIT 12
        """)
        return cur.fetchall()

def get_guest_history():
    with db_cursor() as (_, cur):
        cur.execute("SELECT * FROM vw_GuestHistory ORDER BY TotalSpent DESC")
        return cur.fetchall()
