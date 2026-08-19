from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import get_auth_service
from ..schemas.auth import (
    EmailVerificationRequest,
    EmailVerificationResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    MagicLinkRequest,
    MagicLinkResponse,
    MagicLinkVerifyRequest,
    OTPRequest,
    OTPResponse,
    OTPVerifyRequest,
    PasswordChangeRequest,
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    ResendVerificationRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)

async def login(
    request: LoginRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    try:
        return await auth_service.login(
            email=request.email,
            password=request.password,
            otp=request.otp,
            pin=request.pin,
            device_id=request.device_id,
            remember_device=request.remember_device,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc),) from exc

@router.post(
    "/refresh",
    response_model=TokenRefreshResponse,
)

async def refresh_token(
    request: TokenRefreshRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    result = await auth_service.refresh(request.refresh_token)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token.",)

    return result


@router.post(
    "/logout",
    response_model=LogoutResponse,
)

async def logout(
    request: LogoutRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    success = await auth_service.logout(
        refresh_token=request.refresh_token,
        session_id=request.session_id,
        all_sessions=request.all_sessions,
    )

    return LogoutResponse(
        success=success,
        message="Logout completed." if success else "No active session found.",
    )


@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
)

async def verify_email(
    request: EmailVerificationRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    try:
        result = await auth_service.verify_email(request.token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc),) from exc

    return {
        "success": True,
        "user_id": result["user_id"],
        "email": result["email"],
        "message": "Email verified successfully.",
    }

@router.post(
    "/verify-email/resend",
    response_model=dict,
)

async def resend_verification(
    request: ResendVerificationRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    await auth_service.resend_verification(request.email)

    return {
        "success": True,
        "message": "Verification email sent.",
    }

@router.post(
    "/otp/request",
    response_model=OTPResponse,
)

async def request_otp(
    request: OTPRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    result = await auth_service.request_otp(
        destination=request.destination,
        purpose=request.purpose,
        channel=request.channel,
    )

    return result


@router.post(
    "/otp/verify",
    response_model=OTPResponse,
)

async def verify_otp(
    request: OTPVerifyRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    result = await auth_service.verify_otp(
        user_id=request.user_id,
        code=request.code,
        purpose=request.purpose,
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP.",)

    return {
        "success": True,
        "message": "OTP verified successfully.",
    }

@router.post(
    "/magic-link/request",
    response_model=MagicLinkResponse,
)

async def request_magic_link(
    request: MagicLinkRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    await auth_service.request_magic_link(
        email=request.email,
        purpose=request.purpose,
    )

    return {
        "success": True,
        "message": "Magic link sent.",
    }

@router.post(
    "/magic-link/verify",
    response_model=MagicLinkResponse,
)

async def verify_magic_link(
    request: MagicLinkVerifyRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    result = await auth_service.verify_magic_link(
        token=request.token,
        purpose=request.purpose,
    )

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired magic link.")

    return {
        "success": True,
        "message": "Magic link verified successfully.",
    }

@router.post(
    "/password/change",
    response_model=dict,
)

async def change_password(
    request: PasswordChangeRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    await auth_service.change_password(
        current_password=request.current_password,
        new_password=request.new_password,
    )

    return {
        "success": True,
        "message": "Password changed successfully.",
    }

@router.post(
    "/password/reset",
    response_model=dict,
)

async def request_password_reset(
    request: PasswordResetRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    await auth_service.request_password_reset(request.email)

    return {
        "success": True,
        "message": "If the account exists, a reset email has been sent.",
    }

@router.post(
    "/password/reset/confirm",
    response_model=dict,
)

async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    auth_service: Annotated[object, Depends(get_auth_service)],
):
    await auth_service.confirm_password_reset(
        token=request.token,
        new_password=request.new_password
    )

    return {
        "success": True,
        "message": "Password reset successfully.",
    }