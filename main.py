"""
main.py - Hotel Management System GUI
Santorini Resort Theme | DATCOM Lab | NEU
Run: python main.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import date, timedelta
import sys, os

# ─── Optional: graceful DB import ─────────────────────────────────────────────
try:
    import database as db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# ─── Color Palette (Santorini-inspired) ───────────────────────────────────────
C = {
    "bg":        "#0F1C2E",   # Deep navy
    "sidebar":   "#0A1628",   # Darker sidebar
    "card":      "#162033",   # Card background
    "accent":    "#C9A96E",   # Gold accent
    "accent2":   "#4A90D9",   # Aegean blue
    "white":     "#F0EDE8",   # Warm white
    "muted":     "#8899AA",   # Muted text
    "success":   "#4CAF7D",   # Green
    "warning":   "#E8A44A",   # Orange
    "danger":    "#E85454",   # Red
    "border":    "#1E2F45",   # Border color
    "hover":     "#1E3050",   # Hover state
    "input_bg":  "#1A2840",   # Input background
}

FONT_TITLE  = ("Georgia", 22, "bold")
FONT_HEAD   = ("Georgia", 13, "bold")
FONT_LABEL  = ("Georgia", 10)
FONT_BOLD   = ("Georgia", 10, "bold")
FONT_SMALL  = ("Georgia", 9)
FONT_MONO   = ("American Typewriter", 10)

# ─── Fake data fallback ───────────────────────────────────────────────────────
DEMO_GUESTS = [
    {"GuestID":1,"GuestName":"Nguyen Van An","PhoneNumber":"0901234567","Email":"an@email.com","Address":"Ha Noi","IDNumber":"001234","Nationality":"Vietnamese"},
    {"GuestID":2,"GuestName":"James Wilson","PhoneNumber":"0956789012","Email":"jwilson@gmail.com","Address":"London","IDNumber":"UK9876","Nationality":"British"},
    {"GuestID":3,"GuestName":"Maria Garcia","PhoneNumber":"0967890123","Email":"mgarcia@yahoo.com","Address":"Madrid","IDNumber":"ES1234","Nationality":"Spanish"},
]
DEMO_ROOMS = [
    {"RoomID":1,"RoomNumber":"101","RoomType":"Standard","Floor":1,"Status":"Available","Price":125.00,"MaxOccupancy":2,"Description":"Garden view"},
    {"RoomID":2,"RoomNumber":"201","RoomType":"Deluxe","Floor":2,"Status":"Occupied","Price":220.00,"MaxOccupancy":3,"Description":"Sea view"},
    {"RoomID":3,"RoomNumber":"301","RoomType":"Suite","Floor":3,"Status":"Available","Price":380.00,"MaxOccupancy":4,"Description":"Jacuzzi"},
    {"RoomID":4,"RoomNumber":"401","RoomType":"Presidential","Floor":4,"Status":"Reserved","Price":750.00,"MaxOccupancy":6,"Description":"Infinity pool"},
]
DEMO_BOOKINGS = [
    {"BookingID":1,"GuestName":"Nguyen Van An","PhoneNumber":"090...","RoomNumber":"101","RoomType":"Standard","CheckInDate":"2025-05-01","CheckOutDate":"2025-05-04","Status":"CheckedOut","Adults":2,"Children":0},
    {"BookingID":2,"GuestName":"James Wilson","PhoneNumber":"095...","RoomNumber":"201","RoomType":"Deluxe","CheckInDate":"2025-05-15","CheckOutDate":"2025-05-20","Status":"CheckedIn","Adults":2,"Children":0},
]
DEMO_INVOICES = [
    {"InvoiceID":1,"GuestName":"Nguyen Van An","RoomNumber":"101","RoomType":"Standard","TotalAmount":505.00,"PaymentStatus":"Paid","PaymentDate":"2025-05-04","CheckInDate":"2025-05-01","CheckOutDate":"2025-05-04"},
    {"InvoiceID":2,"GuestName":"James Wilson","RoomNumber":"201","RoomType":"Deluxe","TotalAmount":1175.00,"PaymentStatus":"Pending","PaymentDate":None,"CheckInDate":"2025-05-15","CheckOutDate":"2025-05-20"},
]
DEMO_STATS = {"available":12,"occupied":5,"reserved":3,"revenue":8865.00,"guests":10,"pending_invoices":2}

# ─── Helpers ──────────────────────────────────────────────────────────────────

def safe_db(fn, fallback, *args, **kwargs):
    if DB_AVAILABLE:
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"[DB Error] {fn.__name__}: {e}")
    return fallback

def status_color(status):
    return {
        "Available":  C["success"],
        "Occupied":   C["danger"],
        "Reserved":   C["warning"],
        "Maintenance":C["muted"],
        "CheckedIn":  C["accent2"],
        "CheckedOut": C["muted"],
        "Cancelled":  C["danger"],
        "Paid":       C["success"],
        "Pending":    C["warning"],
        "Refunded":   C["muted"],
    }.get(status, C["white"])


# ═══════════════════════════════════════════════════════════════════════════════
# WIDGET BUILDERS
# ═══════════════════════════════════════════════════════════════════════════════

def make_label(parent, text, font=FONT_LABEL, fg=None, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg or C["white"],
                    bg=kw.pop("bg", C["card"]), **kw)

def make_entry(parent, textvariable=None, width=28, **kw):
    e = tk.Entry(parent, textvariable=textvariable, width=width,
                 bg=C["input_bg"], fg=C["white"], insertbackground=C["accent"],
                 relief="flat", font=FONT_LABEL, bd=6,
                 highlightthickness=1, highlightbackground=C["border"],
                 highlightcolor=C["accent"], **kw)
    return e

def make_button(parent, text, command=None, style="primary", **kw):
    colors = {
        "primary": (C["accent"],   "#0A1628"),
        "blue":    (C["accent2"],  C["white"]),
        "danger":  (C["danger"],   C["white"]),
        "ghost":   ("#1E3A5F",     C["white"]),
        "success": (C["success"],  "#0A1628"),
    }
    bg, fg = colors.get(style, colors["primary"])
    btn = tk.Label(parent, text=text,
                   bg=bg, fg=fg, font=FONT_BOLD,
                   cursor="hand2", padx=16, pady=8,
                   relief="flat", **kw)
    if command:
        btn.bind("<Button-1>", lambda e: command())
    btn.bind("<Enter>", lambda e: btn.config(bg=_lighten(bg)))
    btn.bind("<Leave>", lambda e: btn.config(bg=bg))
    return btn

def _lighten(hex_color):
    try:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        r = min(255, r + 25)
        g = min(255, g + 25)
        b = min(255, b + 25)
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color

def make_separator(parent, bg=None):
    return tk.Frame(parent, height=1, bg=bg or C["border"])

def scrolled_frame(parent):
    """Returns (outer_frame, inner_frame) with scroll."""
    canvas = tk.Canvas(parent, bg=C["card"], highlightthickness=0, bd=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    inner = tk.Frame(canvas, bg=C["card"])
    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0,0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
    return canvas, inner


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════

class HotelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Santorini Resort — Hotel Management System")
        self.geometry("1280x780")
        self.minsize(1100, 680)
        self.configure(bg=C["bg"])
        self._current_page = None
        self._build_ui()
        self.navigate("dashboard")

    # ── Layout ────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self, bg=C["sidebar"], height=52)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="⚓  SANTORINI RESORT", font=("Georgia",14,"bold"),
                 fg=C["accent"], bg=C["sidebar"]).pack(side="left", padx=20, pady=12)
        tk.Label(topbar, text="Hotel Management System", font=("Georgia",10),
                 fg=C["muted"], bg=C["sidebar"]).pack(side="left", padx=4, pady=12)

        # Right: status
        self._db_label = tk.Label(topbar, text="● LIVE DB" if DB_AVAILABLE else "● DEMO MODE",
                                  font=FONT_SMALL,
                                  fg=C["success"] if DB_AVAILABLE else C["warning"],
                                  bg=C["sidebar"])
        self._db_label.pack(side="right", padx=20)

        today_lbl = tk.Label(topbar, text=f"📅  {date.today().strftime('%d %b %Y')}",
                             font=FONT_SMALL, fg=C["muted"], bg=C["sidebar"])
        today_lbl.pack(side="right", padx=16)

        # Sidebar + content
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        self.sidebar = tk.Frame(body, bg=C["sidebar"], width=210)
        self.sidebar.pack(fill="y", side="left")
        self.sidebar.pack_propagate(False)

        self.content = tk.Frame(body, bg=C["bg"])
        self.content.pack(fill="both", expand=True, side="left")

        self._build_sidebar()

    def _build_sidebar(self):
        # Logo area
        logo_area = tk.Frame(self.sidebar, bg=C["sidebar"], pady=20)
        logo_area.pack(fill="x")
        tk.Label(logo_area, text="☰  NAVIGATION", font=("American Typewriter",9,"bold"),
                 fg=C["muted"], bg=C["sidebar"]).pack(anchor="w", padx=20)

        make_separator(self.sidebar).pack(fill="x", padx=12)

        nav_items = [
            ("dashboard",   "🏠",  "Dashboard"),
            ("guests",      "👥",  "Guests"),
            ("rooms",       "🛏",  "Rooms"),
            ("bookings",    "📋",  "Bookings"),
            ("services",    "🛎",  "Services"),
            ("invoices",    "💳",  "Invoices"),
            ("reports",     "📊",  "Reports"),
        ]
        self._nav_buttons = {}
        for page, icon, label in nav_items:
            btn = tk.Label(self.sidebar,
                           text=f"  {icon}   {label}",
                           font=FONT_LABEL, anchor="w",
                           bg=C["sidebar"], fg=C["white"],
                           cursor="hand2", padx=8, pady=9)
            btn.pack(fill="x", padx=8, pady=2)
            btn.bind("<Button-1>", lambda e, p=page: self.navigate(p))
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=C["hover"], fg=C["accent"]))
            btn.bind("<Leave>", lambda e, b=btn, p=page: b.config(
                bg=C["hover"] if self._current_page == p else C["sidebar"],
                fg=C["accent"] if self._current_page == p else C["white"]
            ))
            self._nav_buttons[page] = btn

        # Bottom
        make_separator(self.sidebar).pack(fill="x", padx=12, side="bottom", pady=0)
        tk.Label(self.sidebar, text="Nguyen Phuong Linh - 1124718", font=("American Typewriter",8),
                 fg=C["muted"], bg=C["sidebar"]).pack(side="bottom", pady=10)

    def navigate(self, page):
        # Update active button
        for p, btn in self._nav_buttons.items():
            if p == page:
                btn.config(bg=C["hover"], fg=C["accent"])
            else:
                btn.config(bg=C["sidebar"], fg=C["white"])

        # Clear content
        for w in self.content.winfo_children():
            w.destroy()

        self._current_page = page
        pages = {
            "dashboard": DashboardPage,
            "guests":    GuestsPage,
            "rooms":     RoomsPage,
            "bookings":  BookingsPage,
            "services":  ServicesPage,
            "invoices":  InvoicesPage,
            "reports":   ReportsPage,
        }
        cls = pages.get(page, DashboardPage)
        cls(self.content, self).pack(fill="both", expand=True)


# ═══════════════════════════════════════════════════════════════════════════════
# BASE PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class BasePage(tk.Frame):
    def __init__(self, parent, app, title="", subtitle=""):
        super().__init__(parent, bg=C["bg"])
        self.app = app
        self._build_header(title, subtitle)
        self.body = tk.Frame(self, bg=C["bg"])
        self.body.pack(fill="both", expand=True, padx=24, pady=0)

    def _build_header(self, title, subtitle):
        hdr = tk.Frame(self, bg=C["bg"], pady=0)
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        tk.Label(hdr, text=title, font=FONT_TITLE, fg=C["accent"], bg=C["bg"]).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, font=FONT_SMALL, fg=C["muted"], bg=C["bg"]).pack(anchor="w")
        make_separator(hdr, bg=C["border"]).pack(fill="x", pady=(6, 0))

    def card(self, parent=None, **kw):
        p = parent or self.body
        f = tk.Frame(p, bg=C["card"], bd=0,
                     highlightthickness=1, highlightbackground=C["border"], **kw)
        return f

    def stat_card(self, parent, value, label, color=None, icon=""):
        card = tk.Frame(parent, bg=C["card"],
                        highlightthickness=1, highlightbackground=C["border"])
        tk.Label(card, text=icon, font=("Helvetica",22), bg=C["card"],
                 fg=color or C["accent"]).pack(pady=(14,2))
        tk.Label(card, text=str(value), font=("Georgia",20,"bold"),
                 bg=C["card"], fg=color or C["accent"]).pack()
        tk.Label(card, text=label, font=FONT_SMALL, bg=C["card"], fg=C["muted"]).pack(pady=(2,14))
        return card

    def table(self, parent, columns, data, row_height=32):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Hotel.Treeview",
                         background=C["card"],
                         foreground=C["white"],
                         rowheight=row_height,
                         fieldbackground=C["card"],
                         bordercolor=C["border"],
                         font=FONT_LABEL)
        style.configure("Hotel.Treeview.Heading",
                         background=C["sidebar"],
                         foreground=C["accent"],
                         font=FONT_BOLD,
                         borderwidth=0)
        style.map("Hotel.Treeview",
                  background=[("selected", C["hover"])],
                  foreground=[("selected", C["accent"])])

        frame = tk.Frame(parent, bg=C["card"])

        tree = ttk.Treeview(frame, columns=columns, show="headings",
                             style="Hotel.Treeview", selectmode="browse")

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)

        for row in data:
            tree.insert("", "end", values=row)

        return frame, tree

    def form_row(self, parent, label, widget_fn, **kw):
        row = tk.Frame(parent, bg=C["card"])
        tk.Label(row, text=label, font=FONT_BOLD, fg=C["muted"],
                 bg=C["card"], width=14, anchor="e").pack(side="left", padx=(8,6), pady=4)
        w = widget_fn(row, **kw)
        w.pack(side="left", fill="x", expand=True, padx=(0,8), pady=4)
        row.pack(fill="x", pady=2)
        return w


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "🏠  Dashboard", "Welcome back — Santorini Resort Management")
        self._build()

    def _build(self):
        stats = safe_db(db.get_dashboard_stats, DEMO_STATS) if DB_AVAILABLE else DEMO_STATS

        # Stats row
        stat_frame = tk.Frame(self.body, bg=C["bg"])
        stat_frame.pack(fill="x", pady=(8,16))
        for i in range(6):
            stat_frame.columnconfigure(i, weight=1)

        stat_data = [
            (stats["available"],       "Available Rooms",    C["success"], "🛏"),
            (stats["occupied"],        "Occupied Rooms",     C["danger"],  "🔑"),
            (stats["reserved"],        "Reservations",       C["warning"], "📋"),
            (f"${stats['revenue']:,.0f}", "Monthly Revenue", C["accent"],  "💰"),
            (stats["guests"],          "Total Guests",       C["accent2"], "👥"),
            (stats["pending_invoices"],"Pending Invoices",   C["warning"], "💳"),
        ]
        for i, (val, lbl, col, icon) in enumerate(stat_data):
            card = self.stat_card(stat_frame, val, lbl, col, icon)
            card.grid(row=0, column=i, padx=6, sticky="nsew")

        # Two column layout
        cols = tk.Frame(self.body, bg=C["bg"])
        cols.pack(fill="both", expand=True)
        cols.columnconfigure(0, weight=3)
        cols.columnconfigure(1, weight=2)

        # Recent bookings
        left = self.card(cols)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=4)
        tk.Label(left, text="Recent Bookings", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(left).pack(fill="x", padx=16)

        bookings = safe_db(db.get_all_bookings, DEMO_BOOKINGS)[:8] if DB_AVAILABLE else DEMO_BOOKINGS
        cols_b = ("Guest", "Room", "Check-In", "Check-Out", "Status")
        rows_b = []
        for b in bookings:
            rows_b.append((
                b.get("GuestName",""),
                b.get("RoomNumber",""),
                str(b.get("CheckInDate","")),
                str(b.get("CheckOutDate","")),
                b.get("Status",""),
            ))
        tbl, tree = self.table(left, cols_b, rows_b)
        tbl.pack(fill="both", expand=True, padx=8, pady=8)

        # Room status pie-like summary
        right = self.card(cols)
        right.grid(row=0, column=1, sticky="nsew", pady=4)
        tk.Label(right, text="Room Status", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(right).pack(fill="x", padx=16)

        status_items = [
            ("Available",   stats["available"],  C["success"]),
            ("Occupied",    stats["occupied"],   C["danger"]),
            ("Reserved",    stats["reserved"],   C["warning"]),
        ]
        for status, count, color in status_items:
            row = tk.Frame(right, bg=C["card"])
            row.pack(fill="x", padx=16, pady=6)
            tk.Label(row, text="●", fg=color, bg=C["card"], font=("Helvetica",14)).pack(side="left")
            tk.Label(row, text=status, fg=C["white"], bg=C["card"], font=FONT_LABEL).pack(side="left", padx=8)
            tk.Label(row, text=str(count), fg=color, bg=C["card"], font=FONT_BOLD).pack(side="right")

        # Quick actions
        tk.Label(right, text="Quick Actions", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(20,6))
        make_separator(right).pack(fill="x", padx=16)
        make_button(right, "＋  New Booking",  lambda: self.app.navigate("bookings"), "primary").pack(fill="x", padx=16, pady=4)
        make_button(right, "👤  Add Guest",    lambda: self.app.navigate("guests"),   "blue").pack(fill="x", padx=16, pady=4)
        make_button(right, "📊  View Reports", lambda: self.app.navigate("reports"),  "ghost").pack(fill="x", padx=16, pady=(4,16))


# ═══════════════════════════════════════════════════════════════════════════════
# GUESTS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class GuestsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "👥  Guest Management", "Register and manage guest profiles")
        self._selected_id = None
        self._vars = {}
        self._build()

    def _build(self):
        # Top toolbar
        toolbar = tk.Frame(self.body, bg=C["bg"])
        toolbar.pack(fill="x", pady=(0, 8))
        self._search_var = tk.StringVar()
        make_entry(toolbar, textvariable=self._search_var, width=30).pack(side="left", padx=(0,8))
        make_button(toolbar, "🔍 Search", self._search, "blue").pack(side="left", padx=4)
        make_button(toolbar, "↺ Refresh", self._load_data, "ghost").pack(side="left", padx=4)
        make_button(toolbar, "＋ Add Guest", self._show_add_form, "primary").pack(side="right")
        make_button(toolbar, "✏ Edit",  self._show_edit_form, "ghost").pack(side="right", padx=4)
        make_button(toolbar, "🗑 Delete", self._delete, "danger").pack(side="right", padx=4)

        # Split: table | form
        split = tk.Frame(self.body, bg=C["bg"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)

        # Table
        left = self.card(split)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        cols = ("ID","Name","Phone","Email","Address","Nationality")
        tbl, self._tree = self.table(left, cols, [])
        tbl.pack(fill="both", expand=True, padx=8, pady=8)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # Form panel
        self._form_panel = self.card(split)
        self._form_panel.grid(row=0, column=1, sticky="nsew")
        self._build_form(self._form_panel)

        self._load_data()

    def _build_form(self, parent):
        tk.Label(parent, text="Guest Details", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(parent).pack(fill="x", padx=16)

        fields = [("Name","name"),("Phone","phone"),("Email","email"),
                  ("Address","address"),("ID Number","id_number"),("Nationality","nationality")]
        self._vars = {k: tk.StringVar() for _,k in fields}

        form_body = tk.Frame(parent, bg=C["card"])
        form_body.pack(fill="both", expand=True, padx=12, pady=8)
        for label, key in fields:
            self.form_row(form_body, label+":", lambda p, k=key: make_entry(p, self._vars[k]))

        btns = tk.Frame(parent, bg=C["card"])
        btns.pack(fill="x", padx=16, pady=12)
        make_button(btns, "💾 Save", self._save, "primary").pack(side="left", padx=4)
        make_button(btns, "✖ Clear", self._clear_form, "ghost").pack(side="left", padx=4)

    def _load_data(self):
        data = safe_db(db.get_all_guests, DEMO_GUESTS)
        self._populate(data)

    def _search(self):
        kw = self._search_var.get().strip()
        if not kw:
            self._load_data(); return
        data = safe_db(db.search_guests, DEMO_GUESTS, kw)
        self._populate(data)

    def _populate(self, data):
        self._tree.delete(*self._tree.get_children())
        for g in data:
            self._tree.insert("", "end", iid=g["GuestID"], values=(
                g["GuestID"], g["GuestName"], g["PhoneNumber"],
                g.get("Email",""), g.get("Address",""), g.get("Nationality","")
            ))

    def _on_select(self, event):
        sel = self._tree.selection()
        if not sel: return
        self._selected_id = int(sel[0])
        vals = self._tree.item(sel[0])["values"]
        keys = ["name","phone","email","address","","nationality"]
        for i, key in enumerate(["name","phone","email","address"]):
            self._vars[key].set(vals[i+1] if i+1 < len(vals) else "")
        self._vars["nationality"].set(vals[5] if len(vals)>5 else "")

    def _show_add_form(self):
        self._selected_id = None
        self._clear_form()

    def _show_edit_form(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Please select a guest to edit.")

    def _clear_form(self):
        for v in self._vars.values(): v.set("")
        self._selected_id = None

    def _save(self):
        v = self._vars
        name   = v["name"].get().strip()
        phone  = v["phone"].get().strip()
        email  = v["email"].get().strip()
        addr   = v["address"].get().strip()
        id_num = v["id_number"].get().strip()
        nat    = v["nationality"].get().strip() or "Vietnamese"
        if not name or not phone:
            messagebox.showerror("Validation", "Name and Phone are required."); return
        try:
            if self._selected_id:
                safe_db(db.update_guest, None, self._selected_id, name, phone, email, addr, id_num, nat)
                messagebox.showinfo("Success", "Guest updated!")
            else:
                safe_db(db.add_guest, None, name, phone, email, addr, id_num, nat)
                messagebox.showinfo("Success", "Guest added!")
            self._clear_form()
            self._load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Please select a guest to delete."); return
        if messagebox.askyesno("Confirm Delete", "Delete this guest? This cannot be undone."):
            try:
                safe_db(db.delete_guest, None, self._selected_id)
                self._clear_form()
                self._load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))


# ═══════════════════════════════════════════════════════════════════════════════
# ROOMS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class RoomsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "🛏  Room Management", "Manage rooms, availability, and pricing")
        self._selected_id = None
        self._build()

    def _build(self):
        toolbar = tk.Frame(self.body, bg=C["bg"])
        toolbar.pack(fill="x", pady=(0,8))

        self._filter_var = tk.StringVar(value="All")
        for label in ["All","Available","Occupied","Reserved","Maintenance"]:
            tk.Radiobutton(toolbar, text=label, variable=self._filter_var, value=label,
                           bg=C["bg"], fg=C["white"], selectcolor=C["card"],
                           activebackground=C["bg"], activeforeground=C["accent"],
                           command=self._load_data, font=FONT_SMALL).pack(side="left", padx=4)

        make_button(toolbar, "↺ Refresh", self._load_data, "ghost").pack(side="left", padx=8)
        make_button(toolbar, "✏ Edit Status", self._edit_status, "primary").pack(side="right")

        split = tk.Frame(self.body, bg=C["bg"])
        split.pack(fill="both", expand=True)
        split.columnconfigure(0, weight=3)
        split.columnconfigure(1, weight=2)

        left = self.card(split)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,10))
        cols = ("ID","Room No.","Type","Floor","Status","Price/Night","Capacity")
        tbl, self._tree = self.table(left, cols, [])
        tbl.pack(fill="both", expand=True, padx=8, pady=8)
        self._tree.bind("<<TreeviewSelect>>", self._on_select)

        # Detail panel
        right = self.card(split)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Room Detail", font=FONT_HEAD, fg=C["accent"],
                 bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(right).pack(fill="x", padx=16)
        self._detail_frame = tk.Frame(right, bg=C["card"])
        self._detail_frame.pack(fill="both", expand=True, padx=16, pady=8)

        self._load_data()

    def _load_data(self):
        data = safe_db(db.get_all_rooms, DEMO_ROOMS)
        filt = self._filter_var.get()
        if filt != "All":
            data = [r for r in data if r.get("Status") == filt]
        self._tree.delete(*self._tree.get_children())
        for r in data:
            self._tree.insert("", "end", iid=r["RoomID"], values=(
                r["RoomID"], r["RoomNumber"], r["RoomType"], r.get("Floor",""),
                r["Status"], f"${r['Price']:.2f}", r.get("MaxOccupancy","")
            ))

    def _on_select(self, event):
        sel = self._tree.selection()
        if not sel: return
        self._selected_id = int(sel[0])
        for w in self._detail_frame.winfo_children(): w.destroy()
        vals = self._tree.item(sel[0])["values"]
        items = [("Room No.:", vals[1]),("Type:", vals[2]),("Floor:", vals[3]),
                 ("Status:", vals[4]),("Price:", vals[5]),("Capacity:", vals[6])]
        for lbl, val in items:
            row = tk.Frame(self._detail_frame, bg=C["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=lbl, font=FONT_BOLD, fg=C["muted"],
                     bg=C["card"], width=12, anchor="e").pack(side="left")
            col = status_color(str(val)) if lbl == "Status:" else C["white"]
            tk.Label(row, text=str(val), font=FONT_LABEL, fg=col,
                     bg=C["card"]).pack(side="left", padx=8)

    def _edit_status(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Select a room first."); return
        popup = tk.Toplevel(self)
        popup.title("Update Room Status")
        popup.configure(bg=C["card"])
        popup.geometry("300x200")
        tk.Label(popup, text="New Status:", font=FONT_BOLD, fg=C["white"],
                 bg=C["card"]).pack(pady=(20,4))
        status_var = tk.StringVar(value="Available")
        for s in ["Available","Maintenance","Reserved"]:
            tk.Radiobutton(popup, text=s, variable=status_var, value=s,
                           bg=C["card"], fg=C["white"], selectcolor=C["bg"],
                           font=FONT_LABEL).pack()

        def apply():
            try:
                safe_db(db.update_room, None, self._selected_id, None, status_var.get(), None, None)
                self._load_data()
                popup.destroy()
                messagebox.showinfo("Updated", f"Room status set to {status_var.get()}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        make_button(popup, "✓ Apply", apply, "primary").pack(pady=12)


# ═══════════════════════════════════════════════════════════════════════════════
# BOOKINGS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class BookingsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "📋  Booking Management", "Reservations, check-in, and check-out")
        self._selected_id = None
        self._build()

    def _build(self):
        toolbar = tk.Frame(self.body, bg=C["bg"])
        toolbar.pack(fill="x", pady=(0,8))
        make_button(toolbar, "＋ New Booking",  self._new_booking,    "primary").pack(side="left", padx=4)
        make_button(toolbar, "✓ Check-In",     self._checkin,         "success").pack(side="left", padx=4)
        make_button(toolbar, "🚪 Check-Out",   self._checkout,        "blue").pack(side="left", padx=4)
        make_button(toolbar, "✖ Cancel",       self._cancel,          "danger").pack(side="left", padx=4)
        make_button(toolbar, "🛎 Add Service",  self._add_service,     "ghost").pack(side="left", padx=8)
        make_button(toolbar, "↺ Refresh",      self._load_data,       "ghost").pack(side="right")

        card = self.card(self.body)
        card.pack(fill="both", expand=True)
        cols = ("ID","Guest","Room","Type","Check-In","Check-Out","Adults","Status")
        tbl, self._tree = self.table(card, cols, [])
        tbl.pack(fill="both", expand=True, padx=8, pady=8)
        self._tree.bind("<<TreeviewSelect>>", lambda e: setattr(self, "_selected_id",
            int(self._tree.selection()[0]) if self._tree.selection() else None))
        self._load_data()

    def _load_data(self):
        data = safe_db(db.get_all_bookings, DEMO_BOOKINGS)
        self._tree.delete(*self._tree.get_children())
        for b in data:
            self._tree.insert("", "end", iid=b["BookingID"], values=(
                b["BookingID"], b.get("GuestName",""), b.get("RoomNumber",""),
                b.get("RoomType",""), str(b.get("CheckInDate","")),
                str(b.get("CheckOutDate","")), b.get("Adults",""),
                b.get("Status","")
            ))

    def _new_booking(self):
        popup = tk.Toplevel(self)
        popup.title("New Booking")
        popup.configure(bg=C["card"])
        popup.geometry("420x400")

        tk.Label(popup, text="＋  New Booking", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(pady=(16,8))
        make_separator(tk.Frame(popup, bg=C["card"])).pack(fill="x", padx=16)

        form = tk.Frame(popup, bg=C["card"])
        form.pack(fill="both", expand=True, padx=20, pady=8)

        guest_id_var  = tk.StringVar()
        room_id_var   = tk.StringVar()
        checkin_var   = tk.StringVar(value=str(date.today()))
        checkout_var  = tk.StringVar(value=str(date.today() + timedelta(days=3)))
        adults_var    = tk.StringVar(value="2")

        def lrow(lbl, var):
            r = tk.Frame(form, bg=C["card"])
            r.pack(fill="x", pady=4)
            tk.Label(r, text=lbl, font=FONT_BOLD, fg=C["muted"],
                     bg=C["card"], width=12, anchor="e").pack(side="left")
            make_entry(r, textvariable=var, width=22).pack(side="left", padx=6)

        lrow("Guest ID:", guest_id_var)
        lrow("Room ID:",  room_id_var)
        lrow("Check-In:", checkin_var)
        lrow("Check-Out:",checkout_var)
        lrow("Adults:",   adults_var)

        tk.Label(form, text="Tip: Use Guests/Rooms pages to find IDs",
                 font=FONT_SMALL, fg=C["muted"], bg=C["card"]).pack(pady=4)

        def confirm():
            try:
                gid = int(guest_id_var.get())
                rid = int(room_id_var.get())
                ci  = checkin_var.get()
                co  = checkout_var.get()
                ad  = int(adults_var.get())
                booking_id = safe_db(db.make_booking, None, gid, rid, ci, co, ad)
                if booking_id:
                    messagebox.showinfo("Success", f"Booking #{booking_id} created!")
                else:
                    messagebox.showinfo("Success", "Booking created! (Demo mode)")
                popup.destroy()
                self._load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        make_button(popup, "✓ Confirm Booking", confirm, "primary").pack(pady=12)

    def _checkin(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Select a booking."); return
        if messagebox.askyesno("Check In", f"Check in booking #{self._selected_id}?"):
            safe_db(db.checkin_booking, None, self._selected_id)
            self._load_data()
            messagebox.showinfo("Checked In", "Guest checked in successfully!")

    def _checkout(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Select a booking."); return
        if messagebox.askyesno("Check Out", f"Check out booking #{self._selected_id}? This will generate an invoice."):
            total = safe_db(db.checkout_booking, None, self._selected_id)
            self._load_data()
            if total:
                messagebox.showinfo("Checked Out", f"Invoice generated!\nTotal: ${total:,.2f}")
            else:
                messagebox.showinfo("Checked Out", "Guest checked out. (Demo mode)")

    def _cancel(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Select a booking."); return
        if messagebox.askyesno("Cancel Booking", f"Cancel booking #{self._selected_id}? Room will be freed."):
            safe_db(db.cancel_booking, None, self._selected_id)
            self._load_data()

    def _add_service(self):
        if not self._selected_id:
            messagebox.showwarning("No Selection", "Select a booking."); return
        services = safe_db(db.get_all_services, [
            {"ServiceID":1,"ServiceName":"Airport Transfer","Price":45.0,"Category":"Transport"},
            {"ServiceID":2,"ServiceName":"Breakfast","Price":35.0,"Category":"Food"},
        ])
        popup = tk.Toplevel(self)
        popup.title("Add Service")
        popup.configure(bg=C["card"])
        popup.geometry("360x340")
        tk.Label(popup, text="🛎  Add Service", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(pady=(16,8))

        svc_var = tk.IntVar(value=services[0]["ServiceID"] if services else 1)
        qty_var = tk.StringVar(value="1")

        for s in services:
            tk.Radiobutton(popup, text=f"{s['ServiceName']}  (${s['Price']:.2f})",
                           variable=svc_var, value=s["ServiceID"],
                           bg=C["card"], fg=C["white"], selectcolor=C["bg"],
                           font=FONT_LABEL).pack(anchor="w", padx=20)

        row = tk.Frame(popup, bg=C["card"])
        row.pack(fill="x", padx=20, pady=8)
        tk.Label(row, text="Quantity:", fg=C["muted"], bg=C["card"], font=FONT_BOLD).pack(side="left")
        make_entry(row, textvariable=qty_var, width=6).pack(side="left", padx=8)

        def add():
            try:
                safe_db(db.add_service_to_booking, None, self._selected_id, svc_var.get(), int(qty_var.get()))
                popup.destroy()
                messagebox.showinfo("Added", "Service added to booking!")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        make_button(popup, "＋ Add", add, "primary").pack(pady=12)


# ═══════════════════════════════════════════════════════════════════════════════
# SERVICES PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class ServicesPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "🛎  Service Management", "Hotel services and amenities")
        self._build()

    def _build(self):
        card = self.card(self.body)
        card.pack(fill="both", expand=True)
        tk.Label(card, text="Available Services", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(card).pack(fill="x", padx=16)
        cols = ("ID","Service Name","Category","Price","Description")
        data = safe_db(db.get_all_services, [
            {"ServiceID":1,"ServiceName":"Airport Transfer","Category":"Transport","Price":45.0,"Description":"Round-trip"},
            {"ServiceID":2,"ServiceName":"Breakfast","Category":"Food","Price":35.0,"Description":"Continental for 2"},
            {"ServiceID":6,"ServiceName":"Spa - Basic","Category":"Spa","Price":80.0,"Description":"60-min massage"},
        ])
        rows = [(s["ServiceID"],s["ServiceName"],s["Category"],
                 f"${s['Price']:.2f}",s.get("Description","")) for s in data]
        tbl, _ = self.table(card, cols, rows)
        tbl.pack(fill="both", expand=True, padx=8, pady=8)


# ═══════════════════════════════════════════════════════════════════════════════
# INVOICES PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class InvoicesPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "💳  Invoice Management", "View and process guest payments")
        self._selected_inv_id = None
        self._build()

    def _build(self):
        toolbar = tk.Frame(self.body, bg=C["bg"])
        toolbar.pack(fill="x", pady=(0,8))
        make_button(toolbar, "✓ Mark as Paid", self._mark_paid, "success").pack(side="left", padx=4)
        make_button(toolbar, "↺ Refresh",      self._load_data, "ghost").pack(side="right")

        card = self.card(self.body)
        card.pack(fill="both", expand=True)
        cols = ("Inv.ID","Guest","Room","Type","Room Charges","Svc Charges","Total","Status","Check-In","Check-Out")
        tbl, self._tree = self.table(card, cols, [])
        tbl.pack(fill="both", expand=True, padx=8, pady=8)
        self._tree.bind("<<TreeviewSelect>>", lambda e: setattr(self,"_selected_inv_id",
            int(self._tree.selection()[0]) if self._tree.selection() else None))
        self._load_data()

    def _load_data(self):
        data = safe_db(db.get_all_invoices, DEMO_INVOICES)
        self._tree.delete(*self._tree.get_children())
        for i in data:
            self._tree.insert("", "end", iid=i["InvoiceID"], values=(
                i["InvoiceID"], i.get("GuestName",""), i.get("RoomNumber",""),
                i.get("RoomType",""),
                f"${i.get('RoomCharges', i.get('TotalAmount',0)):.2f}" if "RoomCharges" in i else "-",
                f"${i.get('ServiceCharges',0):.2f}" if "ServiceCharges" in i else "-",
                f"${i['TotalAmount']:.2f}",
                i.get("PaymentStatus",""), str(i.get("CheckInDate","")), str(i.get("CheckOutDate",""))
            ))

    def _mark_paid(self):
        if not self._selected_inv_id:
            messagebox.showwarning("No Selection", "Select an invoice."); return
        method = simpledialog.askstring("Payment Method",
                                        "Method (Cash/Card/BankTransfer/Online):",
                                        parent=self) or "Cash"
        safe_db(db.mark_invoice_paid, None, self._selected_inv_id, method)
        self._load_data()
        messagebox.showinfo("Paid", f"Invoice #{self._selected_inv_id} marked as Paid.")


# ═══════════════════════════════════════════════════════════════════════════════
# REPORTS PAGE
# ═══════════════════════════════════════════════════════════════════════════════

class ReportsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent, app, "📊  Reports & Analytics", "Revenue, occupancy, and guest analytics")
        self._build()

    def _build(self):
        tabs_frame = tk.Frame(self.body, bg=C["bg"])
        tabs_frame.pack(fill="x", pady=(0,8))
        self._tab_content = tk.Frame(self.body, bg=C["bg"])
        self._tab_content.pack(fill="both", expand=True)

        tabs = [("Revenue",self._show_revenue),("Guest History",self._show_guests),("Occupancy",self._show_occupancy)]
        for lbl, fn in tabs:
            make_button(tabs_frame, lbl, fn, "ghost").pack(side="left", padx=4)

        self._show_revenue()

    def _clear(self):
        for w in self._tab_content.winfo_children(): w.destroy()

    def _show_revenue(self):
        self._clear()
        card = self.card(self._tab_content)
        card.pack(fill="both", expand=True)
        tk.Label(card, text="Monthly Revenue Report", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(card).pack(fill="x", padx=16)
        data = safe_db(db.get_revenue_report, [
            {"Month":"2025-05","Revenue":8865.0,"Invoices":5},
            {"Month":"2025-04","Revenue":12350.0,"Invoices":8},
        ])
        cols = ("Month","Revenue","# Invoices")
        rows = [(r["Month"], f"${float(r['Revenue']):,.2f}", r["Invoices"]) for r in data]
        tbl, tree = self.table(card, cols, rows, row_height=36)
        tbl.pack(fill="both", expand=True, padx=8, pady=8)

        # Simple bar chart using canvas
        if data:
            canvas = tk.Canvas(card, bg=C["card"], height=160, highlightthickness=0)
            canvas.pack(fill="x", padx=20, pady=8)
            max_rev = max(float(r["Revenue"]) for r in data) or 1
            bar_w = max(20, min(60, 600 // max(len(data),1)))
            for i, r in enumerate(reversed(data)):
                rev = float(r["Revenue"])
                h = int((rev / max_rev) * 120)
                x = 30 + i * (bar_w + 8)
                canvas.create_rectangle(x, 140-h, x+bar_w, 140, fill=C["accent"], outline="")
                canvas.create_text(x+bar_w//2, 150, text=r["Month"][-5:],
                                   font=("Helvetica",7), fill=C["muted"], anchor="n")

    def _show_guests(self):
        self._clear()
        card = self.card(self._tab_content)
        card.pack(fill="both", expand=True)
        tk.Label(card, text="Guest History & Value", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(card).pack(fill="x", padx=16)
        data = safe_db(db.get_guest_history, [
            {"GuestID":1,"GuestName":"Nguyen Van An","PhoneNumber":"0901234567","Email":"an@email.com","TotalBookings":2,"TotalNights":5,"TotalSpent":1010.0,"LastVisit":"2025-05-04"},
            {"GuestID":4,"GuestName":"Pham Thu Dung","PhoneNumber":"093...","Email":"","TotalBookings":1,"TotalNights":5,"TotalSpent":4520.0,"LastVisit":"2025-05-12"},
        ])
        cols = ("ID","Name","Phone","Bookings","Nights","Total Spent","Last Visit")
        rows = [(g["GuestID"],g["GuestName"],g.get("PhoneNumber",""),
                 g.get("TotalBookings",0), g.get("TotalNights",0) or 0,
                 f"${float(g.get('TotalSpent') or 0):,.2f}",
                 str(g.get("LastVisit","") or "")) for g in data]
        tbl, _ = self.table(card, cols, rows, row_height=36)
        tbl.pack(fill="both", expand=True, padx=8, pady=8)

    def _show_occupancy(self):
        self._clear()
        card = self.card(self._tab_content)
        card.pack(fill="both", expand=True)
        tk.Label(card, text="Room Occupancy Status", font=FONT_HEAD,
                 fg=C["accent"], bg=C["card"]).pack(anchor="w", padx=16, pady=(12,6))
        make_separator(card).pack(fill="x", padx=16)
        data = safe_db(db.get_room_occupancy, [
            {"RoomID":1,"RoomNumber":"101","RoomType":"Standard","Floor":1,"Status":"Available","Price":125.0,"GuestName":None,"CheckInDate":None,"CheckOutDate":None,"NightsBooked":None},
            {"RoomID":2,"RoomNumber":"201","RoomType":"Deluxe","Floor":2,"Status":"Occupied","Price":220.0,"GuestName":"James Wilson","CheckInDate":"2025-05-15","CheckOutDate":"2025-05-20","NightsBooked":5},
        ])
        cols = ("Room","Type","Floor","Status","Guest","Check-In","Check-Out","Nights")
        rows = [(r["RoomNumber"],r["RoomType"],r["Floor"],r["Status"],
                 r.get("GuestName","—") or "—",
                 str(r.get("CheckInDate","") or ""),
                 str(r.get("CheckOutDate","") or ""),
                 str(r.get("NightsBooked","") or "")) for r in data]
        tbl, _ = self.table(card, cols, rows, row_height=36)
        tbl.pack(fill="both", expand=True, padx=8, pady=8)


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not DB_AVAILABLE:
        print("[INFO] Running in DEMO MODE — MySQL not connected.")
        print("[INFO] Install: pip install mysql-connector-python")
        print("[INFO] Configure DB_CONFIG in database.py, then restart.")

    app = HotelApp()
    app.mainloop()
