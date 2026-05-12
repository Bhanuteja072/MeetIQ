# backend/routers/auth.py
import uuid, secrets, re, logging
from fastapi import APIRouter, HTTPException, status, Depends, Request, BackgroundTasks
from config import settings
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from backend.databases.mongo import get_db
from backend.models.user import UserCreate, UserLogin, TokenResponse, UserResponse
from backend.services.auth_service import hash_password, verify_password, create_access_token
from backend.dependencies.auth import get_current_user as get_current_user_dep
from backend.services.otp_service import create_otp, verify_otp, cleanup_otp
from backend.services.email_service import send_otp_email


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RESET_TOKEN_SECRET = settings.jwt_secret + "_reset"  # separate secret
RESET_TOKEN_EXPIRE_MINUTES = 15
def validate_password_strength(password: str) -> bool:
    """
    Validate password strength.
    Requires:
    - 8+ chars
    - uppercase
    - lowercase
    - digit
    """
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    return (
        len(password) >= 8
        and has_upper
        and has_lower
        and has_digit
    )


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

async def _send_otp_task(email: str, otp: str, full_name: str):
    try:
        success = send_otp_email(to_email=email, otp=otp, full_name=full_name)
        if not success:
            logger.error("EMAIL FAILED for %s — send_otp_email returned False", email)
        else:
            logger.info("EMAIL SUCCESS for %s", email)
    except Exception as e:
        logger.exception("EMAIL CRASHED for %s: %s", email, e)

@router.post("/forgot-password")
async def forgot_password(request: Request, background_tasks: BackgroundTasks):
    """
    Step 1 — Send OTP to email.
    Always returns success to prevent email enumeration.
    """
    try:

        body = await request.json()
        email = (body.get("email") or "").strip().lower()

        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        db = get_db()
        user = await db.users.find_one({"email": email})

        # Always send the same response — don't reveal if email exists
        if user:
            otp = await create_otp(email)
            background_tasks.add_task(
                _send_otp_task,
                email,
                otp,
                user.get("full_name", "")
            )
            logger.info(
                "Password reset OTP generated for %s",
                email
            )

        return {"message": "If that email is registered, an OTP has been sent."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Error in forgot_password: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")

@router.post("/verify-otp")
async def verify_otp_endpoint(request: Request):
    """
    Step 2 — Verify OTP and return a short-lived reset token.
    """
    try:
        body = await request.json()
        email = (body.get("email") or "").strip().lower()
        otp = (body.get("otp") or "").strip()

        if not email or not otp:
            raise HTTPException(status_code=400, detail="Email and OTP are required")

        result = await verify_otp(email, otp)

        if not result["valid"]:
            raise HTTPException(status_code=400, detail=result["reason"])

        # Issue a short-lived reset token
        reset_token = jwt.encode(
            {
                "sub": email,
                "type": "password_reset",      # important — blocks reuse as auth token
                "exp": datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES),
            },
            RESET_TOKEN_SECRET,
            algorithm=settings.jwt_algorithm,
        )
        logger.info("OTP verified for %s", email)

        return {"reset_token": reset_token}
    except HTTPException:
        raise  # re-raise known HTTP exceptions without logging as errors
    except Exception as e:
        logger.exception("Error in verify_otp_endpoint: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


@router.post("/reset-password")
async def reset_password(request: Request):
    """
    Step 3 — Verify reset token and update password.
    """
    try:
        
        body = await request.json()
        reset_token = (body.get("reset_token") or "").strip()
        new_password = (body.get("new_password") or "").strip()

        if not reset_token or not new_password:
            raise HTTPException(status_code=400, detail="Token and new password are required")
        if not validate_password_strength(new_password):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Password must contain at least "
                    "8 characters, one uppercase letter, "
                    "one lowercase letter, and one number."
                )
            )
        # Verify reset token
        try:
            payload = jwt.decode(reset_token, RESET_TOKEN_SECRET, algorithms=[settings.jwt_algorithm])
            if payload.get("type") != "password_reset":
                raise HTTPException(status_code=400, detail="Invalid reset token")
            email = payload.get("sub")
            if not email:
                raise HTTPException(status_code=400, detail="Invalid reset token")
        except JWTError:
            raise HTTPException(status_code=400, detail="Reset token is invalid or expired")

        # Update password
        db = get_db()
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Prevent reusing same password
        existing_hash = user.get("hashed_password", "")
        if pwd_context.verify(new_password, existing_hash):
            raise HTTPException(
                status_code=400,
                detail=(
                    "New password cannot be same "
                    "as current password"
                )
            )

        hashed = pwd_context.hash(new_password)
        await db.users.update_one(
            {"email": email},
            {"$set": {"hashed_password": hashed, "updated_at": datetime.utcnow()}}
        )

        # Clean up OTPs
        await cleanup_otp(email)
        logger.info("Password reset successful for %s", email)

        return {"message": "Password reset successfully"}
    except HTTPException:
        raise  # re-raise known HTTP exceptions without logging as errors
    except Exception as e:
        logger.exception("Error in reset_password: %s", e)
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")
    
@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user_dep)):
    """Return the currently logged-in user's profile."""
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        created_at=current_user["created_at"]
    )