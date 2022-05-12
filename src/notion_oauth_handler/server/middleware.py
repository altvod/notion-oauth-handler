from typing import Awaitable, Callable

from aiohttp.web import middleware, Request, Response

from notion_oauth_handler.core.consumer import NotionOAuthConsumer
from notion_oauth_handler.core.oauth_handler import NotionOAuthHandler


OAUTH_HANDLER_REQUEST_KEY = '__ouath_handler__'
CUSTOM_SETTINGS_REQUEST_KEY = '__custom_settings__'


def notion_oauth_middleware_factory(
        notion_client_id: str,
        notion_client_secret: str,
        consumer: NotionOAuthConsumer,
        custom_settings: dict,
):
    oauth_handler = NotionOAuthHandler(
        consumer=consumer,
        client_id=notion_client_id, client_secret=notion_client_secret,
    )

    @middleware
    async def middleware_impl(request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
        request[OAUTH_HANDLER_REQUEST_KEY] = oauth_handler
        request[CUSTOM_SETTINGS_REQUEST_KEY] = custom_settings
        return await handler(request)

    return middleware_impl
