from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from ..services import SigninController
from ...dto import StandardResponse
from ...exceptions import BadRequestException, InternalServerErrorException, UnauthorizedException

router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)


@router.post("", response_model=StandardResponse)
async def signin(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        if not form_data.username or not form_data.password:
            raise BadRequestException(detail="Username and password are required")
        logger.info(f"Login attempt for username: '{form_data.username}'")
        user_data = {"username": form_data.username, "password": form_data.password}
        result = await SigninController.signin(user_data, request)
        return StandardResponse(**result)
    except UnauthorizedException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to sign in user '{form_data.username}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to sign in")
