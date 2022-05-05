import base64
from typing import Any, ClassVar

import aiohttp
import attr
import yarl

from notion_oauth_handler.core.exc import NotionAccessDenied
from notion_oauth_handler.core.dto import AuthRedirectInfo, TokenResponseInfo
from notion_oauth_handler.core.consumer import NotionOAuthConsumer


@attr.s
class NotionOAuthHandler:
    """
    Handles Notion OAuth 2
    """

    _default_base_url: ClassVar[str] = ''
    _auth_entrypoint: ClassVar[str] = '/v1/oauth/token'

    _consumer: NotionOAuthConsumer = attr.ib(kw_only=True)
    _client_id: str = attr.ib(kw_only=True)
    _client_secret: str = attr.ib(kw_only=True)
    _base_url: str = attr.ib(kw_only=True)

    @_base_url.default
    def _make_base_url(self) -> str:
        return self._default_base_url

    def _make_token_url(self, redirect_info: AuthRedirectInfo) -> yarl.URL:
        return yarl.URL(self._base_url) / self._auth_entrypoint

    def _make_token_headers(self, redirect_info: AuthRedirectInfo) -> Any:
        return {
            'Authorization': base64.b64encode(f'{self._client_id}:{self._client_secret}'.encode()),
        }

    def _make_token_body(self, redirect_info: AuthRedirectInfo) -> dict:
        return {
            'grant_type': 'authorization_code',
            'code': redirect_info.code,
            'redirect_uri': redirect_info.redirect_uri,
        }

    async def _make_token_request(self, redirect_info: AuthRedirectInfo) -> TokenResponseInfo:
        url = self._make_token_url(redirect_info=redirect_info)
        body = self._make_token_body(redirect_info=redirect_info)
        headers = self._make_token_headers(redirect_info=redirect_info)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=body, headers=headers) as response:
                response_body = await response.json()

        token_info = TokenResponseInfo(
            access_token=response_body['access_token'],
            workspace_id=response_body['workspace_id'],
            workspace_name=response_body['workspace_name'],
            workspace_icon=response_body['workspace_icon'],
            bot_id=response_body['bot_id'],
            owner=response_body['owner'],
        )
        return token_info

    async def handle_auth(self, redirect_info: AuthRedirectInfo):
        if redirect_info.error:
            await self._consumer.consume_redirect_error(redirect_info=redirect_info)
            raise NotionAccessDenied('Notion access was denied')

        state_info = await self._consumer.consume_redirect_info(redirect_info=redirect_info)
        token_info = await self._make_token_request(redirect_info=redirect_info)
        await self._consumer.consume_token_info(token_info=token_info, state_info=state_info)
