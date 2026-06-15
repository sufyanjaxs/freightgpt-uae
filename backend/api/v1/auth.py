from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import (
    hash_password, verify_password, create_access_token, create_refresh_token,
    decode_token, get_current_user, oauth2_scheme,
)
from db.models.user import User, Tenant, UserRole
from schemas.user import UserCreate, UserLogin, TokenResponse, UserResponse, TenantCreate

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    tenant = await db.execute(select(Tenant).limit(1))
    tenant = tenant.scalar_one_or_none()
    if not tenant:
        tenant = Tenant(name="Default", slug="default")
        db.add(tenant)
        await db.flush()

    user = User(
        tenant_id=tenant.id,
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=UserRole.TENANT_ADMIN,
    )
    db.add(user)
    await db.flush()

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user),
    }


@router.post("/refresh")
async def refresh(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=400, detail="Invalid refresh token")

    access_token = create_access_token({"sub": payload["sub"]})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
