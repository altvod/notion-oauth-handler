import abc
import logging
from http import HTTPStatus
from typing import Any, Optional

from aiohttp.web import View, Response
from aiohttp.typedefs import LooseHeaders

import notion_oauth_handler.core.exc as exc
from notion_oauth_handler.core.dto import AuthRedirectInfo, TokenResponseInfo
from notion_oauth_handler.core.oauth_handler import NotionOAuthHandler
from notion_oauth_handler.server.middleware import OAUTH_HANDLER_REQUEST_KEY


_LOGGER = logging.getLogger(__name__)


class NotionOAuthRedirectView(View, abc.ABC):
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

    async def handle_notion_auth(self) -> Response:
        _LOGGER.info('Accepted redirect request')

        handler = self.make_oauth_handler()

        error_text = self.request.query.get('error', '')
        if error_text:
            try:
                await handler.handle_error(error_text=error_text)
            except exc.NotionAccessDenied:
                return await self.make_access_denied_response(error_text=error_text)

        redirect_info = AuthRedirectInfo(
            redirect_uri=str(self.request.url).split('?')[0],  # https://github.com/aio-libs/yarl/issues/723
            state=self.request.query.get('state', ''),
            code=self.request.query.get('code', ''),
        )
        try:
            token_info = await handler.handle_auth(redirect_info=redirect_info)
        except exc.TokenRequestFailed as err:
            return await self.make_bad_request_response(err=err)

        return await self.make_auth_response(token_info=token_info)

    def make_oauth_handler(self) -> NotionOAuthHandler:
        handler = self.request[OAUTH_HANDLER_REQUEST_KEY]
        assert isinstance(handler, NotionOAuthHandler)
        return handler

    async def get(self) -> Response:
        return await self.handle_notion_auth()

    @abc.abstractmethod
    async def make_bad_request_response(self, err: exc.TokenRequestFailed) -> Response:
        raise NotImplementedError

    @abc.abstractmethod
    async def make_access_denied_response(self, error_text: str) -> Response:
        raise NotImplementedError

    @abc.abstractmethod
    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        raise NotImplementedError


class DefaultNotionOAuthRedirectView(NotionOAuthRedirectView):
    async def make_bad_request_response(self, err: exc.TokenRequestFailed) -> Response:
        return self.make_response(
            status=HTTPStatus.BAD_REQUEST,
            text='Token request failed',
        )

    async def make_access_denied_response(self, error_text: str) -> Response:
        return self.make_response(text='Error', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return self.make_response(text='OK', status=HTTPStatus.OK)


class EchoNotionOAuthRedirectView(DefaultNotionOAuthRedirectView):
    async def make_access_denied_response(self, error_text: str) -> Response:
        return self.make_response(text=f'Error: {error_text}', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return self.make_response(text=f'Token info: {token_info}', status=HTTPStatus.OK)


class DebugNotionOAuthRedirectView(DefaultNotionOAuthRedirectView):
    async def make_bad_request_response(self, err: exc.TokenRequestFailed) -> Response:
        return self.make_response(
            status=HTTPStatus.BAD_REQUEST,
            text=(
                f'Request data: {err.request_data}\n'
                # f'Request headers: {[err.request_headers]}\n'
                f'Response status: {err.response_status}:\n'
                f'Response body: {err.response_body}'
            ),
        )
