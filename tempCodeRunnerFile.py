import os
import shutil
from fastapi import FastAPI, Request, UploadFile, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
from datetime import datetime

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
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")  # ✅ serve uploads

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

@app.post("/upload")
async def upload_invoice(file: UploadFile, db: Session = Depends(get_db)):
    # Save file in uploads folder
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ✅ सिर्फ filename save करें DB में
    saved_filename = os.path.basename(file.filename)

    new_invoice = models.Invoice(
        filename=saved_filename,
        vendor_id=1,
        invoice_number=f"INV-{datetime.now().strftime('%H%M%S')}",
        total_amount=1000.00,
        status="pending",
    )
    db.add(new_invoice)
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.post("/create_vendor")
async def create_vendor(name: str = Form(...), db: Session = Depends(get_db)):
    vendor = models.Vendor(name=name)
    db.add(vendor)
    db.commit()
    return RedirectResponse("/", status_code=303)

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
        invoice.status = "touchless"
    elif action == "reject":
        invoice.status = "rejected"
    elif action == "force_match" and note:
        try:
            po_id = int(note)
            po = db.query(models.PurchaseOrder).filter(models.PurchaseOrder.id == po_id).first()
            if po:
                invoice.po_id = po.id
                invoice.status = "touchless"
        except:
            pass

    db.commit()
    return RedirectResponse("/", status_code=303)

# ---------- Delete Invoice ----------
@app.post("/delete_invoice")
async def delete_invoice(invoice_id: int = Form(...), db: Session = Depends(get_db)):
    invoice = db.query(models.Invoice).filter(models.Invoice.id == invoice_id).first()
    if invoice:
        # delete file from uploads folder if exists
        file_path = os.path.join(UPLOAD_DIR, invoice.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        db.delete(invoice)
        db.commit()
    return RedirectResponse("/", status_code=303)

# ---------- API endpoints ----------
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
