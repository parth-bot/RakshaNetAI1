import os
from functools import lru_cache
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

WIN_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(WIN_PATH):
    pytesseract.pytesseract.tesseract_cmd = WIN_PATH


@lru_cache(maxsize=1)
def ocr_languages():
    """Use English + Hindi + Kannada packs when installed (eng, hin, kan)."""
    try:
        have = set(pytesseract.get_languages(config=""))
    except Exception:
        return "eng"
    return "+".join(l for l in ("eng", "hin", "kan") if l in have) or "eng"


def preprocess_image(image):
    image = image.convert("L")
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image.filter(ImageFilter.SHARPEN)


def extract_text_from_image(uploaded_file):
    try:
        return pytesseract.image_to_string(preprocess_image(Image.open(uploaded_file)), lang=ocr_languages()).strip()
    except Exception as exc:
        return f"OCR_ERROR: {exc}"
