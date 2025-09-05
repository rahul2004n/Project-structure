-- sample_data.sql
-- Autonomous AP Prototype — Sample Data

-- Drop tables if exist (for re-importing)
DROP TABLE IF EXISTS vendors;
DROP TABLE IF EXISTS purchase_orders;
DROP TABLE IF EXISTS invoices;

-- Vendors table
CREATE TABLE vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase Orders table
CREATE TABLE purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_number TEXT NOT NULL,
    vendor_id INTEGER,
    amount DECIMAL(12,2),
    status TEXT DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

-- Invoices table
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    vendor_id INTEGER,
    invoice_number TEXT,
    total_amount DECIMAL(12,2),
    status TEXT DEFAULT 'pending',
    po_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id)
);

-- Insert sample vendors
INSERT INTO vendors (name, email) VALUES
('Tech Supplies Pvt Ltd', 'billing@techsupplies.com'),
('Office Essentials Co', 'accounts@officeessentials.co'),
('Global Logistics Ltd', 'finance@globallogistics.com');

-- Insert sample POs
INSERT INTO purchase_orders (po_number, vendor_id, amount, status) VALUES
('PO-1001', 1, 25000.00, 'open'),
('PO-1002', 2, 15000.00, 'open'),
('PO-1003', 3, 50000.00, 'open');

-- Insert sample invoices
INSERT INTO invoices (filename, vendor_id, invoice_number, total_amount, status, po_id) VALUES
('/uploads/invoice1.pdf', 1, 'INV-9001', 25000.00, 'touchless', 1),
('/uploads/invoice2.pdf', 2, 'INV-9002', 17000.00, 'exception', 2),
('/uploads/invoice3.pdf', 3, 'INV-9003', 48000.00, 'pending', 3);
