import os
from typing import Optional, Type

from aiohttp import web

from notion_oauth_handler.core.consumer import NotionOAuthConsumer
from notion_oauth_handler.server.view import NotionOAuthRedirectView
from notion_oauth_handler.server.middleware import notion_oauth_middleware_factory
from notion_oauth_handler.server.config import AppConfiguration, load_config_from_file
from notion_oauth_handler.entrypoints import get_consumer, get_auth_view_cls


def make_app(
        *,
        consumer: NotionOAuthConsumer,
        auth_view_cls: Type[NotionOAuthRedirectView],
        notion_client_id: str,
        notion_client_secret: str,
        base_path: str = '',
        redirect_path: str = '/auth_redirect',
        custom_settings: dict,
) -> web.Application:
    """
    Create Notion OAuth handling server (aiohttp Application)

    :param consumer: a `NotionOAuthConsumer` subclass instance
        that implements the main logic (e.g. stores the token in a database)
    :param auth_view_cls: a `NotionOAuthRedirectView` subclass that handles
        all of the main oauth request
    :param notion_client_id: client ID of the Notion integration
    :param notion_client_secret: client secret of the Notion integration
    :param base_path: custom base path for all routes
    :param redirect_path: relative path for the redirect handler
    :param custom_settings: dict,: custom app configuration
    :return: an aiohttp `Application` instance
    """

    base_path = base_path.rstrip('/')
    redirect_path = redirect_path.lstrip('/')

    app = web.Application(
        middlewares=[
            notion_oauth_middleware_factory(
                consumer=consumer,
                notion_client_id=notion_client_id,
                notion_client_secret=notion_client_secret,
                custom_settings=custom_settings,
            )
        ],
    )
    app.add_routes([
        web.get(f'{base_path}/{redirect_path}', auth_view_cls),
    ])
    return app


def make_app_from_config(config: AppConfiguration) -> web.Application:
    if config.notion_client_id:
        notion_client_id = config.notion_client_id
    else:
        notion_client_id = os.environ[config.notion_client_id_key]

    if config.notion_client_secret:
        notion_client_secret = config.notion_client_secret
    else:
        notion_client_secret = os.environ[config.notion_client_secret_key]

    consumer = get_consumer(config.consumer_name, custom_settings=config.custom_settings)

    return make_app(
        consumer=consumer,
        auth_view_cls=get_auth_view_cls(config.auth_view_name),
        notion_client_id=notion_client_id,
        notion_client_secret=notion_client_secret,
        base_path=config.base_path,
        redirect_path=config.redirect_path,
        custom_settings=config.custom_settings,
    )


def make_app_from_file(filename: Optional[str] = None) -> web.Application:
    if not filename:
        filename = os.environ.get('NOTION_OAUTH_HANDLER_CONFIG', 'notion-oauth-handler.ini')
    assert filename is not None
    config = load_config_from_file(filename)
    return make_app_from_config(config=config)


async def make_app_from_file_async(filename: Optional[str] = None) -> web.Application:
    return make_app_from_file(filename)
