from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.core.database import get_db
from app.models.host import Host
from app.schemas.host import HostResponse, HostDetail

router = APIRouter()

@router.get("/", response_model=List[HostResponse])
async def list_hosts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).offset(skip).limit(limit))
    hosts = result.scalars().all()
    return hosts

@router.get("/{host_id}", response_model=HostDetail)
async def get_host(host_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Host).where(Host.id == host_id))
    host = result.scalars().first()
    if not host:
        raise HTTPException(status_code=404, detail="Host not found")
    return host
