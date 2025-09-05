import os
import shutil
from fastapi import FastAPI, Request, UploadFile, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime
import pdfplumber
import re

from database import SessionLocal, engine
import models

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Autonomous AP Prototype (ORM)")

# Middleware for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Static + Templates ----------
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ---------- Dependency ----------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Routes ----------
@app.get("/")
def index(request: Request, db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).all()
    vendors = db.query(models.Vendor).all()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "invoices": invoices, "vendors": vendors},
    )

# ---------- Upload + Parse PDF ----------
@app.post("/upload")
async def upload_invoice(file: UploadFile, db: Session = Depends(get_db)):
    # Save uploaded file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Default values
    invoice_number = f"INV-{datetime.now().strftime('%H%M%S')}"
    vendor_name = "Unknown Vendor"
    total_amount = 0.0
    status = "pending"

    # Parse PDF
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"

        inv_match = re.search(r"Invoice\s*#[:\s]*(\S+)", text, re.IGNORECASE)
        vendor_match = re.search(r"Vendor\s*[:\s]*(.+)", text, re.IGNORECASE)
        total_match = re.search(r"Total\s*Amount\s*[:\s]*([\d.,]+)", text, re.IGNORECASE)
        status_match = re.search(r"Status\s*[:\s]*(\w+)", text, re.IGNORECASE)

        if inv_match:
            invoice_number = inv_match.group(1).strip()
        if vendor_match:
            vendor_name = vendor_match.group(1).strip()
        if total_match:
            total_amount = float(total_match.group(1).replace(",", ""))
        if status_match:
            status = status_match.group(1).lower()
    except Exception as e:
        print("PDF parsing failed:", e)

    # Get or create vendor
    vendor = db.query(models.Vendor).filter(models.Vendor.name == vendor_name).first()
    if not vendor:
        vendor = models.Vendor(name=vendor_name)
        db.add(vendor)
        db.commit()
        db.refresh(vendor)

    # Save invoice in DB
    new_invoice = models.Invoice(
        filename=file.filename,
        invoice_number=invoice_number,
        total_amount=total_amount,
        status=status,
        vendor_id=vendor.id,
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    # Return JSON for frontend dynamic update
    return JSONResponse({
        "success": True,
        "invoice": {
            "id": new_invoice.id,
            "vendor_name": vendor.name,
            "invoice_number": new_invoice.invoice_number,
            "total_amount": new_invoice.total_amount,
            "status": new_invoice.status,
            "filename": new_invoice.filename
        }
    })

# ---------- Create Vendor ----------
@app.post("/create_vendor")
async def create_vendor(name: str = Form(...), db: Session = Depends(get_db)):
    vendor = models.Vendor(name=name)
    db.add(vendor)
    db.commit()
    return RedirectResponse("/", status_code=303)

# ---------- Create Purchase Order ----------
@app.post("/create_po")
async def create_po(
    po_number: str = Form(...),
    vendor_id: int = Form(...),
    amount: float = Form(...),
    db: Session = Depends(get_db),
):
    po = models.PurchaseOrder(po_number=po_number, vendor_id=vendor_id, amount=amount)
    db.add(po)
    db.commit()
    return RedirectResponse("/", status_code=303)

# ---------- Invoice Actions ----------
@app.post("/action")
async def invoice_action(
    invoice_id: int = Form(...),
    action: str = Form(...),
    note: str = Form(None),
    db: Session = Depends(get_db),
):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if not invoice:
        return RedirectResponse("/", status_code=303)

    if action == "approve":
        invoice.status = "approved"
    elif action == "reject":
        invoice.status = "rejected"
    elif action == "force_match" and note:
        try:
            po_id = int(note)
            po = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == po_id).first()
            if po:
                invoice.po_id = po.id
                invoice.status = "approved"
        except:
            pass

    db.commit()
    return RedirectResponse("/", status_code=303)

# ---------- Delete Invoice ----------
@app.post("/delete_invoice")
async def delete_invoice(invoice_id: int = Form(...), db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice:
        file_path = os.path.join(UPLOAD_DIR, invoice.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        db.delete(invoice)
        db.commit()
    return RedirectResponse("/", status_code=303)

# ---------- API for Frontend ----------
@app.get("/api/invoices")
def api_invoices(db: Session = Depends(get_db)):
    invoices = db.query(models.Invoice).all()
    data = []
    for inv in invoices:
        data.append({
            "id": inv.id,
            "filename": inv.filename,
            "vendor_name": inv.vendor.name if inv.vendor else None,
            "invoice_number": inv.invoice_number,
            "total_amount": inv.total_amount,
            "status": inv.status,
            "po": {"po_number": inv.po.po_number} if inv.po else None,
        })
    return JSONResponse(data)
