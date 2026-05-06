import logging
import resend, html
from config import settings

logger = logging.getLogger(__name__)



def send_otp_email(to_email: str, otp: str, full_name: str = "") -> bool:
    """
    Send password reset OTP email.

    Args:
        to_email (str): Recipient email address
        otp (str): One-time password
        full_name (str): User full name

    Returns:
        bool: True if email sent successfully, else False
    """

    if not settings.resend_api_key:
        logger.error("RESEND_API_KEY is missing")
        return False

    if not settings.from_email:
        logger.error("FROM_EMAIL is missing")
        return False

    if not to_email or "@" not in to_email:
        logger.error("Invalid recipient email: %s", to_email)
        return False

    resend.api_key = settings.resend_api_key

    safe_name = html.escape(full_name.strip()) if full_name else "there"
    safe_otp = html.escape(str(otp))


    html_content = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#0f172a;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      <div style="max-width:480px;margin:40px auto;background:#1e293b;border-radius:12px;border:1px solid #334155;overflow:hidden;">
        
        <div style="background:#6366f1;padding:28px 32px;">
          <h1 style="color:#fff;margin:0;font-size:22px;font-weight:700;">MeetIQ</h1>
          <p style="color:#c7d2fe;margin:6px 0 0;font-size:14px;">Password Reset Request</p>
        </div>

        <div style="padding:32px;">
          <p style="color:#cbd5e1;font-size:15px;margin:0 0 8px;">Hi {safe_name},</p>
          <p style="color:#94a3b8;font-size:14px;margin:0 0 28px;line-height:1.6;">
            We received a request to reset your MeetIQ password. 
            Use the OTP below — it expires in <strong style="color:#f1f5f9;">10 minutes</strong>.
          </p>

          <div style="background:#0f172a;border-radius:10px;border:1px solid #334155;padding:24px;text-align:center;margin-bottom:28px;">
            <p style="color:#64748b;font-size:12px;text-transform:uppercase;letter-spacing:2px;margin:0 0 12px;">Your OTP</p>
            <p style="color:#a78bfa;font-size:36px;font-weight:700;letter-spacing:10px;margin:0;font-variant-numeric:tabular-nums;">
              {safe_otp}
            </p>
          </div>

          <p style="color:#475569;font-size:13px;margin:0;line-height:1.6;">
            If you didn't request this, you can safely ignore this email. 
            Your password won't change.
          </p>
        </div>

        <div style="padding:20px 32px;border-top:1px solid #334155;">
          <p style="color:#334155;font-size:12px;margin:0;">
            This OTP will expire in 10 minutes and can only be used once.
          </p>
        </div>

      </div>
    </body>
    </html>
    """

    plain_text = f"""
        Hi {safe_name},

        We received a request to reset your MeetIQ password.

        Your OTP is: {safe_otp}

        This OTP expires in 10 minutes.

        If you did not request this, you can safely ignore this email.
        """

    try:
        resend.Emails.send({
            "from": settings.from_email,
            "to": to_email,
            "subject": "Your MeetIQ Password Reset OTP",
            "html": html_content,
            "text": plain_text,
        })
        logger.info("OTP email sent to %s", to_email)
        return True

    except Exception as e:
        logger.error("Failed to send OTP email to %s: %s", to_email, e)
        return False