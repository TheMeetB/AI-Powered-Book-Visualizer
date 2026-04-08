from typing import Mapping, Any, List, Dict

from bson import ObjectId
from loguru import logger
from pymongo.collection import Collection

from .. import dao
from ..ai import loop_for_speech, loop_for_image
from ..config import database
from ..exceptions import InternalServerErrorException, BadRequestException, NotFoundException
from ..vo import MongoBookAiData

BOOK_ID_ERROR_DETAIL = "Book ID is required"


class BookAiDAO:
    collection: Collection = database['booksContent']

    @staticmethod
    def get_summary_with_chapter_id(book_id: str) -> List[Dict[str, str]]:
        """Fetch chapter summaries for a given book."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            summaries = list(
                BookAiDAO.collection.find(
                    {"book_id": book_id}, {"_id": 0, "chapter_id": 1, "summary": 1}
                ).sort("_id", 1)
            )
            if not summaries:
                logger.warning(f"No summaries found for book_id: {book_id}")
                raise NotFoundException(detail=f"No summaries found for book {book_id}")
            return summaries
        except Exception as e:
            logger.error(f"Error fetching summaries for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch book summaries")

    @staticmethod
    def get_summary_audio(book_id: str) -> List[str]:
        """Fetch audio paths for a book's summaries."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            audio_data = dao.BookDAO.collection.find_one(
                {"_id": ObjectId(book_id)}, {"_id": 0, "audio_paths": 1}
            )
            if not audio_data or not audio_data.get("audio_paths"):
                logger.warning(f"No audio paths found for book_id: {book_id}")
                raise NotFoundException(detail=f"No audio found for book {book_id}")
            return audio_data["audio_paths"]
        except Exception as e:
            logger.error(f"Error fetching audio for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch summary audio")

    @staticmethod
    def get_summary_image(book_id: str) -> List[str]:
        """Fetch image paths for a book's summaries."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            image_data = dao.BookDAO.collection.find_one(
                {"_id": ObjectId(book_id)}, {"_id": 0, "image_paths": 1}
            )
            if not image_data or not image_data.get("image_paths"):
                logger.warning(f"No image paths found for book_id: {book_id}")
                raise NotFoundException(detail=f"No image found for book {book_id}")
            return image_data["image_paths"]
        except Exception as e:
            logger.error(f"Error fetching image for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to fetch summary image")

    @staticmethod
    def insert_book_content(book_id: str, book_ai_content: list[dict[str, str | dict[str, str]]]) -> None:
        """Insert AI-generated book content into the database."""
        if not book_id or not book_ai_content:
            raise BadRequestException(detail="Book ID and content are required")
        try:
            mongo_data = [
                MongoBookAiData(
                    book_id=book_id,
                    chapter_id=content["chapter_id"],
                    summary=content["summary"],
                    character=content.get("characters", {}),
                    places=content.get("places", {})
                ).dict()
                for content in book_ai_content
            ]
            BookAiDAO.collection.insert_many(mongo_data)
        except Exception as e:
            logger.error(f"Error inserting content for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to store book content")

    @staticmethod
    def generate_audio(book_id: str, book_path: Mapping[str, Any] | None) -> List[str]:
        """Generate and save audio for book summaries."""
        if not book_id or not book_path:
            raise BadRequestException(detail="Book ID and path are required")
        try:
            summaries = BookAiDAO.get_summary_with_chapter_id(book_id)
            summary_texts = [
                (s["chapter_id"], f"Chapter {s['chapter_id']}. Summary: {s.get('summary', 'No summary available')}")
                for s in summaries
            ]
            audio_outputs = loop_for_speech(summary_texts)
            if not audio_outputs:
                logger.warning(f"No audio generated for book_id: {book_id}")
                raise InternalServerErrorException(detail="Audio generation failed")

            audio_paths = []
            audio_parent_path = book_path["audio_parent_path"]
            for (chapter_id, audio_content), (orig_chapter_id, _) in zip(audio_outputs, summary_texts):
                if not audio_content:
                    logger.warning(f"Audio generation failed for chapter {orig_chapter_id}")
                    continue
                audio_file = f"{audio_parent_path}/chapter_{orig_chapter_id}.mp3"
                with open(audio_file, "wb") as f:
                    f.write(audio_content)
                audio_paths.append(audio_file)
                logger.info(f"Saved audio for chapter {orig_chapter_id} at {audio_file}")

            if not audio_paths:
                raise InternalServerErrorException(detail="No audio files were generated")
            return audio_paths
        except Exception as e:
            logger.error(f"Error generating audio for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to generate audio")

    @staticmethod
    def generate_images(book_id: str, book_path: Mapping[str, Any] | None) -> List[str]:
        """Generate and save images for book summaries."""
        if not book_id or not book_path:
            raise BadRequestException(detail="Book ID and path are required")
        try:
            summaries = BookAiDAO.get_summary_with_chapter_id(book_id)
            summary_texts = [
                (s["chapter_id"], f"Chapter {s['chapter_id']}. Summary: {s.get('summary', 'No summary available')}")
                for s in summaries
            ]
            image_output = loop_for_image(summary_texts)
            image_paths = []
            image_parent_path = book_path["image_parent_path"]
            for (chapter_id, image_content), (orig_chapter_id, _) in zip(image_output, summary_texts):
                if not image_content:
                    logger.warning(f"Image generation failed for chapter {orig_chapter_id}")
                    continue
                image_file = f"{image_parent_path}/chapter_{orig_chapter_id}.webp"
                with open(image_file, "wb") as f:
                    f.write(image_content)
                image_paths.append(image_file)
                logger.info(f"Saved image for chapter {orig_chapter_id} at {image_file}")

            if not image_paths:
                raise InternalServerErrorException(detail="No image files were generated")
            return image_paths
        except Exception as e:
            logger.error(f"Error generating image for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to generate image")

    @staticmethod
    def delete_content(book_id: str) -> None:
        """Delete all AI content for a book."""
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        try:
            result = BookAiDAO.collection.delete_many({"book_id": book_id})
        except Exception as e:
            logger.error(f"Error deleting content for book_id {book_id}: {str(e)}", exc_info=True)
            raise InternalServerErrorException(detail="Failed to delete book content")
