-- ============================================================
-- HOTEL MANAGEMENT SYSTEM - DATABASE SCHEMA
-- Project 11 | DATCOM Lab | NEU
-- ============================================================

CREATE DATABASE IF NOT EXISTS hotel_management 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

USE hotel_management;

-- ============================================================
-- TABLE STRUCTURES
-- ============================================================

-- Guests Table
CREATE TABLE IF NOT EXISTS Guests (
    GuestID     INT AUTO_INCREMENT PRIMARY KEY,
    GuestName   VARCHAR(100) NOT NULL,
    PhoneNumber VARCHAR(20)  NOT NULL,
    Email       VARCHAR(100),
    Address     VARCHAR(255),
    IDNumber    VARCHAR(20),
    Nationality VARCHAR(50) DEFAULT 'Vietnamese',
    CreatedAt   DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_phone (PhoneNumber)
) ENGINE=InnoDB;

-- Rooms Table
CREATE TABLE IF NOT EXISTS Rooms (
    RoomID      INT AUTO_INCREMENT PRIMARY KEY,
    RoomNumber  VARCHAR(10) NOT NULL UNIQUE,
    RoomType    ENUM('Standard','Deluxe','Suite','Presidential') NOT NULL,
    Floor       INT NOT NULL DEFAULT 1,
    Status      ENUM('Available','Occupied','Maintenance','Reserved') NOT NULL DEFAULT 'Available',
    Price       DECIMAL(10,2) NOT NULL,
    MaxOccupancy INT DEFAULT 2,
    Description TEXT,
    UNIQUE KEY uq_roomnumber (RoomNumber)
) ENGINE=InnoDB;

-- Bookings Table
CREATE TABLE IF NOT EXISTS Bookings (
    BookingID    INT AUTO_INCREMENT PRIMARY KEY,
    GuestID      INT NOT NULL,
    RoomID       INT NOT NULL,
    CheckInDate  DATE NOT NULL,
    CheckOutDate DATE NOT NULL,
    Status       ENUM('Reserved','CheckedIn','CheckedOut','Cancelled') NOT NULL DEFAULT 'Reserved',
    Adults       INT DEFAULT 1,
    Children     INT DEFAULT 0,
    Notes        TEXT,
    CreatedAt    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (GuestID) REFERENCES Guests(GuestID) ON DELETE RESTRICT,
    FOREIGN KEY (RoomID)  REFERENCES Rooms(RoomID)   ON DELETE RESTRICT,
    INDEX idx_checkin  (CheckInDate),
    INDEX idx_checkout (CheckOutDate),
    INDEX idx_status   (Status)
) ENGINE=InnoDB;

