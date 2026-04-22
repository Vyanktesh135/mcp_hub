"""Registry routes — browse published API definitions."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.api_definition import ApiDefinition
from schemas.agent import ApiDefinitionResponse
from utils.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/api/registry", tags=["registry"])


@router.get("/", response_model=list[ApiDefinitionResponse])
def list_apis(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(ApiDefinition)
        .filter(ApiDefinition.user_id == current_user.id)
        .order_by(ApiDefinition.created_at.desc())
        .limit(limit)
        .all()
    )


@router.get("/{api_id}", response_model=ApiDefinitionResponse)
def get_api(
    api_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api = db.query(ApiDefinition).filter(
        ApiDefinition.id == api_id, ApiDefinition.user_id == current_user.id
    ).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")
    return api


@router.delete("/{api_id}", status_code=204)
def delete_api(
    api_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    api = db.query(ApiDefinition).filter(
        ApiDefinition.id == api_id, ApiDefinition.user_id == current_user.id
    ).first()
    if not api:
        raise HTTPException(status_code=404, detail="API not found")
    db.delete(api)
    db.commit()
