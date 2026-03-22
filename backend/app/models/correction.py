"""Correction model."""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Correction(Base):
    __tablename__ = "corrections"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    ocr_result_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("ocr_results.id", ondelete="CASCADE"), nullable=False
    )
    original_text: Mapped[str] = mapped_column(Text, nullable=True)
    corrected_text: Mapped[str] = mapped_column(Text, nullable=True)
    corrected_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    ocr_result = relationship("OCRResult", back_populates="corrections")
    corrector = relationship("User", back_populates="corrections")

    def __repr__(self):
        return f"<Correction ocr={self.ocr_result_id} v{self.version}>"
