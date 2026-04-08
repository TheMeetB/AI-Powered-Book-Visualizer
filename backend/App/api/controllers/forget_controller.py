from fastapi import APIRouter, BackgroundTasks
from fastapi.templating import Jinja2Templates
from loguru import logger

from ..services.forget_password_service import ForgetPasswordController
from ...dto import ForgetPasswordRequest, ForgetPasswordOtpRequest, ResetPasswordRequest, StandardResponse
from ...exceptions import BadRequestException, NotFoundException, InternalServerErrorException

templates = Jinja2Templates(directory="backend/App/utils/template/")

router = APIRouter(
    tags=["Forget"]
)


@router.post("/forget-password", response_model=StandardResponse)
async def forget_password(request: ForgetPasswordRequest, background_tasks: BackgroundTasks):
    try:
        if not request.email:
            raise BadRequestException(detail="Email is required")
        logger.info(f"Forget password request for email: '{request.email}'")
        result = await ForgetPasswordController.forget_password_mail(background_tasks, request)
        return StandardResponse(**result)
    except NotFoundException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to send reset email to '{request.email}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to send password reset email")


@router.post("/verify-otp", response_model=StandardResponse)
async def otp_verify(request: ForgetPasswordOtpRequest):
    try:
        if not request.email or not request.otp:
            raise BadRequestException(detail="Email and OTP are required")
        logger.info(f"Verifying OTP for email: '{request.email}'")
        result = await ForgetPasswordController.forget_verify_otp(request)
        return StandardResponse(**result)
    except BadRequestException as e:
        raise e
    except NotFoundException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to verify OTP for '{request.email}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to verify OTP")


@router.post("/reset-password", response_model=StandardResponse)
async def reset_password(request: ResetPasswordRequest):
    try:
        if not request.email or not request.password:
            raise BadRequestException(detail="Email and password are required")
        logger.info(f"Resetting password for email: '{request.email}'")
        result = await ForgetPasswordController.reset_password(request)
        return StandardResponse(**result)
    except BadRequestException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to reset password for '{request.email}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to reset password")
