from typing import Dict

from loguru import logger

from ...dao import UserDAO
from ...exceptions import BadRequestException, InternalServerErrorException, ServiceUnavailableException
from ...utils import Hashing


class SignupController:
    @staticmethod
    async def signup(user) -> Dict[str, int | str | Dict[str, str] | bool]:
        try:
            existing_user = UserDAO.get_user_by_email(user.email)
            if existing_user:
                logger.warning(f"Signup attempt with existing email: {user.email}")
                raise BadRequestException(detail="Email already registered")

            user_data = user.dict(by_alias=True)
            user_data["password"] = Hashing.encrypt(user.password)
            user_id = UserDAO.create_user(user_data)
            logger.info(f"User registered with ID: '{user_id}', email: '{user.email}'")
            return {
                "success": True,
                "status_code": 201,
                "message": "User registered successfully",
                "data": {"user_id": user_id}
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail="Database service unavailable")
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to signup user with email '{user.email}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()
