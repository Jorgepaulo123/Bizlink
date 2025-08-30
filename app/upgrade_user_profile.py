from contextlib import contextmanager
from sqlalchemy import text
from .database import engine

@contextmanager
def _conn():
    with engine.connect() as connection:
        yield connection

def upgrade_user_profile():
    print("Upgrading user profile with new fields...")
    
    # SQL para adicionar os novos campos ao usuário
    add_profile_fields = text("""
        ALTER TABLE users 
        ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(512),
        ADD COLUMN IF NOT EXISTS cover_photo_url VARCHAR(512),
        ADD COLUMN IF NOT EXISTS gender VARCHAR(20);
    """)
    
    # Criar diretório para fotos de usuário
    create_user_photos_dir = text("""
        -- Este comando será executado pelo Python
        -- Os diretórios serão criados automaticamente quando necessário
    """)
    
    with _conn() as c:
        print("Adding profile fields to users table...")
        c.execute(add_profile_fields)
        c.commit()
        print("✅ User profile fields added successfully!")
        
        # Verificar se os campos foram criados
        check_fields = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            AND column_name IN ('profile_photo_url', 'cover_photo_url', 'gender')
            ORDER BY column_name;
        """)
        
        result = c.execute(check_fields)
        fields = result.fetchall()
        
        print("\nNew fields created:")
        for field in fields:
            print(f"  {field[0]}: {field[1]}")
        
        print("\n🎉 User profile upgrade complete!")

if __name__ == "__main__":
    upgrade_user_profile()
