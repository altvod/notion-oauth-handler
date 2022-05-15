import logging
from http import HTTPStatus
from typing import Type

from aiohttp.web import View, Response

from notion_oauth_handler.server.config import DocumentConfig


_LOGGER = logging.getLogger(__name__)


class DocumentView(View):
    doc_config: DocumentConfig

    @property
    def doc_filename(self) -> str:
        return self.doc_config.filename

    @property
    def doc_content_type(self) -> str:
        return self.doc_config.content_type

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


def document_view_factory(document_config: DocumentConfig) -> Type[DocumentView]:
    class CustomDocumentView(DocumentView):
        doc_config = document_config

    return CustomDocumentView
