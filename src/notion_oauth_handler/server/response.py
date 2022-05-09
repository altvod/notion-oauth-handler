import abc
from http import HTTPStatus
from typing import Any, Optional

from aiohttp.web import Response
from aiohttp.typedefs import LooseHeaders

from notion_oauth_handler.core.dto import TokenResponseInfo


class NotionOAuthResponseFactory(abc.ABC):
    @abc.abstractmethod
    async def make_error_response(self, error: str) -> Response:
        raise NotImplementedError

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
    async def make_error_response(self, error: str) -> Response:
        return self.make_response(text='Error', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return self.make_response(text='OK', status=HTTPStatus.OK)


class EchoNotionOAuthResponseFactory(NotionOAuthResponseFactory):
    async def make_error_response(self, error: str) -> Response:
        return self.make_response(text=f'Error: {error}', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return self.make_response(text=f'Token info: {token_info}', status=HTTPStatus.OK)
