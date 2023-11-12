import logging

from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

from web.response import FailResponse, NoLoginResponse, TokenExpireResponse


class ScriptAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        return None

    def process_response(self, request, response):
        if isinstance(response, HttpResponse) and hasattr(response, "data") and response.data != None:
            if response.data.get("code") == "user_not_found":
                return NoLoginResponse()
            if response.data.get("code") == "token_not_valid":
                return TokenExpireResponse()
        return response


class GlobalExceptionHandleMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        if isinstance(exception, BizException):
            logging.warning(exception.errMsg)
            return FailResponse(exception.errCode, exception.errMsg)
        else:
            logging.error(exception)
            return FailResponse(-1, "System error, please try again.")


class BizException(Exception):
    def __init__(self, errCode, errMsg):
        self.errCode = errCode
        self.errMsg = errMsg
        super().__init__()
