from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SummaryResponse
from app.services import summary_service
from app.dependencies import get_current_user
from app.common.response import build_response
from app import models

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("", status_code=status.HTTP_200_OK)
def get_summary(
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),  # 🔒 JWT protected
):
    summary_data = summary_service.get_summary(db)
    data = SummaryResponse.model_validate(summary_data).model_dump(mode="json")
    return build_response(
        status_code=status.HTTP_200_OK,
        status_desc="Spend summary calculated successfully",
        data=data,
        path=str(request.url.path),
        method=request.method,
    )
