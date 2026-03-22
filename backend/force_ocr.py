import asyncio
from app.database import async_session
from sqlalchemy import select, update
from app.models.document import Document
from app.services.ocr_service import OCRService

async def main():
    async with async_session() as db:
        # Get all stuck documents
        result = await db.execute(select(Document).where(Document.status == 'processing'))
        docs = result.scalars().all()
        
        for doc in docs:
            print(f'Testing Doc: {doc.title} ({doc.id}) format: {doc.file_type}')
            try:
                res = await OCRService.process_document(db, doc.id)
                await db.commit()
                print(f'Saved {len(res)} pages!')
            except Exception as e:
                import traceback
                traceback.print_exc()
                
if __name__ == "__main__":
    asyncio.run(main())
