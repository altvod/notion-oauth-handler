import abc
from http import HTTPStatus

from aiohttp.web import Response

from notion_oauth_handler.core.dto import TokenResponseInfo


class NotionOAuthResponseFactory(abc.ABC):
    @abc.abstractmethod
    async def make_error_response(self, error: str) -> Response:
        raise NotImplementedError

    @abc.abstractmethod
    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        raise NotImplementedError


class DummyNotionOAuthResponseFactory(NotionOAuthResponseFactory):
    async def make_error_response(self, error: str) -> Response:
        return Response(text='Error', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return Response(text='OK', status=HTTPStatus.OK)


class EchoNotionOAuthResponseFactory(NotionOAuthResponseFactory):
    async def make_error_response(self, error: str) -> Response:
        return Response(text=f'Error: {error}', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return Response(text=f'Token info: {token_info}', status=HTTPStatus.OK)
