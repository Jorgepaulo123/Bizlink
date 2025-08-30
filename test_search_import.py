#!/usr/bin/env python3
"""
Teste simples para verificar importações do módulo search
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testando importações...")
    
    # Testar importação do database
    print("📊 Importando database...")
    from app.database import get_db
    print("✅ Database importado com sucesso")
    
    # Testar importação dos models
    print("🏗️ Importando models...")
    from app.models import Service, Company, User, CompanyPortfolio
    print("✅ Models importados com sucesso")
    
    # Testar importação do router search
    print("🔍 Importando router search...")
    from app.routers.search import router
    print("✅ Router search importado com sucesso")
    
    print("\n🎉 Todas as importações funcionaram!")
    
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print(f"📍 Arquivo: {e.__traceback__.tb_frame.f_code.co_filename}")
    print(f"📍 Linha: {e.__traceback__.tb_lineno}")
except Exception as e:
    print(f"❌ Erro inesperado: {e}")
    import traceback
    traceback.print_exc()
