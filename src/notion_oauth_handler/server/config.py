"""
[notion_oauth_handler]
consumer = dummy
auth_view = default
custom_section = my_application

[notion_oauth_handler.server]
base_path =
auth_path = /auth
privacy_path = /privacy
terms_path = /terms

[notion_oauth_handler.notion]
client_id = ...
# or notion_client_id_key = ...
client_secret = ...
# or notion_client_secret_key = ...

[notion_oauth_handler.documents]
privacy_filename = docs/privacy_policy.html
privacy_content_type = text/html
terms_filename = docs/terms_of_use.html
terms_content_type = text/html

[my_application]
# Your custom application settings go here
"""

import configparser
from typing import Optional

import attr

import notion_oauth_handler as package


@attr.s(frozen=True)
class AppConfiguration:
    consumer_name: str = attr.ib(kw_only=True)
    auth_view_name: str = attr.ib(kw_only=True)
    notion_client_id: str = attr.ib(kw_only=True, default='')
    notion_client_id_key: str = attr.ib(kw_only=True, default='')
    notion_client_secret: str = attr.ib(kw_only=True, default='')
    notion_client_secret_key: str = attr.ib(kw_only=True, default='')
    base_path: str = attr.ib(kw_only=True, default='')
    auth_path: str = attr.ib(kw_only=True, default='/auth')
    privacy_path: str = attr.ib(kw_only=True, default='/privacy')
    terms_path: str = attr.ib(kw_only=True, default='/terms')
    privacy_filename: Optional[str] = attr.ib(kw_only=True, default=None)
    privacy_content_type: str = attr.ib(kw_only=True, default='text/plain')
    terms_filename: Optional[str] = attr.ib(kw_only=True, default=None)
    terms_content_type: str = attr.ib(kw_only=True, default='text/plain')
    custom_settings: dict = attr.ib(kw_only=True, factory=dict)


def load_config_from_file(filename: str) -> AppConfiguration:
    config = configparser.ConfigParser()
    config.read(filename)
    package_name = package.__name__

    custom_settings: dict[str, str] = {}
    main_section = config[package_name]
    if main_section.get('custom_section'):
        custom_section_name = main_section['custom_section']
        custom_settings = dict(config[custom_section_name])

    documents_section = {}
    if config.has_section(f'{package_name}.documents'):
        documents_section = dict(config[f'{package_name}.documents'])

    notion_section = config[f'{package_name}.notion']
    server_section = config[f'{package_name}.server']

    return AppConfiguration(
        consumer_name=main_section.get('consumer', 'dummy'),
        auth_view_name=main_section.get('auth_view', 'default'),
        notion_client_id=notion_section.get('client_id', ''),
        notion_client_id_key=notion_section.get('client_id_key', ''),
        notion_client_secret=notion_section.get('client_secret', ''),
        notion_client_secret_key=notion_section.get('client_secret_key', ''),
        base_path=server_section.get('base_path', ''),
        auth_path=server_section.get('auth_path', '/auth'),
        privacy_path=server_section.get('privacy_path', '/privacy'),
        terms_path=server_section.get('terms_path', '/terms'),
        privacy_filename=documents_section.get('privacy_filename', None),
        privacy_content_type=documents_section.get('privacy_content_type', 'text/plain'),
        terms_filename=documents_section.get('terms_filename', None),
        terms_content_type=documents_section.get('terms_content_type', 'text/plain'),
        custom_settings=custom_settings,
    )
