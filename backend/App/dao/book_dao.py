import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Mapping, Any

from bson import ObjectId
from loguru import logger
from pymongo.collection import Collection

from .. import dao
from ..config import database
from ..exceptions import InternalServerErrorException, NotFoundException, BadRequestException, \
    UnprocessableEntityException
from ..vo import MongoBookData

# Define a constant for the base directory where books will be stored
BASE_BOOKS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "uploaded_books"  # Set your desired base directory here
BASE_BOOKS_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
BOOK_ID_ERROR_DETAIL = "Book ID is required"


class BookDAO:
    collection: Collection = database['books']

    @staticmethod
    def get_all_books() -> List[Dict[str, str]]:
        """Fetch all books sorted by upload date."""
        try:
            books = [
                {"book_id": str(book.pop("_id"))} | book
                for book in BookDAO.collection.find().sort("uploaded_on", -1)
            ]
            return books
        except Exception as e:
            logger.error(f"Error fetching all books: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch books")

    @staticmethod
    def get_user_books(book_ids) -> List[Dict[str, str]]:
        """Fetch books for given book IDs."""
        if not book_ids:
            logger.info("No book IDs provided")
            return []
        try:
            books = [
                {"book_id": str(book.pop("_id"))} | book
                for book in BookDAO.collection.find(
                    {"_id": {"$in": book_ids}}, {"book_path": 0, "audio_path": 0}
                ).sort("uploaded_on", -1)
            ]
            return books
        except Exception as e:
            logger.error(f"Error fetching user books: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch user books")

    @staticmethod
    def get_book_path(book_id) -> Mapping[str, Any]:
        """Fetch book paths."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            book_path = BookDAO.collection.find_one(
                {"_id": ObjectId(book_id)}, {"_id": 0, "book_path": 1, "audio_parent_path": 1, "image_parent_path": 1}
            )
            if not book_path:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            return book_path
        except Exception as e:
            logger.error(f"Error fetching paths for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch book paths")

    @staticmethod
    def get_book_cover(cover_path: str) -> bytes:
        """Fetch book cover image."""
        if not cover_path:
            raise BadRequestException(detail="Cover path is required")
        try:
            if not os.path.exists(cover_path) or not os.path.isfile(cover_path):
                raise NotFoundException(detail=f"Book cover not found at {cover_path}")
            with open(cover_path, "rb") as f:
                cover_data = f.read()
            return cover_data
        except Exception as e:
            logger.error(f"Error fetching book cover from {cover_path}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch book cover")

    @staticmethod
    def get_book_data(book_id) -> Dict:
        """Fetch book data and metadata."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            book_path = BookDAO.collection.find_one(
                {"_id": ObjectId(book_id)}, {"_id": 0, "book_path": 1, "title": 1, "book_type": 1}
            )
            if not book_path:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            if not os.path.exists(book_path["book_path"]):
                raise NotFoundException(detail=f"Book file not found at {book_path['book_path']}")
            with open(book_path["book_path"], "rb") as f:
                book_data = f.read()
            return {"book_data": book_data, "book_title": book_path["title"], "book_type": book_path["book_type"]}
        except Exception as e:
            logger.error(f"Error fetching book data for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch book data")

    @staticmethod
    def update_book_like(book_id) -> None:
        """Toggle like status for a book."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            book = BookDAO.collection.find_one({"_id": ObjectId(book_id)})
            if not book:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            new_like = not book["like"]
            BookDAO.collection.update_one({"_id": book["_id"]}, {"$set": {"like": new_like}})
            logger.info(f"{'Liked' if new_like else 'Unliked'} book_id: {book_id}")
        except Exception as e:
            logger.error(f"Error updating like for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to update book like")

    @staticmethod
    def update_book_bookmark(book_id) -> None:
        """Toggle bookmark status for a book."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            book = BookDAO.collection.find_one({"_id": ObjectId(book_id)})
            if not book:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            new_bookmark = not book["bookmark"]
            BookDAO.collection.update_one({"_id": book["_id"]}, {"$set": {"bookmark": new_bookmark}})
            logger.info(f"{'Bookmarked' if new_bookmark else 'Un-bookmarked'} book_id: {book_id}")
        except Exception as e:
            logger.error(f"Error updating bookmark for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to update book bookmark")

    @staticmethod
    def update_book_paths(book_id: str, updates: dict):
        """Update book paths."""
        if not book_id or not updates:
            raise BadRequestException(detail="Book ID and updates are required")
        try:
            book = BookDAO.collection.find_one({"_id": ObjectId(book_id)})
            if not book:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            BookDAO.collection.update_one({"_id": book["_id"]}, {"$set": updates})
        except Exception as e:
            logger.error(f"Error updating paths for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to update book paths")

    @staticmethod
    def insert_book(book_data: bytes, cover_page_data: bytes, title: str, book_format: str, file_type: str,
                    user_id: str) -> str:
        """Insert a new book and link it to a user."""
        if not all([book_data, cover_page_data, title, book_format, file_type, user_id]):
            raise BadRequestException(detail="All book data fields are required")
        if len(book_data) > MAX_FILE_SIZE:
            raise UnprocessableEntityException(detail="Book file size exceeds 50MB limit")
        try:
            book_folder = BASE_BOOKS_DIR / title.replace(" ", "_")
            book_folder.mkdir(parents=True, exist_ok=True)

            book_filename = f"{title}.{book_format}"
            cover_filename = f"{title}_cover.png"
            audio_folder = book_folder / "audio_output"
            image_folder = book_folder / "image_output"
            audio_folder.mkdir(parents=True, exist_ok=True)
            image_folder.mkdir(parents=True, exist_ok=True)

            book_path = book_folder / book_filename
            cover_path = book_folder / cover_filename

            with open(book_path, "wb") as f:
                f.write(book_data)
            with open(cover_path, "wb") as f:
                f.write(cover_page_data)

            mongo_data = MongoBookData(
                book_path=str(book_path),
                cover_path=str(cover_path),
                audio_parent_path=str(audio_folder),
                image_parent_path=str(image_folder),
                title=title,
                book_type=file_type,
                uploaded_on=datetime.now()
            ).dict()
            result = BookDAO.collection.insert_one(mongo_data)
            book_id = str(result.inserted_id)

            dao.UserBookDAO.insert_user_book(user_id, book_id)
            return book_id
        except Exception as e:
            logger.error(f"Error inserting book '{title}': {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to insert book")

    @staticmethod
    def delete_book(book_id: str) -> bool:
        """Delete a book and its associated data."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            book = BookDAO.collection.find_one({"_id": ObjectId(book_id)}, {"_id": 0, "title": 1})
            if not book:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            book_folder = BASE_BOOKS_DIR / book["title"].replace(" ", "_")
            if book_folder.exists():
                shutil.rmtree(book_folder)
            dao.BookAiDAO.delete_content(book_id)
            dao.UserBookDAO.delete_user_book(book_id)
            result = BookDAO.collection.delete_one({"_id": ObjectId(book_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to delete book")
