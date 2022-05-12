"""
[main]
consumer = dummy
auth_view = default
custom_section = my_application

[server]
base_path =
redirect_path = /auth_redirect

[notion]
client_id = ...
client_secret = ...

[my_application]
# Your custom application settings go here
"""

import configparser

import attr


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

    custom_settings = {}
    main_section = config['main']
    if main_section.get('custom_section'):
        custom_section_name = main_section['custom_section']
        custom_settings = config[custom_section_name]

    return AppConfiguration(
        consumer_name=main_section.get('consumer', 'dummy'),
        auth_view_name=main_section.get('auth_view', 'default'),
        notion_client_id=config['notion'].get('client_id', ''),
        notion_client_id_key=config['notion'].get('client_id_key', ''),
        notion_client_secret=config['notion'].get('client_secret', ''),
        notion_client_secret_key=config['notion'].get('client_secret_key', ''),
        base_path=config['server'].get('base_path', ''),
        redirect_path=config['server'].get('redirect_path', '/auth_redirect'),
        custom_settings=custom_settings,
    )
