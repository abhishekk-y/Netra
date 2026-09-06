"""Netra — Auth API."""
from __future__ import annotations
from fastapi import APIRouter, Body, Depends, HTTPException, status
from typing import Any
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(data: dict = Body(...)) -> dict[str, Any]:
    username = data.get("username", "")
    password = data.get("password", "")
    if username == "admin" and password == "admin":
        return {"access_token": "demo-token", "token_type": "bearer", "role": "administrator", "username": "admin"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

@router.get("/me")
async def get_me() -> dict[str, Any]:
    return {"username": "admin", "role": "administrator", "email": "admin@netra.local"}
