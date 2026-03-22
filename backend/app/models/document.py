"""Document model."""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, BigInteger, Date, DateTime, ForeignKey, func, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=True)
    document_date: Mapped[date] = mapped_column(Date, nullable=True)
    document_type: Mapped[str] = mapped_column(
        String(100), nullable=True
    )  # judgment, order, petition, notification, circular
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=True)  # pdf, jpg, png, tiff
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=True)
    total_pages: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(
        String(50), default="uploaded"
    )  # uploaded, processing, processed, reviewed
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        Uuid(), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    uploader = relationship("User", back_populates="documents", lazy="selectin")
    ocr_results = relationship(
        "OCRResult", back_populates="document", lazy="selectin", cascade="all, delete-orphan"
    )
    keywords = relationship(
        "Keyword", back_populates="document", lazy="selectin", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Document {self.title} ({self.status})>"
