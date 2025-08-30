from fastapi import APIRouter, Depends, Query as FastAPIQuery
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text
import sqlalchemy as sa
from typing import Optional, List
import re

from ..database import get_db
from ..models import Service, Company, User, CompanyPortfolio
from ..schemas import ServiceOut, CompanyOut, UserOut

router = APIRouter()

@router.get("/feed")
async def get_feed(
    last_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Feed com 10 itens por vez e paginação automática
    Retorna serviços, empresas, usuários e portfólios misturados
    """
    
    try:
        # Limitar o limite máximo
        if limit > 50:
            limit = 50
        
        # Buscar serviços ativos
        services_query = db.query(Service).filter(Service.status == "Ativo")
        if last_id:
            services_query = services_query.filter(Service.id < last_id)
        services = services_query.order_by(Service.id.desc()).limit(limit).all()
        
        # Buscar empresas
        companies_query = db.query(Company)
        if last_id:
            companies_query = companies_query.filter(Company.id < last_id)
        companies = companies_query.order_by(Company.id.desc()).limit(limit).all()
        
        # Buscar usuários ativos
        users_query = db.query(User).filter(User.is_active == True)
        if last_id:
            users_query = users_query.filter(User.id < last_id)
        users = users_query.order_by(User.id.desc()).limit(limit).all()
        
        # Buscar portfólios
        portfolios_query = db.query(CompanyPortfolio)
        if last_id:
            portfolios_query = portfolios_query.filter(CompanyPortfolio.id < last_id)
        portfolios = portfolios_query.order_by(CompanyPortfolio.id.desc()).limit(limit).all()
        
        # Combinar todos os itens
        all_items = []
        
        # Adicionar serviços
        for service in services:
            all_items.append({
                "id": service.id,
                "type": "service",
                "title": service.title,
                "description": service.description,
                "price": service.price,
                "category": service.category,
                "tags": service.tags,
                "status": service.status,
                "company_id": service.company_id,
                "image_url": service.image_url,
                "views": service.views,
                "leads": service.leads,
                "likes": service.likes,
                "is_promoted": service.is_promoted,
                "created_at": service.created_at
            })
        
        # Adicionar empresas
        for company in companies:
            all_items.append({
                "id": company.id,
                "type": "company",
                "name": company.name,
                "description": company.description,
                "logo_url": company.logo_url,
                "cover_url": company.cover_url,
                "province": company.province,
                "district": company.district,
                "address": company.address,
                "nationality": company.nationality,
                "website": company.website,
                "email": company.email,
                "whatsapp": company.whatsapp
            })
        
        # Adicionar usuários
        for user in users:
            all_items.append({
                "id": user.id,
                "type": "user",
                "full_name": user.full_name,
                "email": user.email,
                "profile_photo_url": user.profile_photo_url,
                "cover_photo_url": user.cover_photo_url,
                "gender": user.gender
            })
        
        # Adicionar portfólios
        for portfolio in portfolios:
            all_items.append({
                "id": portfolio.id,
                "type": "portfolio",
                "title": portfolio.title,
                "description": portfolio.description,
                "media_url": portfolio.media_url,
                "link": portfolio.link,
                "company_id": portfolio.company_id,
                "created_at": portfolio.created_at
            })
        
        # Ordenar por ID (mais recentes primeiro) e limitar
        all_items.sort(key=lambda x: x['id'], reverse=True)
        feed_items = all_items[:limit]
        
        # Preparar resposta
        return {
            "items": feed_items,
            "total_returned": len(feed_items),
            "has_more": len(all_items) > limit,
            "next_page_info": {
                "last_id": feed_items[-1]['id'] if feed_items else None
            } if feed_items else None,
            "summary": {
                "services_count": len([item for item in feed_items if item['type'] == 'service']),
                "companies_count": len([item for item in feed_items if item['type'] == 'company']),
                "users_count": len([item for item in feed_items if item['type'] == 'user']),
                "portfolios_count": len([item for item in feed_items if item['type'] == 'portfolio'])
            }
        }
        
    except Exception as e:
        return {
            "error": f"Erro no feed: {str(e)}",
            "items": [],
            "total_returned": 0,
            "has_more": False,
            "next_page_info": None
        }

@router.get("/", response_model=dict)
async def global_search(
    q: str = FastAPIQuery(..., description="Termo de pesquisa"),
    db: Session = Depends(get_db),
    limit: int = FastAPIQuery(20, ge=1, le=100, description="Limite de resultados por categoria")
):
    """
    Pesquisa global em serviços, empresas, usuários e portfólios
    Busca por: nome, categoria, tags, localização
    """
    
    try:
        # Normalizar termo de pesquisa
        search_term = q.strip().lower()
        if len(search_term) < 2:
            return {
                "query": q,
                "total_results": 0,
                "message": "Termo de pesquisa deve ter pelo menos 2 caracteres",
                "results": {
                    "services": [],
                    "companies": [],
                    "users": [],
                    "portfolios": []
                }
            }
        
        # Preparar padrões de busca
        search_pattern = f"%{search_term}%"
        
        # 1. BUSCAR SERVIÇOS
        services_query = db.query(Service).filter(
            or_(
                Service.title.ilike(search_pattern),
                Service.description.ilike(search_pattern),
                Service.category.ilike(search_pattern)
            )
        ).limit(limit)
        
        services = services_query.all()
        
        # 2. BUSCAR EMPRESAS
        companies_query = db.query(Company).filter(
            or_(
                Company.name.ilike(search_pattern),
                Company.description.ilike(search_pattern),
                Company.province.ilike(search_pattern),
                Company.district.ilike(search_pattern),
                Company.address.ilike(search_pattern),
                Company.nationality.ilike(search_pattern)
            )
        ).limit(limit)
        
        companies = companies_query.all()
        
        # 3. BUSCAR USUÁRIOS
        users_query = db.query(User).filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        ).limit(limit)
        
        users = users_query.all()
        
        # 4. BUSCAR PORTFÓLIOS
        portfolios_query = db.query(CompanyPortfolio).filter(
            or_(
                CompanyPortfolio.title.ilike(search_pattern),
                CompanyPortfolio.description.ilike(search_pattern)
            )
        ).limit(limit)
        
        portfolios = portfolios_query.all()
        
        # Calcular total de resultados
        total_results = len(services) + len(companies) + len(users) + len(portfolios)
        
        # Preparar resposta - apenas campos que existem nos modelos
        results = {
            "services": [
                {
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                    "price": s.price,
                    "category": s.category,
                    "tags": s.tags,
                    "status": s.status,
                    "company_id": s.company_id,
                    "image_url": s.image_url,
                    "views": s.views,
                    "leads": s.leads,
                    "likes": s.likes,
                    "is_promoted": s.is_promoted,
                    "created_at": s.created_at
                } for s in services
            ],
            "companies": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "logo_url": c.logo_url,
                    "cover_url": c.cover_url,
                    "province": c.province,
                    "district": c.district,
                    "address": c.address,
                    "nationality": c.nationality,
                    "website": c.website,
                    "email": c.email,
                    "whatsapp": c.whatsapp
                } for c in companies
            ],
            "users": [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "profile_photo_url": u.profile_photo_url,
                    "cover_photo_url": u.cover_photo_url,
                    "gender": u.gender
                } for u in users
            ],
            "portfolios": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "media_url": p.media_url,
                    "link": p.link,
                    "company_id": p.company_id,
                    "created_at": p.created_at
                } for p in portfolios
            ]
        }
        
        return {
            "query": q,
            "total_results": total_results,
            "results": results,
            "summary": {
                "services_count": len(services),
                "companies_count": len(companies),
                "users_count": len(users),
                "portfolios_count": len(portfolios)
            }
        }
    except Exception as e:
        return {
            "query": q,
            "total_results": 0,
            "error": f"Erro na pesquisa: {str(e)}",
            "results": {
                "services": [],
                "companies": [],
                "users": [],
                "portfolios": []
            }
        }

@router.get("/advanced", response_model=dict)
async def advanced_search(
    q: str = FastAPIQuery(..., description="Termo de pesquisa"),
    category: Optional[str] = FastAPIQuery(None, description="Filtrar por categoria"),
    location: Optional[str] = FastAPIQuery(None, description="Filtrar por localização (província/distrito)"),
    tags: Optional[str] = FastAPIQuery(None, description="Filtrar por tags (separadas por vírgula)"),
    min_price: Optional[float] = FastAPIQuery(None, description="Preço mínimo"),
    max_price: Optional[float] = FastAPIQuery(None, description="Preço máximo"),
    db: Session = Depends(get_db),
    limit: int = FastAPIQuery(20, ge=1, le=100, description="Limite de resultados por categoria")
):
    """
    Pesquisa avançada com filtros específicos
    """
    
    try:
        search_term = q.strip().lower()
        if len(search_term) < 2:
            return {
                "query": q,
                "filters": {"category": category, "location": location, "tags": tags, "price_range": f"{min_price}-{max_price}"},
                "total_results": 0,
                "message": "Termo de pesquisa deve ter pelo menos 2 caracteres",
                "results": {"services": [], "companies": [], "users": [], "portfolios": []}
            }
        
        search_pattern = f"%{search_term}%"
        
        # Construir filtros para serviços
        service_filters = [
            or_(
                Service.title.ilike(search_pattern),
                Service.description.ilike(search_pattern),
                Service.category.ilike(search_pattern)
            )
        ]
        
        if category:
            service_filters.append(Service.category.ilike(f"%{category}%"))
        
        # Tags search temporarily disabled due to type issues
        # if tags:
        #     tag_list = [tag.strip().lower() for tag in tags.split(',') if tag.strip()]
        #     for tag in tag_list:
        #         service_filters.append(sa.func.coalesce(Service.tags, sa.cast('{}', sa.ARRAY(sa.String))).any(tag))
        
        if min_price is not None:
            service_filters.append(Service.price >= min_price)
        
        if max_price is not None:
            service_filters.append(Service.price <= max_price)
        
        # Buscar serviços com filtros
        services = db.query(Service).filter(and_(*service_filters)).limit(limit).all()
        
        # Construir filtros para empresas
        company_filters = [
            or_(
                Company.name.ilike(search_pattern),
                Company.description.ilike(search_pattern),
                Company.province.ilike(search_pattern),
                Company.district.ilike(search_pattern),
                Company.address.ilike(search_pattern)
            )
        ]
        
        if location:
            company_filters.append(
                or_(
                    Company.province.ilike(f"%{location}%"),
                    Company.district.ilike(f"%{location}%")
                )
            )
        
        # Buscar empresas com filtros
        companies = db.query(Company).filter(and_(*company_filters)).limit(limit).all()
        
        # Buscar usuários e portfólios (sem filtros específicos para este exemplo)
        users = db.query(User).filter(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        ).limit(limit).all()
        
        portfolios = db.query(CompanyPortfolio).filter(
            or_(
                CompanyPortfolio.title.ilike(search_pattern),
                CompanyPortfolio.description.ilike(search_pattern)
            )
        ).limit(limit).all()
        
        total_results = len(services) + len(companies) + len(users) + len(portfolios)
        
        results = {
            "services": [
                {
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                    "price": s.price,
                    "category": s.category,
                    "tags": s.tags,
                    "status": s.status,
                    "company_id": s.company_id,
                    "image_url": s.image_url,
                    "views": s.views,
                    "leads": s.leads,
                    "likes": s.likes,
                    "is_promoted": s.is_promoted,
                    "created_at": s.created_at
                } for s in services
            ],
            "companies": [
                {
                    "id": c.id,
                    "name": c.name,
                    "description": c.description,
                    "logo_url": c.logo_url,
                    "cover_url": c.cover_url,
                    "province": c.province,
                    "district": c.district,
                    "address": c.address,
                    "nationality": c.nationality,
                    "website": c.website,
                    "email": c.email,
                    "whatsapp": c.whatsapp
                } for c in companies
            ],
            "users": [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "profile_photo_url": u.profile_photo_url,
                    "cover_photo_url": u.cover_photo_url,
                    "gender": u.gender
                } for u in users
            ],
            "portfolios": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "media_url": p.media_url,
                    "link": p.link,
                    "company_id": p.company_id,
                    "created_at": p.created_at
                } for p in portfolios
            ]
        }
        
        return {
            "query": q,
            "filters": {
                "category": category,
                "location": location,
                "tags": tags,
                "price_range": f"{min_price}-{max_price}" if min_price or max_price else None
            },
            "total_results": total_results,
            "results": results,
            "summary": {
                "services_count": len(services),
                "companies_count": len(companies),
                "users_count": len(users),
                "portfolios_count": len(portfolios)
            }
        }
    except Exception as e:
        return {
            "query": q,
            "filters": {
                "category": category,
                "location": location,
                "tags": tags,
                "price_range": f"{min_price}-{max_price}" if min_price or max_price else None
            },
            "total_results": 0,
            "error": f"Erro na pesquisa avançada: {str(e)}",
            "results": {"services": [], "users": [], "companies": [], "portfolios": []}
        }
