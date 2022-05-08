import logging
import uuid

from aiohttp import web


_LOGGER = logging.getLogger(__name__)


class MockTokenView(web.View):
    async def get(self) -> web.Response:
        # TODO: Implement me
        _LOGGER.info('Mock: accepted token request')
        return web.json_response({
            'access_token': str(uuid.uuid4()),
            'workspace_id': str(uuid.uuid4()),
            'workspace_name': str(uuid.uuid4()),
            'workspace_icon': f'http://{uuid.uuid4()}.png',
            'bot_id': str(uuid.uuid4()),
            'owner': {},
        })


def make_mock_app() -> web.Application:
    app = web.Application(
        middlewares=[],
    )
    app.add_routes([
        web.get('/v1/oauth/token', MockTokenView),
    ])
    return app
