"""
[notion_oauth_handler]
consumer = dummy
auth_view = default
custom_section = my_application

[notion_oauth_handler.server]
base_path =
redirect_path = /auth_redirect

[notion_oauth_handler.notion]
client_id = ...
# or notion_client_id_key = ...
client_secret = ...
# or notion_client_secret_key = ...

[my_application]
# Your custom application settings go here
"""

import configparser

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
    redirect_path: str = attr.ib(kw_only=True, default='/auth_redirect')
    custom_settings: dict = attr.ib(kw_only=True, factory=dict)


def load_config_from_file(filename: str) -> AppConfiguration:
    config = configparser.ConfigParser()
    config.read(filename)
    package_name = package.__name__

    custom_settings = {}
    main_section = config[package_name]
    if main_section.get('custom_section'):
        custom_section_name = main_section['custom_section']
        custom_settings = config[custom_section_name]

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
        redirect_path=server_section.get('redirect_path', '/auth_redirect'),
        custom_settings=custom_settings,
    )
