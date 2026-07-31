from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ToolItem, H5Page
from app.schemas import ToolResponse
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/tools", tags=["tools"])


def get_h5_from_db(db: Session, slug: str):
    return (
        db.query(H5Page)
        .filter(H5Page.slug == slug)
        .first()
    )



@router.get("", response_model=list[ToolResponse])
def list_tools(db: Session = Depends(get_db)):
    return db.query(ToolItem).all()



@router.get("/h5/{slug}", response_class=HTMLResponse)
def h5_page(
    slug: str,
    db: Session = Depends(get_db)
):
    page = get_h5_from_db(db, slug)

    if not page:
        raise HTTPException(404, "Page not found")

    return HTMLResponse(content=page.content)