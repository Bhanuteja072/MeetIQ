import secrets
import logging
from datetime import datetime, timedelta
from backend.databases.mongo import get_db

logger = logging.getLogger(__name__)

OTP_EXPIRY_MINUTES = 10
MAX_ATTEMPTS = 3
OTP_REQUEST_COOLDOWN_SECONDS = 60


def _generate_otp() -> str:
    """Generate a secure 6-digit OTP."""
    return str(secrets.randbelow(900000) + 100000)  # always 6 digits

def _normalize_email(email: str) -> str:
    """Normalize email."""
    return email.strip().lower()

async def create_otp(email: str) -> str:
    """
    Generate OTP, save to DB, return the OTP string.
    Deletes any existing OTPs for this email first.
    """
    db = get_db()
    email = _normalize_email(email)

    otp = _generate_otp()

    # Remove any existing OTPs for this email
    await db.otp_store.delete_many({"email": email})

    await db.otp_store.insert_one({
        "email": email,
        "otp": otp,
        "attempts": 0,
        "used": False,
        "expires_at": datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES),
        "created_at": datetime.utcnow(),
    })

    logger.info("OTP created for %s", email)
    return otp


async def verify_otp(email: str, otp: str) -> dict:
    """
    Verify OTP for given email.

    Returns:
        { "valid": True }  on success
        { "valid": False, "reason": "..." }  on failure
    """
    db = get_db()

    record = await db.otp_store.find_one({
        "email": email,
        "used": False,
    })

    if not record:
        return {"valid": False, "reason": "No OTP found. Please request a new one."}

    # Check expiry
    if datetime.utcnow() > record["expires_at"]:
        await db.otp_store.delete_one({"_id": record["_id"]})
        return {"valid": False, "reason": "OTP expired. Please request a new one."}

    # Check attempts
    if record["attempts"] >= MAX_ATTEMPTS:
        await db.otp_store.delete_one({"_id": record["_id"]})
        return {"valid": False, "reason": "Too many attempts. Please request a new OTP."}

    # Wrong OTP — increment attempts
    if record["otp"] != otp:
        await db.otp_store.update_one(
            {"_id": record["_id"]},
            {"$inc": {"attempts": 1}}
        )
        remaining = MAX_ATTEMPTS - record["attempts"] - 1
        return {"valid": False, "reason": f"Incorrect OTP. {remaining} attempt(s) remaining."}

    # Mark as used
    await db.otp_store.update_one(
        {"_id": record["_id"]},
        {"$set": {"used": True}}
    )

    return {"valid": True}


async def cleanup_otp(email: str):
    """Delete all OTPs for email after successful password reset."""
    db = get_db()
    email = _normalize_email(email)
    deleted = await db.otp_store.delete_many({"email": email})

    logger.info(
        "Cleaned up %s OTP record(s) for %s",
        deleted.deleted_count,
        email
    )