from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status, Depends, Request
from loguru import logger

from src.config.settings import settings
from src.database.mongodb import mongodb
from src.api.schemas.auth import (
    TelegramAuthData,
    TokenResponse,
    UserResponse,
    RefreshTokenRequest,
    LogoutResponse,
)
from src.api.middleware.auth import (
    create_access_token,
    create_refresh_token,
    verify_telegram_hash,
    verify_token,
    get_current_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=TokenResponse)
async def login_with_telegram(auth_data: TelegramAuthData, request: Request):
    auth_dict = auth_data.model_dump()
    auth_date = auth_dict.get("auth_date", 0)
    
    # Masked token for logging
    token = settings.TELEGRAM_BOT_TOKEN
    masked_token = f"{token[:5]}...{token[-5:]}" if len(token) > 10 else "***"
    logger.info(f"Attempting login for user {auth_data.id} with token {masked_token}")
    
    if datetime.utcnow().timestamp() - auth_date > 86400:
        logger.warning(f"Auth data expired for user {auth_data.id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication data expired",
        )
    
    hash_value = auth_dict.pop("hash")
    if not verify_telegram_hash({**auth_dict, "hash": hash_value}, settings.TELEGRAM_BOT_TOKEN):
        logger.error(f"Invalid hash for user {auth_data.id}. Check if TELEGRAM_BOT_TOKEN is correct.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication hash",
        )
    
    now = datetime.utcnow()
    user_data = {
        "telegram_id": auth_data.id,
        "username": auth_data.username,
        "first_name": auth_data.first_name,
        "last_name": auth_data.last_name,
        "photo_url": auth_data.photo_url,
        "auth_date": datetime.fromtimestamp(auth_data.auth_date),
        "is_active": True,
        "last_login": now,
    }
    
    existing_user = await mongodb.users.find_one({"telegram_id": auth_data.id})
    if existing_user:
        await mongodb.users.update_one(
            {"telegram_id": auth_data.id},
            {"$set": user_data}
        )
    else:
        user_data["created_at"] = now
        await mongodb.users.insert_one(user_data)
    
    token_data = {"telegram_id": auth_data.id}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    await mongodb.sessions.update_many(
        {"user_telegram_id": auth_data.id},
        {"$set": {"is_active": False}}
    )
    
    session_data = {
        "user_telegram_id": auth_data.id,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "is_active": True,
        "created_at": now,
        "expires_at": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        "last_activity": now,
        "user_agent": request.headers.get("user-agent"),
        "ip_address": request.client.host if request.client else None,
    }
    await mongodb.sessions.insert_one(session_data)
    
    await mongodb.activity_logs.insert_one({
        "user_telegram_id": auth_data.id,
        "action": "login",
        "details": {"method": "telegram_widget"},
        "created_at": now,
    })
    
    logger.info(f"User {auth_data.id} logged in successfully")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(refresh_request: RefreshTokenRequest):
    payload = verify_token(refresh_request.refresh_token, token_type="refresh")
    telegram_id = payload.get("telegram_id")
    
    session = await mongodb.sessions.find_one({
        "user_telegram_id": telegram_id,
        "refresh_token": refresh_request.refresh_token,
        "is_active": True,
    })
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    token_data = {"telegram_id": telegram_id}
    new_access_token = create_access_token(token_data)
    new_refresh_token = create_refresh_token(token_data)
    
    now = datetime.utcnow()
    await mongodb.sessions.update_one(
        {"_id": session["_id"]},
        {
            "$set": {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expires_at": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
                "last_activity": now,
            }
        }
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    await mongodb.sessions.update_many(
        {"user_telegram_id": current_user["telegram_id"]},
        {"$set": {"is_active": False}}
    )
    
    await mongodb.activity_logs.insert_one({
        "user_telegram_id": current_user["telegram_id"],
        "action": "logout",
        "created_at": datetime.utcnow(),
    })
    
    logger.info(f"User {current_user['telegram_id']} logged out")
    
    return LogoutResponse()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)
