from fastapi import APIRouter
from loguru import logger

from ..services import SignupController
from ...dto import StandardResponse, UserRegisterRequest
from ...exceptions import BadRequestException, InternalServerErrorException

router = APIRouter(
    prefix="/register",
    tags=["Register"],
)


@router.post("", response_model=StandardResponse)
async def signup(user: UserRegisterRequest):
    try:
        if not user.email or not user.username or not user.password:
            raise BadRequestException(detail="Username, email, and password are required")
        logger.info(f"Registering user with email: '{user.email}'")
        result = await SignupController.signup(user)
        return StandardResponse(**result)
    except BadRequestException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to register user with email '{user.email}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to register user")
