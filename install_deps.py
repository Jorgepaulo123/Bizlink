#!/usr/bin/env python3
"""
Script para instalar dependências do BizLinkMZ
Tenta diferentes abordagens para resolver problemas de psycopg2
"""

import subprocess
import sys
import os

def run_command(command):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def install_dependencies():
    """Instala as dependências usando diferentes estratégias"""
    print("🚀 Instalando dependências do BizLinkMZ...")
    
    # Lista de comandos para tentar
    commands = [
        # Tentativa 1: pip install normal
        "pip install -r requirements.txt",
        
        # Tentativa 2: pip install com --no-deps para psycopg2
        "pip install psycopg2-binary==2.9.9 --no-deps",
        "pip install -r requirements.txt --no-deps",
        
        # Tentativa 3: pip install com --prefer-binary
        "pip install -r requirements.txt --prefer-binary",
        
        # Tentativa 4: pip install com --force-reinstall
        "pip install -r requirements.txt --force-reinstall",
    ]
    
    for i, command in enumerate(commands, 1):
        print(f"\n📦 Tentativa {i}: {command}")
        
        success, stdout, stderr = run_command(command)
        
        if success:
            print(f"✅ Sucesso na tentativa {i}!")
            print("📋 Output:", stdout)
            return True
        else:
            print(f"❌ Falha na tentativa {i}")
            print("📋 Erro:", stderr)
            
            # Se for psycopg2 que falhou, tenta alternativas
            if "psycopg2" in stderr and "pg_config" in stderr:
                print("🔧 Problema com psycopg2 detectado, tentando alternativas...")
                
                # Tentar instalar asyncpg como alternativa
                alt_success, alt_stdout, alt_stderr = run_command("pip install asyncpg==0.29.0")
                if alt_success:
                    print("✅ asyncpg instalado com sucesso como alternativa!")
                    # Continuar com outras dependências
                    continue
                else:
                    print("❌ asyncpg também falhou")
    
    print("\n❌ Todas as tentativas falharam!")
    print("💡 Sugestões:")
    print("   1. Instale PostgreSQL no Windows")
    print("   2. Use WSL (Windows Subsystem for Linux)")
    print("   3. Use Docker para desenvolvimento")
    print("   4. Use SQLite para desenvolvimento local")
    
    return False

def main():
    """Função principal"""
    print("🔧 Instalador de Dependências BizLinkMZ")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt não encontrado!")
        print("💡 Execute este script no diretório raiz do projeto")
        return 1
    
    # Verificar se pip está disponível
    pip_available, _, _ = run_command("pip --version")
    if not pip_available:
        print("❌ pip não está disponível!")
        print("💡 Instale o Python e pip primeiro")
        return 1
    
    # Instalar dependências
    success = install_dependencies()
    
    if success:
        print("\n🎉 Dependências instaladas com sucesso!")
        print("🚀 Você pode agora executar a aplicação!")
        return 0
    else:
        print("\n💥 Falha na instalação das dependências!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
