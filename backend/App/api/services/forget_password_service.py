import os
import random
from typing import Dict

from fastapi_mail import MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from ...dao import UserDAO
from ...exceptions import BadRequestException, NotFoundException, InternalServerErrorException, \
    ServiceUnavailableException
from ...utils import Hashing, MailConfig

template_loader = FileSystemLoader("backend/App/utils/template")
template_env = Environment(loader=template_loader)
ERROR_DETAIL = "User not found"
DATABASE_ERROR_DETAIL = "Database service unavailable"


class ForgetPasswordController:
    @staticmethod
    async def forget_password_mail(background_tasks, request) -> Dict:
        try:
            user = UserDAO.get_user_by_email(request.email)
            if not user:
                raise NotFoundException(detail=ERROR_DETAIL)

            otp_to_send = random.randint(1000, 9999)
            logger.info(f"OTP generated for email: '{request.email}'")
            UserDAO.update_user(request.email, {"password_otp": otp_to_send})

            template = template_env.get_template("reset_password_mail.html")
            rendered_html = template.render(
                username=user["username"],
                otp=otp_to_send,
                support_email=os.getenv('SUPPORT_MAIL')
            )
            message = MessageSchema(
                subject="Password Reset Request",
                recipients=[request.email],
                body=rendered_html,
                subtype=MessageType.html,
            )
            background_tasks.add_task(MailConfig.fm.send_message, message)
            logger.info(f"Password reset email sent to: '{request.email}'")
            return {
                "success": True,
                "status_code": 200,
                "message": "Email sent successfully",
                "data": None
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to send reset email to '{request.email}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def forget_verify_otp(request) -> Dict:
        try:
            user = UserDAO.get_user_by_email(request.email)
            if not user:
                raise NotFoundException(detail=ERROR_DETAIL)
            if str(request.otp) != str(user.get("password_otp")):
                raise BadRequestException(detail="Incorrect OTP")
            UserDAO.update_user_password_otp_remove(user["email"], "password_otp")
            logger.info(f"OTP verified for email: '{request.email}'")
            return {
                "success": True,
                "status_code": 200,
                "message": "OTP Verified",
                "data": None
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except BadRequestException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to verify OTP for '{request.email}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()

    @staticmethod
    async def reset_password(request) -> Dict:
        try:
            user = UserDAO.get_user_by_email(request.email)
            if not user:
                raise NotFoundException(detail=ERROR_DETAIL)
            password_hash = Hashing.encrypt(request.password)
            UserDAO.update_user(request.email, {'password': password_hash})
            logger.info(f"Password reset successful for email: '{request.email}'")
            return {
                "success": True,
                "status_code": 200,
                "message": "Password Reset Successful",
                "data": None
            }
        except ConnectionError as e:
            logger.error(f"Database unavailable: {str(e)}", exc_info=True)
            raise ServiceUnavailableException(detail=DATABASE_ERROR_DETAIL)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to reset password for '{request.email}': {str(e)}", exc_info=True)
            raise InternalServerErrorException()
