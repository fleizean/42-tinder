# app/api/users.py
from typing import Any
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse

from app.core.db import get_connection
from app.core.security import get_current_user, get_current_verified_user
from app.validation.user import validate_user_update
from app.db import users

router = APIRouter()

@router.get("/me", response_model=dict)
async def read_user_me(
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get current user
    """
    return current_user

@router.put("/me", response_model=dict)
async def update_user_me(
    request: Request,
    current_user = Depends(get_current_verified_user),
    conn = Depends(get_connection)
) -> Any:
    """
    Update current user
    """
    data = await request.json()
    
    # Validate user data
    is_valid, errors = validate_user_update(data)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": errors}
        )
    
    # Check if username is being changed and if it's already taken
    if data.get("username") and data["username"] != current_user["username"]:
        existing_user = await users.get_user_by_username(conn, data["username"])
        if existing_user:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Username already taken"}
            )
    
    # Check if email is being changed and if it's already taken
    if data.get("email") and data["email"] != current_user["email"]:
        existing_email = await users.get_user_by_email(conn, data["email"])
        if existing_email:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Email already registered"}
            )
    
    # Update user
    updated_user = await users.update_user(conn, current_user["id"], data)
    
    if not updated_user:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Failed to update user"}
        )
    
    return dict(updated_user)

@router.post("/heartbeat", response_model=dict)
async def user_heartbeat(
    current_user = Depends(get_current_user),
    conn = Depends(get_connection)
) -> Any:
    """
    Update user's last activity timestamp (for online status)
    """
    await users.update_last_activity(conn, current_user["id"], True)
    
    return {
        "status": "ok"
    }