from importlib import metadata
from typing import Any, Type, cast

import notion_oauth_handler as package
from notion_oauth_handler.core.consumer import NotionOAuthConsumer
from notion_oauth_handler.server.view import NotionOAuthRedirectView


CONSUMER_ENTRYPOINT_NAME = f'{package.__name__}.consumer'
AUTH_VIEW_ENTRYPOINT_NAME = f'{package.__name__}.auth_view'


def list_entrypoint_item_names(entrypoint_name: str) -> list[str]:
    entrypoints = metadata.entry_points()[entrypoint_name]
    return [ep.name for ep in entrypoints]


def _get_entrypoint(entrypoint_name: str, item_name: str) -> Any:
    entrypoints = metadata.entry_points()[entrypoint_name]
    ep_item = next(
        iter(ep for ep in entrypoints if ep.name == item_name)
    ).load()
    return ep_item


def get_consumer(consumer_name: str) -> NotionOAuthConsumer:
    consumer_cls = cast(
        Type[NotionOAuthConsumer],
        _get_entrypoint(entrypoint_name=CONSUMER_ENTRYPOINT_NAME, item_name=consumer_name),
    )
    consumer = consumer_cls()
    return consumer


def get_auth_view_cls(auth_view_name: str) -> Type[NotionOAuthRedirectView]:
    auth_view_cls = cast(
        Type[NotionOAuthRedirectView],
        _get_entrypoint(entrypoint_name=AUTH_VIEW_ENTRYPOINT_NAME, item_name=auth_view_name),
    )
    return auth_view_cls
