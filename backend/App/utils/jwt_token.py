import os
from datetime import timedelta, timezone, datetime

from jose import jwt, JWTError, ExpiredSignatureError
from jwt import DecodeError, InvalidTokenError
from loguru import logger
from pydantic import EmailStr

from ..dto import TokenData
from ..exceptions import UnauthorizedException, BadRequestException, InternalServerErrorException

SECRET_KEY = os.getenv("JWT_TOKEN_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # Default expiration is 24 hours


class JwtToken:
    @staticmethod
    def create_access_token(data: dict, expire_time=ACCESS_TOKEN_EXPIRE_MINUTES):
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=expire_time)
            to_encode.update({"exp": expire})
            logger.info("Access Token Created Successfully")
            return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        except Exception as e:
            logger.error(f"Error creating token: {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    def verify_access_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: EmailStr = payload.get("sub")
            if email is None:
                raise UnauthorizedException(detail="Invalid token: no email found")
            logger.info("Access Token Verified Successfully")
            return TokenData(email=email)
        except ExpiredSignatureError:
            raise UnauthorizedException(detail="Token has expired")
        except (DecodeError, InvalidTokenError, JWTError) as e:
            raise UnauthorizedException(detail=f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}", exc_info=True)
            raise BadRequestException(detail=f"Token verification failed: {str(e)}")

    @staticmethod
    def refresh_access_token(token_request: str):
        try:
            old_token = jwt.decode(token_request, SECRET_KEY, algorithms=[ALGORITHM])
            email = old_token.get("sub")
            if not email:
                raise UnauthorizedException(detail="Could not validate credentials")
            return {"access_token": JwtToken.create_access_token(data={"sub": email})}
        except ExpiredSignatureError:
            raise UnauthorizedException(detail="Token has expired")
        except (DecodeError, InvalidTokenError, JWTError) as e:
            raise UnauthorizedException(detail=f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}", exc_info=True)
            raise InternalServerErrorException()
