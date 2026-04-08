from typing import Dict

from loguru import logger
from pydantic import EmailStr

from ...dao import UserDAO
from ...exceptions import UnauthorizedException, NotFoundException, InternalServerErrorException, \
    ServiceUnavailableException
from ...utils import Hashing, JwtToken


class SigninController:
    @staticmethod
    async def signin(user, request) -> Dict[str, int | str | Dict[str, str] | bool]:
        try:
            username = EmailStr(user["username"])
            existing_user = UserDAO.get_user_by_email(username)
            if not existing_user:
                raise NotFoundException(detail="User does not exist")
            if not Hashing.verify(user["password"], str(existing_user['password'])):
                raise UnauthorizedException(detail="Incorrect password")

            access_token = JwtToken.create_access_token(data={"sub": username})
            request.session['user'] = dict(username=username, access_token=access_token)
            logger.info(f"User logged in: '{username}', token: '{access_token}'")
            return {
                "success": True,
                "status_code": 202,
                "message": "Login successful.",
                "data": {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user_id": str(existing_user["_id"]),
                    "username": existing_user["username"]
                }
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail="Database service unavailable")
        except NotFoundException as e:
            raise e
        except UnauthorizedException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to sign in user '{str(user['username'])}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()
