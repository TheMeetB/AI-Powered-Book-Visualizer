import base64
from io import BytesIO
from typing import BinaryIO, Dict

from fastapi.responses import StreamingResponse
from loguru import logger

from ...dao import BookDAO, UserBookDAO
from ...exceptions import NotFoundException, InternalServerErrorException, BadRequestException, \
    ServiceUnavailableException
from ...utils import CoverPageExtractor

DATABASE_ERROR_DETAIL = "Database service unavailable"


class DashboardController:
    @staticmethod
    async def get_books() -> Dict:
        try:
            books = BookDAO.get_all_books()
            if not books:
                logger.info("No books found in the database")
            logger.info(f"Retrieved {len(books)} books")
            return {
                "success": True,
                "status_code": 200,
                "message": "Books retrieved successfully",
                "data": books or []
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except Exception as e:
            logger.error(f"Failed to fetch books: {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def get_user_books(user_id: str) -> Dict:
        try:
            books = UserBookDAO.get_user_books(user_id)
            if not books:
                logger.info(f"No books found for user '{user_id}'")
                raise NotFoundException(detail="No books found for this user")
            for book in books:
                try:
                    cover_data = BookDAO.get_book_cover(book["cover_path"])
                    book["book_cover"] = f"data:image/png;base64,{base64.b64encode(cover_data).decode('utf-8')}"
                except Exception as e:
                    logger.warning(f"Failed to load cover for book '{book.get('title', 'unknown')}': {str(e)}")
                    book["book_cover"] = None
            logger.info(f"Retrieved {len(books)} books for user_id: '{user_id}'")
            return {
                "success": True,
                "status_code": 200,
                "message": "User books retrieved successfully",
                "data": books
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable for user_id '{user_id}': {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except Exception as e:
            logger.error(f"Failed to fetch books for user_id '{user_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def get_book_data(book_id: str) -> StreamingResponse:
        try:
            file = BookDAO.get_book_data(book_id)
            if not file:
                raise NotFoundException(detail=f"Book with ID '{book_id}' not found")
            headers = {"Content-Disposition": f'attachment; filename="{file["book_title"]}"'}
            logger.info(f"Streaming book data for book_id: '{book_id}'")
            return StreamingResponse(BytesIO(file["book_data"]), media_type=file["book_type"], headers=headers)
        except ConnectionError as e:
            logger.error(f"Database unavailable for book_id '{book_id}': {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to stream book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def like_book(book_id: str) -> Dict:
        try:
            BookDAO.update_book_like(book_id)
            return {
                "success": True,
                "status_code": 200,
                "message": "Book liked/unliked successfully",
                "data": None
            }
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to like/unlike book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def bookmark_book(book_id: str) -> Dict:
        try:
            BookDAO.update_book_bookmark(book_id)
            return {
                "success": True,
                "status_code": 200,
                "message": "Book bookmarked/un-bookmarked successfully",
                "data": None
            }
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to bookmark/un-bookmark    book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def upload_book(book_data: BinaryIO, file_name: str, file_type: str, user_id: str) -> Dict:
        try:
            title = file_name.rsplit('.', 1)[0]
            book_format = file_name.rsplit('.', 1)[1]

            existing_book = BookDAO.collection.find_one({"title": title})
            if existing_book:
                logger.warning(f"Book with title '{title}' already exists")
                raise BadRequestException(detail=f"Book with title '{title}' already exists")

            cover_page_data = CoverPageExtractor.main(book_data.read(), file_type)
            book_data.seek(0)  # Reset file pointer
            book_id = BookDAO.insert_book(book_data.read(), cover_page_data, title, book_format, file_type, user_id)
            logger.info(f'Book uploaded: "{str(title)}" (ID: "{str(book_id)}") by user ID: "{str(user_id)}"')
            return {
                "success": True,
                "status_code": 200,
                "message": "Book successfully uploaded",
                "data": {"book_id": book_id}
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable during upload: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to upload book '{file_name}' for user_id '{user_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def delete_book(book_id: str) -> Dict:
        try:
            BookDAO.delete_book(book_id)
            logger.info(f"Book_id '{book_id}' deleted")
            return {
                "success": True,
                "status_code": 200,
                "message": "Book deleted successfully",
                "data": None
            }
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to delete book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()
