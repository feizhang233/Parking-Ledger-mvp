from pathlib import Path

from ledger.db import DB_PATH, get_connection, init_db


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    init_db()
    seed_sql = Path(__file__).resolve().parent / "sql" / "seed.sql"
    with get_connection() as conn:
        conn.executescript(seed_sql.read_text(encoding="utf-8"))
        conn.commit()
    print("Sample data initialized successfully.")


if __name__ == "__main__":
    main()
