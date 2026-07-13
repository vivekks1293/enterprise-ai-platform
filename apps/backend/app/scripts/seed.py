import asyncio

from app.infrastructure.bootstrap.seed_admin import seed_admin
from app.infrastructure.persistence.database import engine

async def main():
    await seed_admin()
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())