from contextlib import contextmanager
from sqlalchemy import text
from .database import engine

@contextmanager
def _conn():
    with engine.connect() as connection:
        yield connection

def fix_price_column():
    print("Fixing price column type...")
    
    # Check current column type
    check_sql = text("""
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name = 'services' AND column_name = 'price'
    """)
    
    # Alter column type
    alter_sql = text("""
        ALTER TABLE services 
        ALTER COLUMN price TYPE double precision 
        USING CASE 
            WHEN price IS NULL THEN NULL 
            WHEN price = '' THEN NULL 
            ELSE price::double precision 
        END
    """)
    
    with _conn() as c:
        # Check current type
        result = c.execute(check_sql)
        current_type = result.scalar()
        print(f"Current price column type: {current_type}")
        
        if current_type == 'text' or current_type == 'character varying':
            print("Converting price column from text to double precision...")
            c.execute(alter_sql)
            c.commit()
            print("Price column type fixed!")
        else:
            print(f"Price column is already {current_type}, no changes needed.")
        
        # Verify the change
        result = c.execute(check_sql)
        new_type = result.scalar()
        print(f"New price column type: {new_type}")

if __name__ == "__main__":
    fix_price_column()
