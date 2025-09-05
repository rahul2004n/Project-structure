# ocr_utils.py
import pytesseract
from PIL import Image
import re

# Agar Windows me Tesseract install hai to path set karna hoga
# (e.g., C:\Program Files\Tesseract-OCR\tesseract.exe)
# Uncomment aur apne system ka path daal do:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def parse_invoice(file_path: str):
    """
    Basic OCR parser for invoices.
    Extracts vendor name, invoice number, and total amount.
    """
    try:
        # Image open karo
        img = Image.open(file_path)

        # OCR text extract
        text = pytesseract.image_to_string(img)

        # Defaults
        vendor = None
        invoice_number = None
        total_amount = None

        # Regex patterns (basic)
        vendor_pattern = r"Vendor[:\-]?\s*(\w+)"
        invoice_pattern = r"Invoice\s*No[:\-]?\s*(\w+)"
        amount_pattern = r"Total[:\-]?\s*\$?([\d,.]+)"

        vendor_match = re.search(vendor_pattern, text, re.IGNORECASE)
        if vendor_match:
            vendor = vendor_match.group(1)

        invoice_match = re.search(invoice_pattern, text, re.IGNORECASE)
        if invoice_match:
            invoice_number = invoice_match.group(1)

        amount_match = re.search(amount_pattern, text, re.IGNORECASE)
        if amount_match:
            # ',' ko hata ke float me convert
            total_amount = float(amount_match.group(1).replace(",", ""))

        return {
            "vendor": vendor,
            "invoice_number": invoice_number,
            "total_amount": total_amount,
            "raw_text": text
        }

    except Exception as e:
        return {"error": str(e)}
