from typing import Dict

from loguru import logger
from pydantic import EmailStr

from ...dao import UserDAO
from ...exceptions import BadRequestException, InternalServerErrorException, NotFoundException, \
    ServiceUnavailableException
from ...utils import Hashing, JwtToken


class UserController:
    @staticmethod
    async def refresh_token(token_request: str) -> Dict[str, int | str | Dict[str, str] | bool]:
        try:
            updated_token = JwtToken.refresh_access_token(token_request)
            logger.info(f"Token refreshed successfully: '{updated_token['access_token']}'")
            return {
                "success": True,
                "status_code": 202,
                "message": "Token successfully refreshed",
                "data": updated_token
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail="Database service unavailable")
        except Exception as e:
            logger.error(f"Failed to refresh token: {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def delete_user(user) -> Dict[str, int | str | None | bool]:
        try:
            email = EmailStr(user.email)
            existing_user = UserDAO.get_user_by_email(email)
            if not existing_user:
                raise NotFoundException(detail="User does not exist")
            if not Hashing.verify(user.password, str(existing_user['password'])):
                raise BadRequestException(detail="Incorrect password")
            UserDAO.soft_delete_user(existing_user['_id'], email)
            logger.info(f"User soft-deleted: '{email}'")
            return {
                "success": True,
                "status_code": 200,
                "message": "User deleted successfully",
                "data": None
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail="Database service unavailable")
        except NotFoundException as e:
            raise e
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to delete user '{str(user.email)}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()
