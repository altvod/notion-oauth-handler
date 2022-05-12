"""
[server]
base_path =
redirect_path = /auth_redirect

[notion]
client_id = ...
client_secret = ...

[handler]
consumer = dummy
auth_view = default
"""

import configparser

import attr


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class AppConfiguration:
    consumer_name: str
    auth_view_name: str
    notion_client_id: str = ''
    notion_client_id_key: str = ''
    notion_client_secret: str = ''
    notion_client_secret_key: str = ''
    base_path: str = ''
    redirect_path: str = '/auth_redirect'


def load_config_from_file(filename: str) -> AppConfiguration:
    config = configparser.ConfigParser()
    config.read(filename)
    return AppConfiguration(
        consumer_name=config['handler'].get('consumer', 'dummy'),
        auth_view_name=config['handler'].get('auth_view', 'default'),
        notion_client_id=config['notion'].get('client_id', ''),
        notion_client_id_key=config['notion'].get('client_id_key', ''),
        notion_client_secret=config['notion'].get('client_secret', ''),
        notion_client_secret_key=config['notion'].get('client_secret_key', ''),
        base_path=config['server'].get('base_path', ''),
        redirect_path=config['server'].get('redirect_path', '/auth_redirect'),
    )
