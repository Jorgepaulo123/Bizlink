from sqlalchemy import text
from .database import engine

def test_service_creation():
    print("Testing service creation directly in database...")
    
    # Test data
    test_service = {
        'company_id': 1,
        'title': 'Test Service',
        'description': 'Test Description',
        'price': 99.99,  # This should be a float
        'category': 'Test Category',
        'tags': ['tag1', 'tag2'],  # This should be an array
        'status': 'Ativo',
        'views': 0,
        'leads': 0,
        'likes': 0,
        'is_promoted': False
    }
    
    # Insert directly with SQL
    insert_sql = text("""
        INSERT INTO services (
            company_id, title, description, price, category, tags, 
            status, views, leads, likes, is_promoted
        ) VALUES (
            :company_id, :title, :description, :price, :category, :tags,
            :status, :views, :leads, :likes, :is_promoted
        ) RETURNING id
    """)
    
    try:
        with engine.connect() as conn:
            result = conn.execute(insert_sql, test_service)
            service_id = result.scalar()
            conn.commit()
            print(f"✅ Service created successfully with ID: {service_id}")
            
            # Verify the data
            select_sql = text("SELECT * FROM services WHERE id = :id")
            result = conn.execute(select_sql, {'id': service_id})
            service = result.fetchone()
            
            print(f"✅ Service retrieved: {dict(service)}")
            
            # Clean up
            delete_sql = text("DELETE FROM services WHERE id = :id")
            conn.execute(delete_sql, {'id': service_id})
            conn.commit()
            print(f"✅ Test service cleaned up")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_service_creation()
