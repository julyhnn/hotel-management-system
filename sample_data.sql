-- ============================================================
-- SAMPLE DATA - Hotel Management System
-- ============================================================

USE hotel_management;

-- ============================================================
-- ROOMS (20 rooms across 4 floors)
-- ============================================================
INSERT INTO Rooms (RoomNumber, RoomType, Floor, Status, Price, MaxOccupancy, Description) VALUES
('101','Standard',1,'Available',125.00,2,'Cozy standard room with garden view'),
('102','Standard',1,'Available',125.00,2,'Cozy standard room with garden view'),
('103','Standard',1,'Available',135.00,2,'Standard room with partial sea view'),
('104','Standard',1,'Maintenance',125.00,2,'Under renovation'),
('105','Standard',1,'Available',125.00,2,'Standard room near pool'),
('201','Deluxe',2,'Available',220.00,3,'Spacious deluxe room with sea view balcony'),
('202','Deluxe',2,'Available',220.00,3,'Deluxe room with Aegean view'),
('203','Deluxe',2,'Reserved',235.00,3,'Corner deluxe room, panoramic view'),
('204','Deluxe',2,'Available',220.00,3,'Deluxe room with private terrace'),
('205','Deluxe',2,'Occupied',220.00,3,'Deluxe room with sunset view'),
('301','Suite',3,'Available',380.00,4,'Luxury suite with jacuzzi and sea view'),
('302','Suite',3,'Available',380.00,4,'Suite with private pool access'),
('303','Suite',3,'Occupied',395.00,4,'Corner suite, full panoramic Santorini view'),
('304','Suite',3,'Reserved',380.00,4,'Suite with king bed and lounge area'),
('305','Suite',3,'Available',380.00,4,'Honeymoon suite with rose petal décor'),
('401','Presidential',4,'Available',750.00,6,'Presidential villa with infinity pool'),
('402','Presidential',4,'Available',780.00,6,'Presidential suite, full rooftop terrace'),
('403','Presidential',4,'Reserved',750.00,4,'Executive presidential room'),
('404','Presidential',4,'Available',750.00,6,'Royal suite with butler service'),
('405','Presidential',4,'Available',800.00,6,'Penthouse presidential, best view in hotel');

-- ============================================================
-- GUESTS (10 guests)
-- ============================================================
INSERT INTO Guests (GuestName, PhoneNumber, Email, Address, IDNumber, Nationality) VALUES
('Nguyen Van An',       '0901234567','an.nguyen@email.com',   'Ha Noi, Vietnam',          '001234567890','Vietnamese'),
('Tran Thi Bich',       '0912345678','bich.tran@email.com',   'Ho Chi Minh, Vietnam',     '079234567891','Vietnamese'),
('Le Minh Cuong',       '0923456789','cuong.le@email.com',    'Da Nang, Vietnam',          '048345678902','Vietnamese'),
('Pham Thu Dung',       '0934567890','dung.pham@email.com',   'Hai Phong, Vietnam',        '031456789013','Vietnamese'),
('Hoang Van Em',        '0945678901','em.hoang@email.com',    'Can Tho, Vietnam',          '092567890124','Vietnamese'),
('James Wilson',        '0956789012','jwilson@gmail.com',     'London, United Kingdom',   'UK9876543','British'),
('Maria Garcia',        '0967890123','mgarcia@yahoo.com',     'Madrid, Spain',             'ES12345678','Spanish'),
('Yuki Tanaka',         '0978901234','ytanaka@mail.jp',       'Tokyo, Japan',              'JP87654321','Japanese'),
('Michael Chen',        '0989012345','mchen@outlook.com',     'Singapore',                 'SG12345678','Singaporean'),
('Sophie Dubois',       '0990123456','sdubois@mail.fr',       'Paris, France',             'FR98765432','French');

-- ============================================================
-- SERVICES (10 services)
-- ============================================================
INSERT INTO Services (ServiceName, Category, Description, Price) VALUES
('Airport Transfer',      'Transport','Round-trip airport pickup and drop-off',45.00),
('Room Service Breakfast','Food','In-room continental breakfast for 2',35.00),
('Full Board Dinner',     'Food','3-course dinner at rooftop restaurant',65.00),
('Laundry & Ironing',     'Laundry','Full laundry service per bag',25.00),
('Dry Cleaning',          'Laundry','Dry cleaning per garment',15.00),
('Spa Package - Basic',   'Spa','60-min aromatherapy massage',80.00),
('Spa Package - Premium', 'Spa','120-min full body treatment + facial',150.00),
('City Tour',             'Transport','Half-day guided city sightseeing tour',55.00),
('Mini Bar Restock',      'Food','Premium mini bar package',40.00),
('Late Checkout',         'Other','Checkout extended to 3:00 PM',30.00);

-- ============================================================
-- BOOKINGS (10 bookings)
-- ============================================================
INSERT INTO Bookings (GuestID, RoomID, CheckInDate, CheckOutDate, Status, Adults, Children, Notes) VALUES
(1, 1,  '2025-05-01','2025-05-04','CheckedOut',2,0,'Booked via website'),
(2, 6,  '2025-05-03','2025-05-07','CheckedOut',2,1,'Anniversary couple, request rose setup'),
(3, 11, '2025-05-05','2025-05-10','CheckedOut',2,0,''),
(4, 16, '2025-05-07','2025-05-12','CheckedOut',4,2,'VIP guest, requires butler'),
(5, 3,  '2025-05-10','2025-05-13','CheckedOut',1,0,''),
(6, 7,  '2025-05-15','2025-05-20','CheckedIn', 2,0,'British tourist'),
(7, 13, '2025-05-14','2025-05-18','CheckedIn', 2,0,'Honeymoon couple'),
(8, 4,  '2025-05-20','2025-05-25','Reserved',  2,1,''),
(9, 17, '2025-05-18','2025-05-22','Reserved',  3,0,'Business traveler'),
(10,12, '2025-05-25','2025-05-30','Reserved',  2,0,'French holiday');

-- ============================================================
-- BOOKING SERVICES
-- ============================================================
INSERT INTO BookingServices (BookingID, ServiceID, Quantity) VALUES
(1,2,3),(1,4,1),
(2,2,4),(2,6,1),(2,1,1),
(3,7,1),(3,2,5),
(4,1,1),(4,2,5),(4,3,5),(4,7,2),
(5,2,3),(5,8,1),
(6,2,2),(6,9,1),
(7,7,1),(7,2,4),
(8,1,1),
(9,1,1),(9,10,1),
(10,6,1);

-- ============================================================
-- INVOICES (for checked-out bookings)
-- ============================================================
INSERT INTO Invoices (BookingID, GuestID, RoomCharges, ServiceCharges, TotalAmount, PaymentMethod, PaymentStatus, PaymentDate) VALUES
(1,1, 375.00, 130.00, 505.00,  'Card',        'Paid',   '2025-05-04 11:00:00'),
(2,2, 880.00, 235.00, 1115.00, 'BankTransfer','Paid',   '2025-05-07 12:00:00'),
(3,3,1900.00, 295.00, 2195.00, 'Cash',        'Paid',   '2025-05-10 10:30:00'),
(4,4,3750.00, 770.00, 4520.00, 'Card',        'Paid',   '2025-05-12 13:00:00'),
(5,5, 405.00, 125.00, 530.00,  'Cash',        'Paid',   '2025-05-13 11:00:00'),
(6,6,1100.00,  75.00,1175.00,  'Card',        'Pending', NULL),
(7,7,1580.00, 310.00,1890.00,  'Card',        'Pending', NULL);
