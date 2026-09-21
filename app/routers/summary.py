from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SummaryResponse
from app.services import summary_service
from app.dependencies import get_current_user
from app import models

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("", response_model=SummaryResponse)
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🔒 JWT protected
):
    return summary_service.get_summary(db)
