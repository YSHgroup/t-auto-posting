"""
Telegram authentication endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, TelegramAccount
from app.telegram.client import get_telegram_service
from pyrogram.errors import SessionPasswordNeeded, RpcError
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/telegram", tags=["telegram"])

# Request/Response schemas
class PhoneLoginRequest(BaseModel):
    phone: str

class CodeVerificationRequest(BaseModel):
    phone: str
    code: str

class TwoFARequest(BaseModel):
    password: str

class TelegramStatusResponse(BaseModel):
    connected: bool
    phone: Optional[str] = None
    first_name: Optional[str] = None

@router.post("/login/request-code")
async def request_telegram_code(
    request: PhoneLoginRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 1: Request Telegram login code
    
    The code will be sent to the user's Telegram app.
    Store the phone temporarily in session or return it for next step.
    """
    try:
        phone = request.phone.strip()
        if not phone.startswith("+"):
            phone = "+" + phone
        
        # Initialize Telegram service
        telegram_service = get_telegram_service()
        
        # Request login code
        await telegram_service.login_with_phone(phone)
        
        logger.info(f"User {current_user.id} requested Telegram login for {phone}")
        
        return {
            "status": "code_sent",
            "message": "Check your Telegram app for the verification code",
            "phone": phone
        }
    
    except RpcError as e:
        logger.error(f"Telegram RPC error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telegram error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Telegram login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request Telegram code"
        )


@router.post("/login/verify-code")
async def verify_telegram_code(
    request: CodeVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 2: Verify Telegram login code
    
    If 2FA is enabled, will raise SessionPasswordNeeded
    """
    try:
        telegram_service = get_telegram_service()
        
        # Verify code
        session_string = await telegram_service.verify_code(
            request.phone,
            request.code
        )
        
        # Store session in database (encrypted)
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == current_user.id
        ).first()
        
        if not telegram_account:
            telegram_account = TelegramAccount(
                user_id=current_user.id,
                phone_number=request.phone,
                session_string=session_string
            )
            db.add(telegram_account)
        else:
            telegram_account.session_string = session_string
            telegram_account.phone_number = request.phone
        
        db.commit()
        
        logger.info(f"User {current_user.id} verified Telegram code")
        
        return {
            "status": "authenticated",
            "message": "Successfully logged in to Telegram",
            "phone": request.phone
        }
    
    except SessionPasswordNeeded:
        logger.info(f"2FA password required for {request.phone}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="2FA password required. Please provide your account password."
        )
    
    except RpcError as e:
        logger.error(f"Telegram RPC error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telegram error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Code verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify Telegram code"
        )


@router.post("/login/verify-2fa")
async def verify_2fa(
    request: TwoFARequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Step 3: Verify 2FA password
    
    Only required if account has 2FA enabled
    """
    try:
        telegram_service = get_telegram_service()
        
        # Verify 2FA password
        session_string = await telegram_service.verify_2fa(request.password)
        
        # Store session in database (encrypted)
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == current_user.id
        ).first()
        
        if not telegram_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No pending Telegram login session"
            )
        
        telegram_account.session_string = session_string
        db.commit()
        
        logger.info(f"User {current_user.id} verified 2FA password")
        
        return {
            "status": "authenticated",
            "message": "Successfully logged in to Telegram"
        }
    
    except RpcError as e:
        logger.error(f"Telegram RPC error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password. Please try again."
        )
    except Exception as e:
        logger.error(f"2FA verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify 2FA password"
        )


@router.get("/status")
async def get_telegram_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get Telegram connection status"""
    try:
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == current_user.id
        ).first()
        
        if not telegram_account or not telegram_account.session_string:
            return TelegramStatusResponse(connected=False)
        
        return TelegramStatusResponse(
            connected=True,
            phone=telegram_account.phone_number,
            first_name=telegram_account.first_name
        )
    except Exception as e:
        logger.error(f"Error getting Telegram status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Telegram status"
        )


@router.post("/logout")
async def logout_telegram(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Telegram account"""
    try:
        telegram_account = db.query(TelegramAccount).filter(
            TelegramAccount.user_id == current_user.id
        ).first()
        
        if telegram_account:
            db.delete(telegram_account)
            db.commit()
        
        logger.info(f"User {current_user.id} logged out of Telegram")
        
        return {"status": "logged_out", "message": "Disconnected from Telegram"}
    except Exception as e:
        logger.error(f"Error logging out of Telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout of Telegram"
        )
