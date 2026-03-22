import asyncio
from app.database import async_session
from app.services.auth_service import AuthService
from app.schemas.user import UserCreate

async def main():
    try:
        async with async_session() as db:
            user = UserCreate(email="test2@example.com", password="password123", full_name="Test", role="user")
            res = await AuthService.register(db, user)
            print(res)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
