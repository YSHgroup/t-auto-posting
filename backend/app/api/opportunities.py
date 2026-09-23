"""
Opportunities API routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Opportunity
from app.schemas import OpportunityResponse
from typing import List, Optional
from app.api.auth import get_current_user
from app.models import User

router = APIRouter()

@router.get("", response_model=List[OpportunityResponse])
async def get_opportunities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    opportunity_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """Get identified opportunities"""
    query = db.query(Opportunity).filter(
        Opportunity.user_id == current_user.id
    )
    
    if opportunity_type:
        query = query.filter(Opportunity.opportunity_type == opportunity_type)
    
    if status_filter:
        query = query.filter(Opportunity.status == status_filter)
    
    opportunities = query.order_by(
        Opportunity.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return opportunities

@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get opportunity details"""
    opportunity = db.query(Opportunity).filter(
        (Opportunity.id == opportunity_id) &
        (Opportunity.user_id == current_user.id)
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return opportunity

@router.post("/analyze")
async def analyze_group_for_opportunities(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger opportunity analysis for a group.
    Retrieves up to 500 recent messages and analyzes for investors/partners.
    Runs asynchronously via Celery worker.
    """
    # TODO: Queue opportunity analysis task
    return {"status": "analysis_queued", "group_id": group_id}

@router.put("/{opportunity_id}/status")
async def update_opportunity_status(
    opportunity_id: int,
    status: str = Query(..., regex="^(new|reviewed|contacted|dismissed)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update opportunity status"""
    opportunity = db.query(Opportunity).filter(
        (Opportunity.id == opportunity_id) &
        (Opportunity.user_id == current_user.id)
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    opportunity.status = status
    db.commit()
    
    return {"status": "updated"}
