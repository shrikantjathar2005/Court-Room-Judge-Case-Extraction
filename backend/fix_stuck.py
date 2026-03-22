import asyncio
from app.database import async_session
from sqlalchemy import update
from app.models.document import Document

async def main():
    async with async_session() as db:
        await db.execute(update(Document).where(Document.status == 'processing').values(status='uploaded'))
        await db.commit()
        print("Reset stuck documents.")

if __name__ == "__main__":
    asyncio.run(main())
