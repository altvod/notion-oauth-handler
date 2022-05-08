import logging
from http import HTTPStatus

import aiohttp.web

from notion_oauth_handler.core import exc
from notion_oauth_handler.core.dto import AuthRedirectInfo
from notion_oauth_handler.core.oauth_handler import NotionOAuthHandler
from notion_oauth_handler.server.middleware import (
    OAUTH_HANDLER_REQUEST_KEY, RESPONSE_FACTORY_REQUEST_KEY,
)
from notion_oauth_handler.server.response import NotionOAuthResponseFactory


_LOGGER = logging.getLogger(__name__)


class NotionOAuthRedirectView(aiohttp.web.View):
    def get_oauth_handler(self) -> NotionOAuthHandler:
        handler = self.request[OAUTH_HANDLER_REQUEST_KEY]
        assert isinstance(handler, NotionOAuthHandler)
        return handler

    def get_response_factory(self) -> NotionOAuthResponseFactory:
        response_factory = self.request[RESPONSE_FACTORY_REQUEST_KEY]
        assert isinstance(response_factory, NotionOAuthResponseFactory)
        return response_factory

    async def get(self) -> aiohttp.web.Response:
        _LOGGER.info('Accepted redirect request')

        handler = self.get_oauth_handler()
        response_factory = self.get_response_factory()

        error = self.request.query.get('error', '')
        if error:
            try:
                await handler.handle_error(error=error)
            except exc.NotionAccessDenied:
                return await response_factory.make_error_response(error=error)

        redirect_info = AuthRedirectInfo(
            redirect_uri=str(self.request.url),
            state=self.request.query.get('state', ''),
            code=self.request.query.get('code', ''),
        )
        try:
            token_info = await handler.handle_auth(redirect_info=redirect_info)
        except exc.TokenRequestFailed:
            return aiohttp.web.Response(
                status=HTTPStatus.BAD_REQUEST,
                text='Token request failed',
            )

        return await response_factory.make_auth_response(token_info=token_info)
