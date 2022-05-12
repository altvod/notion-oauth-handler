import os
from typing import Optional, Type

from aiohttp import web

from notion_oauth_handler.core.consumer import NotionOAuthConsumer
from notion_oauth_handler.server.auth_view import NotionOAuthRedirectView
from notion_oauth_handler.server.document_view import PrivacyView, TermsView
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
        auth_path: str = '/auth',
        privacy_path: str = '/privacy',
        terms_path: str = '/terms',
        privacy_filename: Optional[str] = None,
        privacy_content_type: str = 'text/plain',
        terms_filename: Optional[str] = None,
        terms_content_type: str = 'text/plain',
        custom_settings: dict,
) -> web.Application:
    """
    Create Notion OAuth handling server (aiohttp Application)
    """

    base_path = base_path.rstrip('/')
    auth_path = auth_path.lstrip('/')
    privacy_path = privacy_path.lstrip('/')
    terms_path = terms_path.lstrip('/')

    app = web.Application(
        middlewares=[
            notion_oauth_middleware_factory(
                consumer=consumer,
                notion_client_id=notion_client_id,
                notion_client_secret=notion_client_secret,
                privacy_filename=privacy_filename,
                privacy_content_type=privacy_content_type,
                terms_filename=terms_filename,
                terms_content_type=terms_content_type,
                custom_settings=custom_settings,
            )
        ],
    )
    app.add_routes([
        web.get(f'{base_path}/{auth_path}', auth_view_cls),
    ])
    if privacy_filename is not None:
        app.add_routes([web.get(f'{base_path}/{privacy_path}', PrivacyView)])
    if terms_filename is not None:
        app.add_routes([web.get(f'{base_path}/{terms_path}', TermsView)])

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
        auth_path=config.auth_path,
        privacy_path=config.privacy_path,
        terms_path=config.terms_path,
        privacy_filename=config.privacy_filename,
        privacy_content_type=config.privacy_content_type,
        terms_filename=config.terms_filename,
        terms_content_type=config.terms_content_type,
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
