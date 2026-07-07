from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ToolItem
from app.schemas import ToolResponse

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("", response_model=list[ToolResponse])
def list_tools(db: Session = Depends(get_db)):
    return db.query(ToolItem).all()
