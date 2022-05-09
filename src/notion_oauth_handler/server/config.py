"""
[server]
base_path =
redirect_path = /auth_redirect

[notion]
client_id = ...
client_secret = ...

[handler]
consumer = dummy
response_factory = dummy
"""

import configparser

import attr


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class AppConfiguration:
    consumer_name: str
    response_factory_name: str
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
        response_factory_name=config['handler'].get('response_factory', 'dummy'),
        notion_client_id=config['notion'].get('client_id', ''),
        notion_client_id_key=config['notion'].get('client_id', ''),
        notion_client_secret=config['notion'].get('client_secret', ''),
        notion_client_secret_key=config['notion'].get('client_secret', ''),
        base_path=config['server'].get('base_path', ''),
        redirect_path=config['server'].get('redirect_path', '/auth_redirect'),
    )
