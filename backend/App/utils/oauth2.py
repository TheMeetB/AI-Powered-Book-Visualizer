from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from loguru import logger

from ..utils import JwtToken

# OAuth2 password bearer to authenticate routes
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="login")


class GoogleOAuth2:
    # Dependency to get the current user from JWT token
    @staticmethod
    def get_current_user(token: str = Depends(oauth2_bearer)):
        try:
            return JwtToken.verify_access_token(token)
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}", exc_info=True)
            raise
