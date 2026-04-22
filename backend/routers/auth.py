# backend/routers/auth.py
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from backend.databases.mongo import get_db
from backend.models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from backend.services.auth_service import hash_password, verify_password, create_access_token
from backend.dependencies.auth import get_current_user as get_current_user_dep

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: UserCreate):
    """
    Register a new user.
    1. Check email not already taken
    2. Hash password
    3. Save to users collection
    4. Return JWT token immediately (no need to login again)
    """
    db = get_db()

    # Check duplicate email
    existing = await db.users.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    user_id = str(uuid.uuid4())
    now = datetime.utcnow()

    user_doc = {
        "_id": user_id,
        "email": body.email.lower(),
        "hashed_password": hash_password(body.password),
        "full_name": body.full_name or "",
        "created_at": now,
    }

    await db.users.insert_one(user_doc)

    token = create_access_token(user_id, body.email.lower())

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user_id,
            email=body.email.lower(),
            full_name=body.full_name,
            created_at=now
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    """
    Login with email + password.
    1. Find user by email
    2. Verify password against bcrypt hash
    3. Return fresh JWT token
    """
    db = get_db()

    user = await db.users.find_one({"email": body.email.lower()})

    # Same error for wrong email OR wrong password (security: don't reveal which)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(user["_id"], user["email"])

    return TokenResponse(
        access_token=token,
        user=UserResponse(
            id=user["_id"],
            email=user["email"],
            full_name=user.get("full_name"),
            created_at=user["created_at"]
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user_dep)):
    """Return the currently logged-in user's profile."""
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        created_at=current_user["created_at"]
    )