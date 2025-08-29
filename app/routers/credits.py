from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..deps import get_current_active_user
from ..models import CompanyCredit, CreditTransaction, Company, User
from ..schemas import CompanyCreditOut, CreditTransactionOut, CreditTransactionCreate

router = APIRouter()

@router.get("/company/{company_id}", response_model=CompanyCreditOut)
async def get_company_credit(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca o crédito de uma empresa específica"""
    # Verificar se o usuário é dono da empresa
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    # Buscar ou criar crédito da empresa
    credit = db.query(CompanyCredit).filter(CompanyCredit.company_id == company_id).first()
    if not credit:
        # Criar crédito inicial com 100 MT
        credit = CompanyCredit(
            company_id=company_id,
            balance=100.0,
            total_earned=0.0,
            total_spent=0.0
        )
        db.add(credit)
        db.commit()
        db.refresh(credit)
    
    return credit

@router.get("/company/{company_id}/transactions", response_model=List[CreditTransactionOut])
async def get_company_transactions(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca o histórico de transações de crédito de uma empresa"""
    # Verificar se o usuário é dono da empresa
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    # Buscar crédito da empresa
    credit = db.query(CompanyCredit).filter(CompanyCredit.company_id == company_id).first()
    if not credit:
        return []
    
    # Buscar transações ordenadas por data (mais recentes primeiro)
    transactions = db.query(CreditTransaction)\
        .filter(CreditTransaction.company_credit_id == credit.id)\
        .order_by(CreditTransaction.created_at.desc())\
        .all()
    
    return transactions

@router.post("/company/{company_id}/earn", response_model=CompanyCreditOut)
async def earn_credits(
    company_id: int,
    transaction: CreditTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Adiciona créditos a uma empresa (ganhos, bônus, etc.)"""
    # Verificar se o usuário é dono da empresa
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    # Buscar ou criar crédito da empresa
    credit = db.query(CompanyCredit).filter(CompanyCredit.company_id == company_id).first()
    if not credit:
        credit = CompanyCredit(
            company_id=company_id,
            balance=100.0,
            total_earned=0.0,
            total_spent=0.0
        )
        db.add(credit)
        db.commit()
        db.refresh(credit)
    
    # Validar tipo de transação
    if transaction.type not in ['earn', 'bonus']:
        raise HTTPException(status_code=400, detail="Invalid transaction type for earning credits")
    
    # Validar valor
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Registrar transação
    balance_before = credit.balance
    credit.balance += transaction.amount
    credit.total_earned += transaction.amount
    
    # Criar registro da transação
    credit_transaction = CreditTransaction(
        company_credit_id=credit.id,
        type=transaction.type,
        amount=transaction.amount,
        description=transaction.description,
        balance_before=balance_before,
        balance_after=credit.balance
    )
    
    db.add(credit_transaction)
    db.commit()
    db.refresh(credit)
    
    return credit

@router.post("/company/{company_id}/spend", response_model=CompanyCreditOut)
async def spend_credits(
    company_id: int,
    transaction: CreditTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Gasta créditos de uma empresa (promoções, serviços, etc.)"""
    # Verificar se o usuário é dono da empresa
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    # Buscar crédito da empresa
    credit = db.query(CompanyCredit).filter(CompanyCredit.company_id == company_id).first()
    if not credit:
        raise HTTPException(status_code=404, detail="Company has no credit account")
    
    # Validar tipo de transação
    if transaction.type not in ['spend', 'deduction']:
        raise HTTPException(status_code=400, detail="Invalid transaction type for spending credits")
    
    # Validar valor
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    # Verificar se tem créditos suficientes
    if credit.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    # Registrar transação
    balance_before = credit.balance
    credit.balance -= transaction.amount
    credit.total_spent += transaction.amount
    
    # Criar registro da transação
    credit_transaction = CreditTransaction(
        company_credit_id=credit.id,
        type=transaction.type,
        amount=transaction.amount,
        description=transaction.description,
        balance_before=balance_before,
        balance_after=credit.balance
    )
    
    db.add(credit_transaction)
    db.commit()
    db.refresh(credit)
    
    return credit

@router.get("/company/{company_id}/balance", response_model=dict)
async def get_company_balance(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Retorna o saldo atual de créditos de uma empresa"""
    # Verificar se o usuário é dono da empresa
    company = db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    if company.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    # Buscar crédito da empresa
    credit = db.query(CompanyCredit).filter(CompanyCredit.company_id == company_id).first()
    if not credit:
        # Retornar saldo inicial
        return {
            "company_id": company_id,
            "balance": 100.0,
            "total_earned": 0.0,
            "total_spent": 0.0,
            "message": "Initial credit balance: 100 MT"
        }
    
    return {
        "company_id": company_id,
        "balance": credit.balance,
        "total_earned": credit.total_earned,
        "total_spent": credit.total_spent,
        "last_updated": credit.updated_at
    }
