# Autonomous AP Invoice Management System

A full-stack **invoice management system** built with **FastAPI**, **SQLAlchemy**, **Jinja2**, and **Vanilla JavaScript**.  
This system automates invoice handling, vendor management, and purchase order (PO) matching, allowing dynamic invoice approval, rejection, and correction from the frontend.

---

## 🚀 Features

1. **Dynamic Invoice Upload**
   - Upload PDF invoices directly from the frontend.
   - Extracts vendor name, invoice number, total amount, and status automatically from PDFs using `pdfplumber`.

2. **Vendor Management**
   - Create and manage vendors.
   - Assign invoices to vendors automatically or manually.

3. **Purchase Order Management**
   - Create POs and link invoices via **Force Match**.
   - Approve invoices automatically after linking to a PO.

4. **Invoice Actions**
   - **Approve** or **Reject** unpaid invoices.
   - **Edit approved invoices** to correct mistakes (status can be changed back to unpaid or rejected).
   - Delete rejected invoices.

5. **Dynamic Frontend**
   - Table updates dynamically without page reload.
   - Auto-refresh invoices every 30 seconds.
   - PDF invoice links open in a new tab.

6. **PDF Parsing**
   - Uses `pdfplumber` to extract invoice details.
   - Handles multiple page PDFs.

---

## 🛠 Installation & Setup

Follow these **6 steps** to set up the project:

1. **Clone the repository**
   ```bash

   
2. Create a virtual environment

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

3.  Install dependencies

pip install fastapi uvicorn sqlalchemy jinja2 pdfplumber python-multipart

4.   Run the server

uvicorn main:app --reload

5.  Open in browser

Navigate to http://127.0.0.1:8000
 to access the application.
3.    git clone <your-repo-url>
   cd <repo-folder>
