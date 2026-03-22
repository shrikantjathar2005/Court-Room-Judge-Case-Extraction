import pytesseract
from app.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

try:
    print("Trying with file path...")
    out = pytesseract.image_to_string('uploads/documents/86b69691-f010-4a29-8c32-98100863541a.jpg', config='--oem 3 --psm 6 -l eng')
    print("Success! Length:", len(out))
except Exception as e:
    import traceback
    traceback.print_exc()
