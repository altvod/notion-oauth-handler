import abc
from typing import Generic, TypeVar

from notion_oauth_handler.core.dto import AuthRedirectInfo, TokenResponseInfo


_STATE_TV = TypeVar('_STATE_TV')


class NotionOAuthConsumer(abc.ABC, Generic[_STATE_TV]):
    """
    Class for application-specific implementation of the oauth handling process.

    Requires the implementation of two methods in subclasses:
    - consume_redirect_info
    - consume_token_info

    and, optionally:
    - consume_redirect_error
    """

    async def consume_redirect_error(self, error: str) -> None:
        pass

    @abc.abstractmethod
    async def consume_redirect_info(self, redirect_info: AuthRedirectInfo) -> _STATE_TV:
        raise NotImplementedError

    @abc.abstractmethod
    async def consume_token_info(self, token_info: TokenResponseInfo, state_info: _STATE_TV) -> None:
        raise NotImplementedError


class DefaultNotionOAuthConsumer(NotionOAuthConsumer[AuthRedirectInfo]):
    """
    Default half-implementation; uses `AuthRedirectInfo` as state_info.
    Does not require re-implementation of `consume_redirect_info`
    in subclasses.
    """

    async def consume_redirect_info(self, redirect_info: AuthRedirectInfo) -> AuthRedirectInfo:
        return redirect_info

    @abc.abstractmethod
    async def consume_token_info(self, token_info: TokenResponseInfo, state_info: AuthRedirectInfo) -> None:
        raise NotImplementedError


class DummyNotionOAuthConsumer(DefaultNotionOAuthConsumer):
    async def consume_token_info(self, token_info: TokenResponseInfo, state_info: AuthRedirectInfo) -> None:
        print(f'Consumed token info: {token_info}')
