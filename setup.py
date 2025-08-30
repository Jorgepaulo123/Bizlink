from setuptools import setup, find_packages

setup(
    name="bizlink-api",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-multipart>=0.0.6",
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.0",
        "alembic>=1.13.0",
        "python-dotenv>=1.0.0",
        "qrcode[pil]>=7.4.0",
        "Pillow>=10.4.0",
    ],
    python_requires=">=3.8",
)
