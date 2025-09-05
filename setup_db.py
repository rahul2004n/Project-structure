import sqlite3

# Create or connect to SQLite DB
conn = sqlite3.connect("ap_demo.db")
cursor = conn.cursor()

# Create tables
cursor.executescript("""
CREATE TABLE IF NOT EXISTS vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    po_number TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id)
);

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER,
    po_id INTEGER,
    invoice_number TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    status TEXT DEFAULT 'Pending',
    file_path TEXT,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (po_id) REFERENCES purchase_orders(id)
);

CREATE TABLE IF NOT EXISTS exceptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    issue TEXT NOT NULL,
    status TEXT DEFAULT 'Open',
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);
""")

# Insert sample data
cursor.executescript("""
INSERT INTO vendors (name, address) VALUES
('Tata Consultancy Services', 'Mumbai, India'),
('Infosys Limited', 'Bangalore, India'),
('Wipro Technologies', 'Hyderabad, India');

INSERT INTO purchase_orders (vendor_id, po_number, amount) VALUES
(1, 'PO1001', 50000.00),
(2, 'PO2001', 75000.00),
(3, 'PO3001', 60000.00);

INSERT INTO invoices (vendor_id, po_id, invoice_number, amount, status, file_path) VALUES
(1, 1, 'INV-TCS-001', 50000.00, 'Approved', 'uploads/inv_tcs_001.pdf'),
(2, 2, 'INV-INFY-001', 80000.00, 'Exception', 'uploads/inv_infy_001.pdf'),
(3, 3, 'INV-WIPRO-001', 60000.00, 'Approved', 'uploads/inv_wipro_001.pdf');

INSERT INTO exceptions (invoice_id, issue, status) VALUES
(2, 'Invoice amount does not match PO amount', 'Open');
""")

conn.commit()
conn.close()

print("✅ ap_demo.db created successfully!")
