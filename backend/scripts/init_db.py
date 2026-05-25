"""
Create database tables from SQLAlchemy ORM models.

Usage (from backend/):
  python -m scripts.init_db
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.init_db import create_tables
from app.database.session import check_database_connection


async def main() -> None:
    if not await check_database_connection():
        print("ERROR: Cannot connect to database. Check DATABASE_URL in .env")
        sys.exit(1)
    await create_tables()
    print("Tables created: users, performance_data, interview_results, recommendations")


if __name__ == "__main__":
    asyncio.run(main())
