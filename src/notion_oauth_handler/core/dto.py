from typing import Any

import attr


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class AuthRedirectInfo:
    redirect_uri: str
    code: str
    state: str


@attr.s(frozen=True, auto_attribs=True, kw_only=True)
class TokenResponseInfo:
    access_token: str
    workspace_id: str
    workspace_name: str
    workspace_icon: str
    bot_id: str
    owner: dict[str, Any]
