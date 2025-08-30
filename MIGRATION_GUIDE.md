# 🚀 Guia de Migrações - BizLinkMZ

Este projeto usa **Alembic** para gerenciar migrações do banco de dados PostgreSQL de forma profissional e segura.

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL
- Alembic instalado (`pip install alembic`)
- psycopg2 instalado (`pip install psycopg2-binary`)

## 🔧 Configuração

### 1. Arquivos de Configuração

- **`alembic.ini`** - Configuração principal do Alembic
- **`alembic/env.py`** - Configuração do ambiente (conexão com banco)
- **`alembic/versions/`** - Diretório com as migrações

### 2. Configuração do Banco

O Alembic usa automaticamente a URL do banco definida em `app/settings.py`:

```python
DATABASE_URL: str = "postgresql://user:pass@host:port/database"
```

## 🚀 Comandos Principais

### Usando o Script Helper (Recomendado)

```bash
# Ver status das migrações
python migrate.py status

# Criar nova migração
python migrate.py create "add new field"

# Aplicar migrações
python migrate.py upgrade

# Reverter última migração
python migrate.py downgrade

# Ver histórico
python migrate.py history

# Ver migração atual
python migrate.py current
```

### Usando Alembic Diretamente

```bash
# Ver status
alembic current

# Criar migração
alembic revision --autogenerate -m "descrição da mudança"

# Aplicar migrações
alembic upgrade head

# Reverter migração
alembic downgrade -1

# Ver histórico
alembic history
```

## 📝 Fluxo de Trabalho

### 1. Desenvolvimento

```bash
# 1. Faça mudanças nos modelos (app/models.py)
# 2. Crie uma migração
python migrate.py create "add user preferences"

# 3. Revise o arquivo gerado em alembic/versions/
# 4. Aplique a migração
python migrate.py upgrade
```

### 2. Produção

```bash
# 1. Aplique todas as migrações pendentes
python migrate.py upgrade

# 2. Verifique o status
python migrate.py status
```

## 🏗️ Estrutura das Migrações

Cada migração contém:

```python
"""Add user preferences

Revision ID: abc123def456
Revises: previous_revision_id
Create Date: 2025-08-30 10:00:00

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    """Aplicar mudanças"""
    op.add_column('users', sa.Column('preferences', sa.JSON))

def downgrade() -> None:
    """Reverter mudanças"""
    op.drop_column('users', 'preferences')
```

## ⚠️ Boas Práticas

### ✅ Faça Sempre

- **Teste migrações** em ambiente de desenvolvimento
- **Revise arquivos** gerados automaticamente
- **Use mensagens descritivas** para migrações
- **Faça backup** antes de migrações em produção
- **Teste downgrade** para garantir reversibilidade

### ❌ Nunca Faça

- **Edite migrações** já aplicadas em produção
- **Ignore erros** de migração
- **Aplique migrações** sem revisar
- **Use `--autogenerate`** sem verificar o resultado

## 🔍 Solução de Problemas

### Erro: "relation already exists"

```bash
# Marcar migração como aplicada
alembic stamp head
```

### Erro: "column does not exist"

```bash
# Verificar status atual
alembic current

# Verificar histórico
alembic history

# Aplicar migrações pendentes
alembic upgrade head
```

### Erro de Conexão

```bash
# Verificar configuração do banco
# Verificar se PostgreSQL está rodando
# Verificar credenciais em app/settings.py
```

## 📊 Monitoramento

### Verificar Status

```bash
python migrate.py status
```

### Verificar Histórico

```bash
python migrate.py history
```

### Verificar Migração Atual

```bash
python migrate.py current
```

## 🚨 Emergências

### Resetar Banco (CUIDADO!)

```bash
python migrate.py reset
```

⚠️ **ATENÇÃO**: Isso apaga todos os dados!

### Reverter Migração Específica

```bash
alembic downgrade <revision_id>
```

## 🔗 Links Úteis

- [Documentação Alembic](https://alembic.sqlalchemy.org/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [PostgreSQL](https://www.postgresql.org/docs/)

## 📞 Suporte

Se encontrar problemas:

1. Verifique o status: `python migrate.py status`
2. Verifique o histórico: `python migrate.py history`
3. Verifique logs do Alembic
4. Consulte a documentação oficial

---

**🎯 Dica**: Use sempre `python migrate.py` em vez de comandos diretos do Alembic para uma experiência mais amigável!
