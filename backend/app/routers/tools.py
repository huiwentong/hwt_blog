from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import ToolItem, H5Page
from app.schemas import (
    ToolResponse,
    ToolCreate,
    ToolUpdate,
    H5PageCreate,
    H5PageResponse,
)
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
    return db.query(ToolItem).order_by(ToolItem.id.desc()).all()


@router.post("", response_model=ToolResponse, status_code=201)
def create_tool(payload: ToolCreate, db: Session = Depends(get_db)):
    tool = ToolItem(
        name=payload.name,
        description=payload.description,
        url=payload.url,
        icon=payload.icon,
        category=payload.category,
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    return tool


@router.patch("/{tool_id}", response_model=ToolResponse)
def update_tool(tool_id: int, payload: ToolUpdate, db: Session = Depends(get_db)):
    tool = db.query(ToolItem).filter(ToolItem.id == tool_id).first()
    if not tool:
        raise HTTPException(404, "Tool not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tool, field, value)
    db.commit()
    db.refresh(tool)
    return tool


@router.delete("/{tool_id}")
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    tool = db.query(ToolItem).filter(ToolItem.id == tool_id).first()
    if not tool:
        raise HTTPException(404, "Tool not found")
    db.delete(tool)
    db.commit()
    return {"ok": True}


# ---- H5 pages (managed from the desktop manager) ----

@router.post("/h5", response_model=H5PageResponse, status_code=201)
def create_h5_page(payload: H5PageCreate, db: Session = Depends(get_db)):
    exists = db.query(H5Page).filter(H5Page.slug == payload.slug).first()
    if exists:
        raise HTTPException(409, "Slug already exists")
    page = H5Page(slug=payload.slug, content=payload.content)
    db.add(page)
    db.commit()
    db.refresh(page)
    return page


@router.get("/h5", response_model=list[H5PageResponse])
def list_h5_pages(db: Session = Depends(get_db)):
    return db.query(H5Page).order_by(H5Page.id.desc()).all()


@router.delete("/h5/{h5_id}")
def delete_h5_page(h5_id: int, db: Session = Depends(get_db)):
    page = db.query(H5Page).filter(H5Page.id == h5_id).first()
    if not page:
        raise HTTPException(404, "H5 page not found")
    db.delete(page)
    db.commit()
    return {"ok": True}



@router.get("/h5/{slug}", response_class=HTMLResponse)
def h5_page(
    slug: str,
    db: Session = Depends(get_db)
):
    page = get_h5_from_db(db, slug)

    if not page:
        raise HTTPException(404, "Page not found")

    return HTMLResponse(content=page.content)