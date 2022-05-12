import abc
import logging
from http import HTTPStatus
from typing import ClassVar

from aiohttp.web import View, Response
from aiohttp.typedefs import LooseHeaders

import notion_oauth_handler.core.exc as exc
from notion_oauth_handler.core.dto import AuthRedirectInfo, TokenResponseInfo
from notion_oauth_handler.core.oauth_handler import NotionOAuthHandler
from notion_oauth_handler.server.middleware import (
    DOC_PRIVACY_REQUEST_KEY, DOC_TERMS_REQUEST_KEY,
)


_LOGGER = logging.getLogger(__name__)


class DocumentView(View):
    doc_info_key: ClassVar[str]

    @property
    def doc_filename(self) -> str:
        doc_info_key = self.request[self.doc_info_key]
        assert isinstance(doc_info_key, tuple)
        return doc_info_key[0]

    @property
    def doc_content_type(self) -> str:
        doc_info_key = self.request[self.doc_info_key]
        assert isinstance(doc_info_key, tuple)
        return doc_info_key[1]

    def get_doc_body(self) -> str:
        with open(self.doc_filename) as doc_file:
            return doc_file.read()

    async def get(self) -> Response:
        doc_body = self.get_doc_body()
        return Response(
            status=HTTPStatus.OK,
            body=doc_body,
            content_type=self.doc_content_type,
        )


class PrivacyView(DocumentView):
    doc_info_key = DOC_PRIVACY_REQUEST_KEY


class TermsView(DocumentView):
    doc_info_key = DOC_TERMS_REQUEST_KEY
