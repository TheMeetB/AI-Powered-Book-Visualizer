from fastapi import APIRouter
from loguru import logger

from ..services import UserController
from ...dto import StandardResponse, RefreshTokenData, UserDeleteRequest
from ...exceptions import BadRequestException, NotFoundException, InternalServerErrorException

router = APIRouter(
    tags=["User"]
)


@router.post("/refresh_token", response_model=StandardResponse)
async def refresh_token(token_request: RefreshTokenData):
    try:
        if not token_request.token:
            raise BadRequestException(detail="Token is required")
        logger.info("Refreshing token")
        result = await UserController.refresh_token(token_request.token)
        return StandardResponse(**result)
    except BadRequestException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to refresh token: {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to refresh token")


@router.delete("/user_delete", response_model=StandardResponse)
async def user_delete(user: UserDeleteRequest):
    try:
        if not user.email or not user.password:
            raise BadRequestException(detail="Email and password are required")
        logger.info(f"Deleting user with email: '{user.email}'")
        result = await UserController.delete_user(user)
        return StandardResponse(**result)
    except NotFoundException as e:
        raise e
    except BadRequestException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to delete user with email '{user.email}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to delete user")
