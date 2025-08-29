from contextlib import contextmanager
from sqlalchemy import text
from .database import engine

@contextmanager
def _conn():
    with engine.connect() as connection:
        yield connection

SQL = {
    "rename_name_to_title": text(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'services' AND column_name = 'name'
          ) THEN
            EXECUTE 'ALTER TABLE services RENAME COLUMN name TO title';
          END IF;
        END $$;
        """
    ),
    "add_missing_columns": text(
        """
        ALTER TABLE services ADD COLUMN IF NOT EXISTS description text;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS price double precision;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS image_url text;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS category text;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS tags text[];
        ALTER TABLE services ADD COLUMN IF NOT EXISTS status varchar(20) DEFAULT 'Ativo' NOT NULL;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS views integer DEFAULT 0 NOT NULL;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS leads integer DEFAULT 0 NOT NULL;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS likes integer DEFAULT 0 NOT NULL;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS is_promoted boolean DEFAULT false NOT NULL;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS created_at timestamptz DEFAULT now() NOT NULL;
        ALTER TABLE services ADD COLUMN IF NOT EXISTS updated_at timestamptz DEFAULT now() NOT NULL;
        """
    ),
    "backfill_title": text(
        """
        UPDATE services SET title = '' WHERE title IS NULL;
        """
    ),
}

def run():
    print("Running services table upgrade...")
    with _conn() as c:
        c.execute(SQL["rename_name_to_title"])
        c.execute(SQL["add_missing_columns"])
        c.execute(SQL["backfill_title"])
        c.commit()
    print("Upgrade complete.")

if __name__ == "__main__":
    run()
