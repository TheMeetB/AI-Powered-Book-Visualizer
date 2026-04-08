from fastapi import APIRouter, Depends
from loguru import logger

from ..services import AIController
from ...dto import StandardResponse
from ...exceptions import BadRequestException, NotFoundException, InternalServerErrorException, \
    ServiceUnavailableException
from ...utils import GoogleOAuth2

router = APIRouter(
    prefix="/book",
    tags=["AI"],
    dependencies=[Depends(GoogleOAuth2.get_current_user)]
)

BOOK_ID_ERROR_DETAIL = "Book ID cannot be empty"


@router.get("/{book_id}/summary", response_model=StandardResponse)
async def book_summary(book_id: str):
    try:
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        logger.info(f"Fetching summary for book_id: '{book_id}'")
        result = AIController.get_summary(book_id)
        return StandardResponse(**result)
    except NotFoundException as e:
        raise e
    except ServiceUnavailableException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to fetch summary for book_id '{book_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to fetch book summary")


@router.get("/{book_id}/audio")
async def book_audio(book_id: str):
    try:
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        logger.info(f"Fetching audio for book_id: '{book_id}'")
        response = AIController.get_audio(book_id)
        return response  # StreamingResponse
    except NotFoundException as e:
        raise e
    except ServiceUnavailableException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to fetch audio for book_id '{book_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to fetch book audio")


@router.get("/{book_id}/image")
async def book_image(book_id: str):
    try:
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        logger.info(f"Fetching image for book_id: '{book_id}'")
        response = AIController.get_image(book_id)
        return response  # StreamingResponse
    except NotFoundException as e:
        raise e
    except ServiceUnavailableException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to fetch image for book_id '{book_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to fetch book image")
