import abc
from http import HTTPStatus
from typing import Any, Optional

from aiohttp.web import Response
from aiohttp.typedefs import LooseHeaders

import notion_oauth_handler.core.exc as exc
from notion_oauth_handler.core.dto import TokenResponseInfo


class NotionOAuthResponseFactory(abc.ABC):
    @abc.abstractmethod
    async def make_access_denied_response(self, error_text: str) -> Response:
        raise NotImplementedError

    async def make_bad_request_response(self, err: exc.TokenRequestFailed) -> Response:
        return self.make_response(
            status=HTTPStatus.BAD_REQUEST,
            text='Token request failed',
        )

    @abc.abstractmethod
    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        raise NotImplementedError

    def make_response(
            self,
            *,
            body: Any = None,
            status: int = 200,
            text: Optional[str] = None,
            headers: Optional[LooseHeaders] = None,
            content_type: Optional[str] = None,
    ) -> Response:
        """Just a wrapper for the Response object"""
        return Response(body=body, status=status, text=text, headers=headers, content_type=content_type)


class DummyNotionOAuthResponseFactory(NotionOAuthResponseFactory):
    async def make_access_denied_response(self, error_text: str) -> Response:
        return self.make_response(text='Error', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return self.make_response(text='OK', status=HTTPStatus.OK)


class EchoNotionOAuthResponseFactory(NotionOAuthResponseFactory):
    async def make_access_denied_response(self, error_text: str) -> Response:
        return self.make_response(text=f'Error: {error_text}', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return self.make_response(text=f'Token info: {token_info}', status=HTTPStatus.OK)


class DebugNotionOAuthResponseFactory(EchoNotionOAuthResponseFactory):
    async def make_bad_request_response(self, err: exc.TokenRequestFailed) -> Response:
        return self.make_response(
            status=HTTPStatus.BAD_REQUEST,
            text=(
                f'Request data: {err.request_data}\n'
                f'Request headers: {[err.request_headers]}\n'
                f'Response status: {err.response_status}:\n'
                f'Response body: {err.response_body}'
            ),
        )

