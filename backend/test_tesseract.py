import traceback
import cv2
import numpy as np
import pytesseract
from app.config import settings

pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

# create a dummy image
img = np.zeros((100, 200, 3), dtype=np.uint8)

try:
    print("Running image_to_string...")
    res = pytesseract.image_to_string(img, config="--oem 3 --psm 6 -l eng")
    print("Success:", res)
except Exception as e:
    traceback.print_exc()
