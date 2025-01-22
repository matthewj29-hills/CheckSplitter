import pytesseract
from PIL import Image, UnidentifiedImageError, ImageOps
import re

def preprocess_image(image_path):
    """
    Preprocess the image to improve OCR accuracy.
    """
    try:
        image = Image.open(image_path)
        image = ImageOps.grayscale(image)  # Convert to grayscale
        return image
    except UnidentifiedImageError:
        raise ValueError("Unsupported or corrupted image format.")

def extract_text_from_image(image_path):
    """
    Extract text from an image file using Tesseract OCR.
    """
    try:
        image = preprocess_image(image_path)
        text = pytesseract.image_to_string(image).strip()

        if not text:
            raise ValueError("No readable text found in the image. Please upload a clearer receipt.")

        return text
    except Exception as e:
        return f"Error reading image: {e}"

def parse_receipt(text):
    """
    Parse the extracted text to identify and organize receipt details.
    """
    items = []
    subtotal, tax, tip, total = None, None, None, None

    # Normalize text for case-insensitive processing
    lines = [line.strip() for line in text.lower().split('\n') if line.strip()]
    
    for line in lines:
        # Match items with quantity, name, and price (e.g. "2 Soda $20.00")
        item_match = re.search(r'(\d+)\s+(.+?)\s+\$?(\d+\.\d{2})', line)
        if item_match:
            qty, name, price = item_match.groups()
            items.append({"name": name.strip(), "quantity": int(qty), "price": float(price)})
            continue

        # Match subtotal (case-insensitive search)
        if re.search(r'subtotal|sub total', line):
            subtotal_match = re.search(r'\$?(\d+\.\d{2})', line)
            if subtotal_match:
                subtotal = float(subtotal_match.group(1))
                continue

        # Match tax
        if "tax" in line:
            tax_match = re.search(r'\$?(\d+\.\d{2})', line)
            if tax_match:
                tax = float(tax_match.group(1))
                continue

        # Match tip or gratuity
        if re.search(r'tip|gratuity', line):
            tip_match = re.search(r'\$?(\d+\.\d{2})', line)
            if tip_match:
                tip = float(tip_match.group(1))
                continue

        # Match total
        if re.search(r'total|amount due', line):
            total_match = re.search(r'\$?(\d+\.\d{2})', line)
            if total_match:
                total = float(total_match.group(1))
                continue

    # Calculate missing values if possible
    if total and subtotal:
        if tax is None:
            tax = round(total - subtotal - (tip if tip else 0), 2)
        if tip is None and tax is not None:
            tip = round(total - subtotal - tax, 2)

    # Ensure all values are properly assigned, else default to 0
    return {
        "items": items,
        "subtotal": subtotal if subtotal is not None else 0.0,
        "tax": tax if tax is not None else 0.0,
        "tip": tip if tip is not None else 0.0,
        "total": total if total is not None else 0.0
    }