-- Services Table
CREATE TABLE IF NOT EXISTS Services (
    ServiceID   INT AUTO_INCREMENT PRIMARY KEY,
    ServiceName VARCHAR(100) NOT NULL,
    Category    ENUM('Food','Laundry','Spa','Transport','Other') NOT NULL DEFAULT 'Other',
    Description TEXT,
    Price       DECIMAL(10,2) NOT NULL,
    IsActive    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB;

-- Booking Services (Junction Table)
CREATE TABLE IF NOT EXISTS BookingServices (
    ID          INT AUTO_INCREMENT PRIMARY KEY,
    BookingID   INT NOT NULL,
    ServiceID   INT NOT NULL,
    Quantity    INT DEFAULT 1,
    UsedAt      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BookingID)  REFERENCES Bookings(BookingID) ON DELETE CASCADE,
    FOREIGN KEY (ServiceID)  REFERENCES Services(ServiceID) ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Invoices Table
CREATE TABLE IF NOT EXISTS Invoices (
    InvoiceID      INT AUTO_INCREMENT PRIMARY KEY,
    BookingID      INT NOT NULL UNIQUE,
    GuestID        INT NOT NULL,
    RoomCharges    DECIMAL(10,2) NOT NULL DEFAULT 0,
    ServiceCharges DECIMAL(10,2) NOT NULL DEFAULT 0,
    Discount       DECIMAL(10,2) NOT NULL DEFAULT 0,
    TotalAmount    DECIMAL(10,2) NOT NULL DEFAULT 0,
    PaymentMethod  ENUM('Cash','Card','BankTransfer','Online') DEFAULT 'Cash',
    PaymentStatus  ENUM('Pending','Paid','Refunded') DEFAULT 'Pending',
    PaymentDate    DATETIME,
    CreatedAt      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (BookingID) REFERENCES Bookings(BookingID),
    FOREIGN KEY (GuestID)   REFERENCES Guests(GuestID)
) ENGINE=InnoDB;

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX idx_guests_name   ON Guests(GuestName);
CREATE INDEX idx_guests_phone  ON Guests(PhoneNumber);
CREATE INDEX idx_rooms_status  ON Rooms(Status);
CREATE INDEX idx_rooms_type    ON Rooms(RoomType);
CREATE INDEX idx_invoices_status ON Invoices(PaymentStatus);

-- ============================================================
-- VIEWS
-- ============================================================

-- View: Current room occupancy
CREATE OR REPLACE VIEW vw_RoomOccupancy AS
SELECT 
    r.RoomID, r.RoomNumber, r.RoomType, r.Floor, r.Status, r.Price,
    g.GuestName, g.PhoneNumber,
    b.BookingID, b.CheckInDate, b.CheckOutDate,
    DATEDIFF(b.CheckOutDate, b.CheckInDate) AS NightsBooked
FROM Rooms r
LEFT JOIN Bookings b ON r.RoomID = b.RoomID AND b.Status = 'CheckedIn'
LEFT JOIN Guests  g ON b.GuestID = g.GuestID;

-- View: Guest history
CREATE OR REPLACE VIEW vw_GuestHistory AS
SELECT 
    g.GuestID, g.GuestName, g.PhoneNumber, g.Email,
    COUNT(b.BookingID) AS TotalBookings,
    SUM(DATEDIFF(b.CheckOutDate, b.CheckInDate)) AS TotalNights,
    SUM(i.TotalAmount) AS TotalSpent,
    MAX(b.CheckInDate) AS LastVisit
FROM Guests g
LEFT JOIN Bookings b ON g.GuestID = b.GuestID AND b.Status != 'Cancelled'
LEFT JOIN Invoices i ON b.BookingID = i.BookingID AND i.PaymentStatus = 'Paid'
GROUP BY g.GuestID, g.GuestName, g.PhoneNumber, g.Email;

-- View: Unpaid invoices
CREATE OR REPLACE VIEW vw_UnpaidInvoices AS
SELECT 
    i.InvoiceID, i.BookingID, i.TotalAmount,
    g.GuestName, g.PhoneNumber,
    b.CheckInDate, b.CheckOutDate,
    r.RoomNumber, r.RoomType,
    i.CreatedAt
FROM Invoices i
JOIN Bookings b ON i.BookingID = b.BookingID
JOIN Guests   g ON i.GuestID   = g.GuestID
JOIN Rooms    r ON b.RoomID    = r.RoomID
WHERE i.PaymentStatus = 'Pending';

-- ============================================================
-- STORED PROCEDURES
-- ============================================================

DELIMITER $$

-- Procedure: Check In Guest
CREATE PROCEDURE sp_CheckIn(
    IN p_BookingID INT,
    OUT p_Result   VARCHAR(100)
)
BEGIN
    DECLARE v_RoomID INT;
    DECLARE v_Status VARCHAR(20);

    SELECT RoomID, Status INTO v_RoomID, v_Status
    FROM Bookings WHERE BookingID = p_BookingID;

    IF v_Status != 'Reserved' THEN
        SET p_Result = 'ERROR: Booking is not in Reserved status';
    ELSE
        UPDATE Bookings SET Status = 'CheckedIn' WHERE BookingID = p_BookingID;
        UPDATE Rooms SET Status = 'Occupied' WHERE RoomID = v_RoomID;
        SET p_Result = 'SUCCESS: Guest checked in';
    END IF;
END$$

-- Procedure: Check Out Guest
CREATE PROCEDURE sp_CheckOut(
    IN p_BookingID INT,
    OUT p_Result   VARCHAR(100)
)
BEGIN
    DECLARE v_GuestID   INT;
    DECLARE v_RoomID    INT;
    DECLARE v_RoomPrice DECIMAL(10,2);
    DECLARE v_Nights    INT;
    DECLARE v_RoomCharge DECIMAL(10,2);
    DECLARE v_ServiceCharge DECIMAL(10,2);

    SELECT b.GuestID, b.RoomID, DATEDIFF(b.CheckOutDate, b.CheckInDate),
           r.Price
    INTO v_GuestID, v_RoomID, v_Nights, v_RoomPrice
    FROM Bookings b JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.BookingID = p_BookingID;

    SET v_RoomCharge = v_RoomPrice * v_Nights;

    SELECT IFNULL(SUM(s.Price * bs.Quantity), 0) INTO v_ServiceCharge
    FROM BookingServices bs JOIN Services s ON bs.ServiceID = s.ServiceID
    WHERE bs.BookingID = p_BookingID;

    UPDATE Bookings SET Status = 'CheckedOut' WHERE BookingID = p_BookingID;
    UPDATE Rooms SET Status = 'Available' WHERE RoomID = v_RoomID;

    INSERT INTO Invoices (BookingID, GuestID, RoomCharges, ServiceCharges, TotalAmount)
    VALUES (p_BookingID, v_GuestID, v_RoomCharge, v_ServiceCharge, v_RoomCharge + v_ServiceCharge)
    ON DUPLICATE KEY UPDATE
        RoomCharges = v_RoomCharge,
        ServiceCharges = v_ServiceCharge,
        TotalAmount = v_RoomCharge + v_ServiceCharge;

    SET p_Result = CONCAT('SUCCESS: Invoice created. Total: ', v_RoomCharge + v_ServiceCharge);
END$$

-- Procedure: Make Booking
CREATE PROCEDURE sp_MakeBooking(
    IN p_GuestID     INT,
    IN p_RoomID      INT,
    IN p_CheckIn     DATE,
    IN p_CheckOut    DATE,
    IN p_Adults      INT,
    OUT p_BookingID  INT,
    OUT p_Result     VARCHAR(100)
)
BEGIN
    DECLARE v_Conflict INT DEFAULT 0;

    SELECT COUNT(*) INTO v_Conflict FROM Bookings
    WHERE RoomID = p_RoomID
      AND Status IN ('Reserved','CheckedIn')
      AND NOT (CheckOutDate <= p_CheckIn OR CheckInDate >= p_CheckOut);

    IF v_Conflict > 0 THEN
        SET p_BookingID = 0;
        SET p_Result = 'ERROR: Room not available for selected dates';
    ELSE
        INSERT INTO Bookings (GuestID, RoomID, CheckInDate, CheckOutDate, Adults)
        VALUES (p_GuestID, p_RoomID, p_CheckIn, p_CheckOut, p_Adults);
        SET p_BookingID = LAST_INSERT_ID();
        UPDATE Rooms SET Status = 'Reserved' WHERE RoomID = p_RoomID;
        SET p_Result = 'SUCCESS: Booking created';
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- USER DEFINED FUNCTIONS
-- ============================================================

DELIMITER $$

-- Function: Calculate total booking cost
CREATE FUNCTION fn_BookingCost(p_BookingID INT) 
RETURNS DECIMAL(10,2) DETERMINISTIC
BEGIN
    DECLARE v_RoomCost    DECIMAL(10,2) DEFAULT 0;
    DECLARE v_ServiceCost DECIMAL(10,2) DEFAULT 0;

    SELECT r.Price * DATEDIFF(b.CheckOutDate, b.CheckInDate)
    INTO v_RoomCost
    FROM Bookings b JOIN Rooms r ON b.RoomID = r.RoomID
    WHERE b.BookingID = p_BookingID;

    SELECT IFNULL(SUM(s.Price * bs.Quantity), 0) INTO v_ServiceCost
    FROM BookingServices bs JOIN Services s ON bs.ServiceID = s.ServiceID
    WHERE bs.BookingID = p_BookingID;

    RETURN v_RoomCost + v_ServiceCost;
END$$

-- Function: Apply discount
CREATE FUNCTION fn_ApplyDiscount(p_Amount DECIMAL(10,2), p_Nights INT)
RETURNS DECIMAL(10,2) DETERMINISTIC
BEGIN
    DECLARE v_Discount DECIMAL(5,2) DEFAULT 0;
    IF p_Nights >= 14 THEN SET v_Discount = 0.15;
    ELSEIF p_Nights >= 7 THEN SET v_Discount = 0.10;
    ELSEIF p_Nights >= 3 THEN SET v_Discount = 0.05;
    END IF;
    RETURN p_Amount * (1 - v_Discount);
END$$

DELIMITER ;

-- ============================================================
-- TRIGGERS
-- ============================================================

DELIMITER $$

-- Trigger: Auto update room status on check-in
CREATE TRIGGER trg_AfterBookingUpdate
AFTER UPDATE ON Bookings
FOR EACH ROW
BEGIN
    IF NEW.Status = 'CheckedIn' AND OLD.Status != 'CheckedIn' THEN
        UPDATE Rooms SET Status = 'Occupied' WHERE RoomID = NEW.RoomID;
    ELSEIF NEW.Status = 'CheckedOut' AND OLD.Status != 'CheckedOut' THEN
        UPDATE Rooms SET Status = 'Available' WHERE RoomID = NEW.RoomID;
    ELSEIF NEW.Status = 'Cancelled' THEN
        UPDATE Rooms SET Status = 'Available' WHERE RoomID = NEW.RoomID;
    END IF;
END$$

DELIMITER ;

-- ============================================================
-- USER ACCESS CONTROL
-- ============================================================

-- Receptionist: Can manage guests and bookings, view rooms
CREATE USER IF NOT EXISTS 'receptionist'@'localhost' IDENTIFIED BY 'Recept!on2024';
GRANT SELECT, INSERT, UPDATE ON hotel_management.Guests   TO 'receptionist'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hotel_management.Bookings TO 'receptionist'@'localhost';
GRANT SELECT ON hotel_management.Rooms    TO 'receptionist'@'localhost';
GRANT SELECT ON hotel_management.Services TO 'receptionist'@'localhost';
GRANT SELECT, INSERT ON hotel_management.BookingServices TO 'receptionist'@'localhost';
GRANT SELECT ON hotel_management.vw_RoomOccupancy TO 'receptionist'@'localhost';

-- Manager: Full access except user management
CREATE USER IF NOT EXISTS 'manager'@'localhost' IDENTIFIED BY 'M@nager2024!';
GRANT SELECT, INSERT, UPDATE, DELETE ON hotel_management.* TO 'manager'@'localhost';

-- Accountant: Invoice and payment focus
CREATE USER IF NOT EXISTS 'accountant'@'localhost' IDENTIFIED BY 'Acc0unt!2024';
GRANT SELECT ON hotel_management.Bookings  TO 'accountant'@'localhost';
GRANT SELECT ON hotel_management.Guests    TO 'accountant'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hotel_management.Invoices TO 'accountant'@'localhost';
GRANT SELECT ON hotel_management.vw_UnpaidInvoices TO 'accountant'@'localhost';
GRANT SELECT ON hotel_management.vw_GuestHistory   TO 'accountant'@'localhost';

FLUSH PRIVILEGES;
