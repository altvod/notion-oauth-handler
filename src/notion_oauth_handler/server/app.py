import os

from aiohttp import web

from notion_oauth_handler.core.consumer import NotionOAuthConsumer, DummyNotionOAuthConsumer
from notion_oauth_handler.server.view import NotionOAuthRedirectView
from notion_oauth_handler.server.middleware import notion_oauth_middleware_factory
from notion_oauth_handler.server.response import NotionOAuthResponseFactory, DummyNotionOAuthResponseFactory


def make_app(
        consumer: NotionOAuthConsumer,
        response_factory: NotionOAuthResponseFactory,
        notion_client_id: str,
        notion_client_secret: str,
        base_path: str = '',
) -> web.Application:
    base_path = base_path.rstrip('/')
    app = web.Application(
        middlewares=[
            notion_oauth_middleware_factory(
                consumer=consumer,
                response_factory=response_factory,
                notion_client_id=notion_client_id,
                notion_client_secret=notion_client_secret,
            )
        ],
    )
    app.add_routes([
        web.get(f'{base_path}/auth_redirect', NotionOAuthRedirectView),
    ])
    return app


def run() -> None:
    app = make_app(
        consumer=DummyNotionOAuthConsumer(),
        response_factory=DummyNotionOAuthResponseFactory(),
        notion_client_id=os.environ['NOTION_CLIENT_ID'],
        notion_client_secret=os.environ['NOTION_CLIENT_SECRET'],
    )
    web.run_app(app)
