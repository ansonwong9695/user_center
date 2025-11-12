from ninja import NinjaAPI
from .exception.business_exception import BusinessException
from users.schemas import ResponseBase
from core.constants import ErrorCode
import logging

logger = logging.getLogger("django")


def exception_handler(api: NinjaAPI):
    @api.exception_handler(BusinessException)
    def handle_business_exception(request, exc: BusinessException):
        logger.error(
            f"BusinessException occurred: {exc.code} - {exc.message}-{exc.description}",
            exc_info=True,
        )
        response = ResponseBase.from_error_code(
            code=exc.code, description=exc.description, message=exc.message
        )
        return api.create_response(request, response, status=400)

    @api.exception_handler(Exception)
    def handle_exception(request, exc: Exception):
        logger.error(f"Exception occurred: {str(exc)}", exc_info=True)
        response = ResponseBase.from_error_code(error_code=ErrorCode.PARAMS_ERROR)
        return api.create_response(request, response, status=500)
