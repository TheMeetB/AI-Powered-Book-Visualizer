from fastapi import APIRouter, Request, File, UploadFile, status, Form, Depends
from fastapi.background import BackgroundTasks
from loguru import logger

from ..services import DashboardController, AIController
from ...dto import StandardResponse
from ...exceptions import BadRequestException, NotFoundException, InternalServerErrorException, \
    ServiceUnavailableException
from ...utils import GoogleOAuth2

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Depends(GoogleOAuth2.get_current_user)]
)

BOOK_ID_ERROR_DETAIL = "Book ID cannot be empty"
USER_ID_ERROR_DETAIL = "User ID cannot be empty"
ALLOWED_EXTENSIONS = {".pdf", ".epub", ".txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.get("", response_model=StandardResponse)
async def dashboard(request: Request):
    try:
        user_details = request.session.get('user')
        username = user_details.get("username", "unknown")
        logger.info(f"Dashboard accessed by user: '{username}'")
        return StandardResponse(
            success=True,
            status_code=status.HTTP_200_OK,
            message="Dashboard accessed successfully",
            data={"status": "ok"}
        )
    except Exception as e:
        logger.error(f"Failed to access dashboard : {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to access dashboard")


@router.get("/get_all_books", response_model=StandardResponse)
async def list_all_books():
    try:
        logger.info("Fetching all books")
        books_response = await DashboardController.get_books()
        return StandardResponse(**books_response)
    except ServiceUnavailableException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to retrieve books: {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to retrieve books")


@router.get("/get_all_books/{user_id}", response_model=StandardResponse)
async def list_user_books(user_id: str):
    try:
        if not user_id:
            raise BadRequestException(detail=USER_ID_ERROR_DETAIL)
        logger.info(f"Fetching books for user_id: '{user_id}'")
        books = await DashboardController.get_user_books(user_id)
        return StandardResponse(**books)
    except NotFoundException as e:
        raise e
    except ServiceUnavailableException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to retrieve books for user_id '{user_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to retrieve user books")


@router.get("/get_book_data/{book_id}")
async def get_book_data(book_id: str):
    try:
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        logger.info(f"Fetching data for book_id: '{book_id}'")
        response = await DashboardController.get_book_data(book_id)
        return response  # StreamingResponse
    except NotFoundException as e:
        raise e
    except ServiceUnavailableException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to retrieve book data for book_id '{book_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to retrieve book data")


@router.post("/{book_id}/like", response_model=StandardResponse)
async def like_book(book_id: str):
    try:
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        logger.info(f"Request received to like/unlike book_id: '{book_id}'")
        result = await DashboardController.like_book(book_id)
        return StandardResponse(**result)
    except NotFoundException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to like/unlike book_id '{book_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to like/unlike book")


@router.post("/{book_id}/bookmark", response_model=StandardResponse)
async def bookmark_book(book_id: str):
    try:
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        logger.info(f"Request received to bookmark/un-bookmark book ID: '{book_id}'")
        result = await DashboardController.bookmark_book(book_id)
        return StandardResponse(**result)
    except NotFoundException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to bookmark/un-bookmark book_id '{book_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to bookmark/un-bookmark book")


@router.post("/insert_book", response_model=StandardResponse)
async def insert_book(background_tasks: BackgroundTasks, data: UploadFile = File(...), user_id: str = Form(...)):
    try:
        if not user_id:
            raise BadRequestException(detail=USER_ID_ERROR_DETAIL)
        if not data:
            raise BadRequestException(detail="File upload cannot be empty")
        file_name = data.filename or ""
        if not file_name:
            raise BadRequestException(detail="File name cannot be empty")
        
        ext = ""
        if "." in file_name:
            ext = "." + file_name.rsplit('.', 1)[-1].lower()
            
        if ext not in ALLOWED_EXTENSIONS:
            raise BadRequestException(detail="Only PDF, EPUB, and TEXT files are allowed")
            
        # Normalize file_type for the extractor
        if ext == ".pdf":
            file_type = "application/pdf"
        elif ext == ".epub":
            file_type = "application/epub+zip"
        elif ext == ".txt":
            file_type = "text/plain"
        else:
            file_type = data.content_type

        file_content = await data.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise BadRequestException(detail="File size exceeds 50MB limit")

        logger.info(f'Uploading book "{file_name}" for user_id: "{user_id}"')
        data.file.seek(0)
        book_data = data.file
        result = await DashboardController.upload_book(book_data, file_name, file_type, user_id)

        # background tasks for book content generations
        background_tasks.add_task(AIController.generate_book_summary, result["data"]["book_id"])
        background_tasks.add_task(AIController.generate_book_summary_audio, result["data"]["book_id"])
        # background_tasks.add_task(AIController.generate_book_summary_images, result["data"]["book_id"])
        return StandardResponse(**result)
    except BadRequestException as e:
        raise e
    except ServiceUnavailableException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to upload book for user_id '{user_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to upload book")


@router.delete("/{book_id}/delete", response_model=StandardResponse)
async def delete_book(book_id: str):
    try:
        if not book_id:
            raise BadRequestException(detail=BOOK_ID_ERROR_DETAIL)
        logger.info(f"Deleting book_id: '{book_id}'")
        result = await DashboardController.delete_book(book_id)
        return StandardResponse(**result)
    except NotFoundException as e:
        raise e
    except Exception as e:
        logger.error(f"Failed to delete book_id '{book_id}': {str(e)}", exc_info=True)
        raise InternalServerErrorException(detail="Failed to delete book")
