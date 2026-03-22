"""Image preprocessing utilities for OCR pipeline using OpenCV."""

import cv2
import numpy as np
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def preprocess_image(image: np.ndarray) -> np.ndarray:
    """
    Full preprocessing pipeline for OCR optimization.
    Steps: grayscale → denoise → threshold → deskew
    """
    processed = to_grayscale(image)
    processed = denoise(processed)
    processed = adaptive_threshold(processed)
    processed = deskew(processed)
    return processed


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert image to grayscale if it's in color."""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def denoise(image: np.ndarray) -> np.ndarray:
    """Remove noise from image using Non-local Means Denoising."""
    try:
        return cv2.fastNlMeansDenoising(image, h=30, templateWindowSize=7, searchWindowSize=21)
    except Exception as e:
        logger.warning(f"Denoising failed: {e}, returning original image")
        return image


def adaptive_threshold(image: np.ndarray) -> np.ndarray:
    """Apply adaptive thresholding for better text contrast."""
    try:
        return cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2,
        )
    except Exception as e:
        logger.warning(f"Adaptive threshold failed: {e}, trying Otsu's method")
        try:
            _, result = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            return result
        except Exception:
            return image


def deskew(image: np.ndarray) -> np.ndarray:
    """Correct image skew/rotation for better OCR accuracy."""
    try:
        # Find all non-zero points (text pixels)
        coords = np.column_stack(np.where(image > 0))
        if len(coords) < 10:
            return image

        # Get the minimum area bounding rectangle
        angle = cv2.minAreaRect(coords)[-1]

        # Adjust angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only deskew if angle is significant but not too large
        if abs(angle) < 0.5 or abs(angle) > 15:
            return image

        # Rotate the image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
        )
        return rotated
    except Exception as e:
        logger.warning(f"Deskew failed: {e}, returning original image")
        return image


def resize_for_ocr(image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
    """Resize image to target DPI for optimal OCR performance."""
    try:
        height, width = image.shape[:2]
        # Assume 72 DPI for screen images, scale up to target DPI
        scale_factor = target_dpi / 72.0
        if scale_factor > 1.0 and max(width, height) < 2000:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        return image
    except Exception as e:
        logger.warning(f"Resize failed: {e}, returning original image")
        return image


def get_image_quality_score(image: np.ndarray) -> float:
    """
    Estimate image quality using Laplacian variance.
    Higher values indicate sharper (better quality) images.
    """
    try:
        gray = to_grayscale(image) if len(image.shape) == 3 else image
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        # Normalize to 0-100 scale
        return min(100.0, laplacian_var / 5.0)
    except Exception:
        return 0.0
