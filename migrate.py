#!/usr/bin/env python3
"""
Script de migração para BizLinkMZ
Facilita o gerenciamento de migrações do banco de dados
"""

import subprocess
import sys
import os

def run_command(command):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {command}")
        if e.stderr:
            print(f"Erro: {e.stderr}")
        return False

def main():
    if len(sys.argv) < 2:
        print("""
🔧 Script de Migração BizLinkMZ

Uso: python migrate.py <comando>

Comandos disponíveis:
  status     - Mostra o status atual das migrações
  create     - Cria uma nova migração (ex: python migrate.py create "add new field")
  upgrade    - Aplica todas as migrações pendentes
  downgrade  - Reverte a última migração
  history    - Mostra o histórico de migrações
  current    - Mostra a migração atual
  reset      - Reseta o banco (CUIDADO: apaga todos os dados!)
  help       - Mostra esta ajuda

Exemplos:
  python migrate.py create "add user preferences"
  python migrate.py upgrade
  python migrate.py status
        """)
        return

    command = sys.argv[1].lower()
    
    if command == "status":
        print("📊 Status das migrações:")
        run_command("alembic current")
        print("\n📋 Migrações pendentes:")
        run_command("alembic heads")
        
    elif command == "create":
        if len(sys.argv) < 3:
            print("❌ Erro: Deve especificar uma mensagem para a migração")
            print("Exemplo: python migrate.py create 'add new field'")
            return
        message = sys.argv[2]
        print(f"🆕 Criando migração: {message}")
        run_command(f'alembic revision --autogenerate -m "{message}"')
        
    elif command == "upgrade":
        print("⬆️ Aplicando migrações...")
        run_command("alembic upgrade head")
        
    elif command == "downgrade":
        print("⬇️ Revertendo última migração...")
        run_command("alembic downgrade -1")
        
    elif command == "history":
        print("📚 Histórico de migrações:")
        run_command("alembic history")
        
    elif command == "current":
        print("📍 Migração atual:")
        run_command("alembic current")
        
    elif command == "reset":
        print("⚠️  ATENÇÃO: Isso vai apagar todos os dados do banco!")
        confirm = input("Tem certeza? Digite 'SIM' para confirmar: ")
        if confirm == "SIM":
            print("🗑️ Resetando banco...")
            run_command("alembic downgrade base")
            run_command("alembic upgrade head")
        else:
            print("❌ Operação cancelada")
            
    elif command == "help":
        print("""
🔧 Script de Migração BizLinkMZ

Uso: python migrate.py <comando>

Comandos disponíveis:
  status     - Mostra o status atual das migrações
  create     - Cria uma nova migração (ex: python migrate.py create "add new field")
  upgrade    - Aplica todas as migrações pendentes
  downgrade  - Reverte a última migração
  history    - Mostra o histórico de migrações
  current    - Mostra a migração atual
  reset      - Reseta o banco (CUIDADO: apaga todos os dados!)
  help       - Mostra esta ajuda

Exemplos:
  python migrate.py create "add user preferences"
  python migrate.py upgrade
  python migrate.py status
        """)
        
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("Use 'python migrate.py help' para ver os comandos disponíveis")

if __name__ == "__main__":
    main()
