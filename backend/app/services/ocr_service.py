"""OCR processing service using Tesseract and OpenCV."""

import os
import time
import uuid
import logging
import cv2
import numpy as np
import pytesseract
from typing import List, Optional
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from app.config import settings
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.utils.image_processing import preprocess_image, resize_for_ocr

logger = logging.getLogger(__name__)

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD


class OCRService:
    """Service for OCR processing operations."""

    @staticmethod
    async def process_document(
        db: AsyncSession,
        document_id: uuid.UUID,
        languages: str = None,
        preprocess: bool = True,
    ) -> List[OCRResult]:
        """Process a document through the OCR pipeline."""
        languages = languages or settings.OCR_LANGUAGES

        # Get document
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Update document status
        document.status = "processing"
        await db.flush()

        ocr_results = []

        try:
            # Get images from document
            images = OCRService._load_document_images(document.file_path, document.file_type)

            for page_num, image in enumerate(images, start=1):
                ocr_result = await OCRService._process_page(
                    db, document_id, page_num, image, languages, preprocess
                )
                ocr_results.append(ocr_result)

            # Update document status
            document.status = "processed"
            document.total_pages = len(images)
            await db.flush()

        except Exception as e:
            logger.error(f"OCR processing failed for document {document_id}: {e}")
            document.status = "uploaded"  # Reset status
            await db.flush()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"OCR processing failed: {str(e)}",
            )

        return ocr_results

    @staticmethod
    async def _process_page(
        db: AsyncSession,
        document_id: uuid.UUID,
        page_number: int,
        image: np.ndarray,
        languages: str,
        preprocess: bool,
    ) -> OCRResult:
        """Process a single page through OCR."""
        start_time = time.time()

        # Create OCR result record
        ocr_result = OCRResult(
            document_id=document_id,
            page_number=page_number,
            language=languages,
            status="processing",
        )
        db.add(ocr_result)
        await db.flush()

        try:
            # Preprocess image
            if preprocess:
                processed_image = preprocess_image(image)
                processed_image = resize_for_ocr(processed_image)
            else:
                processed_image = image

            # Run Tesseract OCR using a temporary file instead of numpy arrays
            # to avoid Leptonica stdin decoding bugs on MacOS.
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                temp_path = tmp_file.name
                
            cv2.imwrite(temp_path, processed_image)
            
            # Switch to PSM 1 (Automatic page segmentation with OSD) to better handle tables.
            custom_config = f"--oem 3 --psm 1 -l {languages}"

            # Get text with confidence data
            data = pytesseract.image_to_data(
                temp_path,
                config=custom_config,
                output_type=pytesseract.Output.DICT,
            )

            # Extract text
            raw_text = pytesseract.image_to_string(
                temp_path,
                config=custom_config,
            )
            
            os.remove(temp_path)

            # Calculate average confidence
            confidences = [
                int(conf)
                for conf, text in zip(data["conf"], data["text"])
                if int(conf) > 0 and text.strip()
            ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            processing_time = time.time() - start_time

            # Update OCR result
            ocr_result.raw_text = raw_text
            ocr_result.confidence_score = round(avg_confidence, 2)
            ocr_result.processing_time = round(processing_time, 2)
            ocr_result.status = "completed"

        except Exception as e:
            logger.error(f"OCR failed for page {page_number}: {e}")
            ocr_result.status = "failed"
            ocr_result.error_message = str(e)
            ocr_result.processing_time = time.time() - start_time

        await db.flush()
        await db.refresh(ocr_result)
        return ocr_result

    @staticmethod
    def _load_document_images(file_path: str, file_type: str) -> List[np.ndarray]:
        """Load document pages as OpenCV images."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        images = []

        if file_type == "pdf":
            try:
                from pdf2image import convert_from_path

                pil_images = convert_from_path(file_path, dpi=300)
                for pil_img in pil_images:
                    img_array = np.array(pil_img)
                    # Convert RGB to BGR for OpenCV
                    if len(img_array.shape) == 3:
                        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    images.append(img_array)
            except Exception as e:
                raise RuntimeError(f"Failed to convert PDF: {e}")
        else:
            # Load image file
            img = cv2.imread(file_path)
            if img is None:
                raise RuntimeError(f"Failed to load image: {file_path}")
            images.append(img)

        return images

    @staticmethod
    async def get_ocr_status(db: AsyncSession, document_id: uuid.UUID) -> dict:
        """Get OCR processing status for a document."""
        # Get document
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        # Get OCR results
        results = await db.execute(
            select(OCRResult)
            .where(OCRResult.document_id == document_id)
            .order_by(OCRResult.page_number)
        )
        ocr_results = results.scalars().all()

        # Calculate stats
        completed = [r for r in ocr_results if r.status == "completed"]
        confidences = [r.confidence_score for r in completed if r.confidence_score]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        return {
            "document_id": document_id,
            "status": document.status,
            "total_pages": document.total_pages,
            "processed_pages": len(completed),
            "average_confidence": round(avg_confidence, 2) if avg_confidence else None,
            "results": ocr_results,
        }

    @staticmethod
    async def get_ocr_results(
        db: AsyncSession, document_id: uuid.UUID
    ) -> List[OCRResult]:
        """Get all OCR results for a document."""
        results = await db.execute(
            select(OCRResult)
            .where(OCRResult.document_id == document_id)
            .order_by(OCRResult.page_number)
        )
        return results.scalars().all()
