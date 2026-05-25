"""
Test database connection and print helpful errors.

Usage (from backend/):
  python -m scripts.check_db
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.database.session import check_database_connection


async def main() -> None:
    url = settings.database_url
    # Hide password in output
    safe = url.split("@")[-1] if "@" in url else url
    print(f"DATABASE_URL → ...@{safe}")

    if await check_database_connection():
        print("OK — database connection successful.")
        print("Run: python -m scripts.init_db && python -m scripts.seed_db")
        return

    print("FAILED — cannot connect to database.\n")
    print("Common fixes:")
    print("  1. Start Docker Desktop, then: docker compose up -d db")
    print("  2. Or use Supabase URL in backend/.env (postgresql+asyncpg://...)")
    print("  3. Wrong password? Update DATABASE_URL in backend/.env")
    print("     Docker default: postgres:postgres@localhost:5432/mentormind")
    print("  4. Port 5432 in use by another Postgres? Stop it or change the port.")
    sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
