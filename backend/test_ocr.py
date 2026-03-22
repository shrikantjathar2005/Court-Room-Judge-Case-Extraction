import asyncio
import uuid
from app.database import async_session
from app.services.ocr_service import OCRService

async def main():
    try:
        doc_id = uuid.UUID("1f222022-b31f-40c0-b6f6-e49691ec3b14")
        async with async_session() as db:
            res = await OCRService.process_document(db, doc_id)
            print("Success!", len(res))
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
