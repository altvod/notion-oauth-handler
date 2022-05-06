import os

from aiohttp import web

from notion_oauth_handler.core.consumer import DummyNotionOAuthConsumer
from notion_oauth_handler.server.response import DummyNotionOAuthResponseFactory
from notion_oauth_handler.server.app import make_app


def run() -> None:
    app = make_app(
        consumer=DummyNotionOAuthConsumer(),
        response_factory=DummyNotionOAuthResponseFactory(),
        notion_client_id=os.environ['NOTION_CLIENT_ID'],
        notion_client_secret=os.environ['NOTION_CLIENT_SECRET'],
    )
    web.run_app(app)
