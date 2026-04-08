from passlib.context import CryptContext
from loguru import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hashing(object):
    @staticmethod
    def encrypt(password: str) -> str:
        try:
            logger.info("Hashed Password Created Successfully")
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error encrypting password: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def verify(plain: str, hashed: str):
        try:
            logger.info("Hashed Password Verified Successfully")
            return pwd_context.verify(plain, hashed)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}", exc_info=True)
            raise