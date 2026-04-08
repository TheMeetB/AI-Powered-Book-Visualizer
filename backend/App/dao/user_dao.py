from datetime import datetime
from typing import Mapping, Any

from bson import ObjectId
from loguru import logger
from pydantic import EmailStr
from pymongo.collection import Collection

from ..config import database
from ..exceptions import InternalServerErrorException, BadRequestException, NotFoundException
from ..vo import MongoUserData


class UserDAO:
    collection: Collection = database['users']

    @staticmethod
    def get_user_by_email(email: EmailStr) -> Mapping[str, Any] | None:
        """Fetch a user by email."""
        if not email:
            raise BadRequestException(detail="Email is required")
        try:
            user = UserDAO.collection.find_one({"email": email, "is_deleted": False})
            return user
        except Exception as e:
            logger.error(f"Error fetching user by email {email}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch user")

    @staticmethod
    def create_user(user_data: dict) -> str:
        """Create a new user."""
        if not user_data or "email" not in user_data:
            raise BadRequestException(detail="User data with email is required")
        try:
            user_data["created_at"] = datetime.now()
            user_data["updated_on"] = datetime.now()
            user_data["is_deleted"] = False
            mongo_data = MongoUserData(**user_data).dict()
            result = UserDAO.collection.insert_one(mongo_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating user with email {user_data['email']}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to create user")

    @staticmethod
    def update_user(email: EmailStr, updates: dict) -> bool:
        """Update user details."""
        if not email or not updates:
            raise BadRequestException(detail="Email and updates are required")
        try:
            updates["updated_on"] = datetime.now()
            result = UserDAO.collection.update_one({"email": email, "is_deleted": False}, {"$set": updates})
            if result.modified_count == 0:
                logger.warning(f"No user updated for email: {email}")
                raise NotFoundException(detail=f"User with email {email} not found or no changes made")
            return True
        except Exception as e:
            logger.error(f"Error updating user with email {email}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to update user")

    @staticmethod
    def update_user_password_otp_remove(email: EmailStr, updates: str) -> bool:
        """Remove OTP field from user."""
        if not email or not updates:
            raise BadRequestException(detail="Email and updates to remove are required")
        try:
            result = UserDAO.collection.update_one({"email": email, "is_deleted": False}, {"$unset": {updates: ""}})
            if result.modified_count == 0:
                logger.warning(f"No OTP removed for email: {email}")
                raise NotFoundException(detail=f"User with email {email} not found")
            return True
        except Exception as e:
            logger.error(f"Error removing OTP for email {email}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to remove OTP")

    @staticmethod
    def soft_delete_user(user_id: str, email: EmailStr) -> bool:
        """Soft delete a user."""
        if not user_id or not email:
            raise BadRequestException(detail="User ID and email are required")
        try:
            result = UserDAO.collection.update_one(
                {"_id": ObjectId(user_id), "email": email, "is_deleted": False},
                {"$set": {"updated_on": datetime.now(), "is_deleted": True}}
            )
            if result.modified_count == 0:
                logger.warning(f"No user soft-deleted for email: {email}")
                raise NotFoundException(detail=f"User with email {email} not found")
            return True
        except Exception as e:
            logger.error(f"Error soft-deleting user with email {email}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to soft-delete user")
