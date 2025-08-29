from sqlalchemy import inspect
from .models import Service
from .database import engine

def test_model_mapping():
    print("Testing Service model mapping...")
    
    # Get table info
    inspector = inspect(engine)
    columns = inspector.get_columns('services')
    
    print("\nDatabase table columns:")
    for col in columns:
        print(f"  {col['name']}: {col['type']} (nullable: {col['nullable']})")
    
    # Check model attributes
    print("\nModel attributes:")
    mapper = inspect(Service)
    for attr_name, attr in mapper.attrs.items():
        if hasattr(attr, 'column'):
            col = attr.column
            print(f"  {attr_name}: {type(col.type)} (nullable: {col.nullable})")
    
    # Check specific price column
    price_attr = mapper.attrs.get('price')
    if price_attr and hasattr(price_attr, 'column'):
        price_col = price_attr.column
        print(f"\nPrice column type: {type(price_col.type)}")
        print(f"Price column info: {price_col.type}")

if __name__ == "__main__":
    test_model_mapping()
