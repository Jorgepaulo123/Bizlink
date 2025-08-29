from contextlib import contextmanager
from sqlalchemy import text
from .database import engine

@contextmanager
def _conn():
    with engine.connect() as connection:
        yield connection

def create_credit_tables():
    print("Creating credit system tables...")
    
    # SQL para criar as tabelas de crédito
    create_company_credits = text("""
        CREATE TABLE IF NOT EXISTS company_credits (
            id SERIAL PRIMARY KEY,
            company_id INTEGER UNIQUE NOT NULL,
            balance DOUBLE PRECISION DEFAULT 100.0 NOT NULL,
            total_earned DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
            total_spent DOUBLE PRECISION DEFAULT 0.0 NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            updated_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE
        );
    """)
    
    create_credit_transactions = text("""
        CREATE TABLE IF NOT EXISTS credit_transactions (
            id SERIAL PRIMARY KEY,
            company_credit_id INTEGER NOT NULL,
            type VARCHAR(20) NOT NULL,
            amount DOUBLE PRECISION NOT NULL,
            description TEXT,
            balance_before DOUBLE PRECISION NOT NULL,
            balance_after DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMPTZ DEFAULT NOW() NOT NULL,
            FOREIGN KEY (company_credit_id) REFERENCES company_credits(id) ON DELETE CASCADE
        );
    """)
    
    # Criar índices para performance
    create_indexes = text("""
        CREATE INDEX IF NOT EXISTS idx_company_credits_company_id ON company_credits(company_id);
        CREATE INDEX IF NOT EXISTS idx_credit_transactions_company_credit_id ON credit_transactions(company_credit_id);
        CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON credit_transactions(created_at DESC);
    """)
    
    with _conn() as c:
        print("Creating company_credits table...")
        c.execute(create_company_credits)
        
        print("Creating credit_transactions table...")
        c.execute(create_credit_transactions)
        
        print("Creating indexes...")
        c.execute(create_indexes)
        
        c.commit()
        print("✅ Credit system tables created successfully!")

def initialize_existing_companies():
    print("Initializing credit accounts for existing companies...")
    
    # SQL para criar créditos iniciais para empresas existentes
    init_credits = text("""
        INSERT INTO company_credits (company_id, balance, total_earned, total_spent)
        SELECT 
            c.id,
            100.0 as balance,
            0.0 as total_earned,
            0.0 as total_spent
        FROM companies c
        WHERE NOT EXISTS (
            SELECT 1 FROM company_credits cc WHERE cc.company_id = c.id
        );
    """)
    
    with _conn() as c:
        result = c.execute(init_credits)
        c.commit()
        print(f"✅ Initialized credit accounts for {result.rowcount} companies!")

if __name__ == "__main__":
    create_credit_tables()
    initialize_existing_companies()
    print("🎉 Credit system setup complete!")
