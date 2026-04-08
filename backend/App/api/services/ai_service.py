from io import BytesIO
from typing import Dict
from zipfile import ZipFile, ZIP_DEFLATED

from loguru import logger
from starlette.responses import StreamingResponse

from ...ai import api_module
from ...dao import BookAiDAO, BookDAO
from ...exceptions import NotFoundException, InternalServerErrorException, ServiceUnavailableException

DATABASE_ERROR_DETAIL = "Database service unavailable"


class AIController:
    @staticmethod
    def get_summary(book_id: str) -> Dict[str, int | str | list[Dict[str, str]] | bool]:
        try:
            book_summary = BookAiDAO.get_summary_with_chapter_id(book_id)
            if not book_summary:
                raise NotFoundException(detail=f"Summary not found for book_id '{book_id}'")
            logger.info(f"Retrieved summary for book_id: '{book_id}'")
            return {
                "success": True,
                "status_code": 200,
                "message": "Book summary fetched successfully",
                "data": book_summary
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to fetch summary for book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch book summary")

    @staticmethod
    def get_audio(book_id: str) -> StreamingResponse:
        try:
            audio_file_list = BookAiDAO.get_summary_audio(book_id)
            if not audio_file_list:
                raise NotFoundException(detail="No audio files found for this book")
            # Create a ZIP file in memory
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zip_file:
                for file_name in audio_file_list:
                    zip_file.write(file_name, arcname=file_name.split("\\")[-1])
            zip_buffer.seek(0)  # Rewind the buffer to the beginning, so it can be read from the start
            logger.info(f"Generated audio ZIP for book_id: '{book_id}'")
            # Return the ZIP file as a streaming response
            return StreamingResponse(
                zip_buffer, media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=audio_files.zip"}
            )
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to fetch audio for book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch book audio")

    @staticmethod
    def get_image(book_id: str) -> StreamingResponse:
        try:
            image_file_list = BookAiDAO.get_summary_image(book_id)
            if not image_file_list:
                raise NotFoundException(detail="No image files found for this book")
            # Create a ZIP file in memory
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w", ZIP_DEFLATED) as zip_file:
                for file_name in image_file_list:
                    zip_file.write(file_name, arcname=file_name.split("\\")[-1])
            zip_buffer.seek(0)  # Rewind the buffer to the beginning, so it can be read from the start
            logger.info(f"Generated image ZIP for book_id: '{book_id}'")
            # Return the ZIP file as a streaming response
            return StreamingResponse(
                zip_buffer, media_type="application/zip",
                headers={"Content-Disposition": "attachment; filename=image_files.zip"}
            )
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to fetch image for book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch book image")

    @staticmethod
    async def generate_book_summary(book_id: str):
        try:
            # Generating the book summary content and storing it
            book_path = BookDAO.get_book_path(book_id)
            if not book_path:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            book_ai_content = await api_module.main(book_path["book_path"])
            BookAiDAO.insert_book_content(book_id, book_ai_content)
            logger.info(f"Generated summary for book_id: '{book_id}'")
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate summary for book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def generate_book_summary_audio(book_id: str):
        try:
            # Generating the book summary content and storing it
            book_path = BookDAO.get_book_path(book_id)
            if not book_path:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            audio_paths = BookAiDAO.generate_audio(book_id, book_path)
            update = {"audio_paths": audio_paths}
            BookDAO.update_book_paths(book_id, update)
            logger.info(f"Generated audio for book_id: '{book_id}'")
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate audio for book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def generate_book_summary_images(book_id: str):
        try:
            # Generating the book summary content and storing it
            book_path = BookDAO.get_book_path(book_id)
            if not book_path:
                raise NotFoundException(detail=f"Book with ID {book_id} not found")
            image_paths = BookAiDAO.generate_images(book_id, book_path)
            update = {"image_paths": image_paths}
            BookDAO.update_book_paths(book_id, update)
            logger.info(f"Generated image for book_id: '{book_id}'")
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to generate image for book_id '{book_id}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()
