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
/privacy = text/html; docs/privacy_policy.html
/terms = text/html; docs/terms_of_use.html

[my_application]
# Your custom application settings go here
"""

import configparser

import attr

import notion_oauth_handler as package


@attr.s(frozen=True)
class DocumentConfig:
    filename: str = attr.ib(kw_only=True)
    content_type: str = attr.ib(kw_only=True)


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
    documents: dict[str, DocumentConfig] = attr.ib(kw_only=True, default='text/plain')
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

    documents: dict[str, DocumentConfig] = {}
    if config.has_section(f'{package_name}.documents'):
        documents_section = config[f'{package_name}.documents']
        documents = {
            server_path: DocumentConfig(
                content_type=file_spec.split(';')[0].strip(),
                filename=file_spec.split(';')[1].strip(),
            )
            for server_path, file_spec in documents_section.items()
        }

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
        documents=documents,
        custom_settings=custom_settings,
    )
