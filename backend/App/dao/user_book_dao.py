from bson import ObjectId
from loguru import logger
from pymongo.collection import Collection

from .. import dao
from ..config import database
from ..exceptions import InternalServerErrorException, BadRequestException
from ..vo import MongoUserBookData


class UserBookDAO:
    collection: Collection = database['userBooks']

    @staticmethod
    def get_user_books(user_id) -> list[dict]:
        """Fetch all books associated with a user."""
        if not user_id:
            raise BadRequestException(detail="User ID is required")
        try:
            user_books = list(UserBookDAO.collection.find({"user_id": user_id}, {"_id": 0, "book_id": 1}))
            book_ids = [ObjectId(book["book_id"]) for book in user_books]
            if not book_ids:
                logger.info(f"No books found for user_id: {user_id}")
                return []
            books = dao.BookDAO.get_user_books(book_ids)
            return books
        except Exception as e:
            logger.error(f"Error fetching books for user_id {user_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch user books")

    @staticmethod
    def insert_user_book(user_id: str, book_id: str) -> None:
        """Link a book to a user."""
        if not user_id or not book_id:
            raise BadRequestException(detail="User ID and Book ID are required")
        try:
            existing = UserBookDAO.collection.find_one({"user_id": user_id, "book_id": book_id})
            if existing:
                logger.info(f"Book_id {book_id} already linked to user_id {user_id}")

            user_book_data = MongoUserBookData(user_id=user_id, book_id=book_id).dict()
            UserBookDAO.collection.insert_one(user_book_data)
        except Exception as e:
            logger.error(f"Error linking book_id {book_id} to user_id {user_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to link book to user")

    @staticmethod
    def delete_user_book(book_id: str) -> None:
        """Unlink a book from all users."""
        if not book_id:
            raise BadRequestException(detail="Book ID is required")
        try:
            result = UserBookDAO.collection.delete_one({"book_id": book_id})
        except Exception as e:
            logger.error(f"Error unlinking book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to unlink book")
