from http import HTTPStatus

from aiohttp.web import Response

from notion_oauth_handler.core.dto import AuthRedirectInfo, TokenResponseInfo
from notion_oauth_handler.core.consumer import DefaultNotionOAuthConsumer
from notion_oauth_handler.server.auth_view import DefaultNotionOAuthRedirectView


class MyAppNotionOAuthConsumer(DefaultNotionOAuthConsumer):
    """
    Define how the authentication info is handled,
    where it is saved, etc.
    """

    async def _connect_to_database(self) -> None:  # Not a mandatory method - just as an example
        # Connect somewhere or something
        print(f'MyApp settings: {self.custom_settings}')
        # return something here?

    async def consume_token_info(self, token_info: TokenResponseInfo, state_info: AuthRedirectInfo) -> None:
        """
        Mandatory method - this is where all the main logic is located.

        - retrieve state info from `state_info`
        - save `access_token` to database
        """

        await self._connect_to_database()  # maybe?
        # Do something


class MyAppNotionOAuthRedirectView(DefaultNotionOAuthRedirectView):
    """Customize the HTTP responses"""

    async def make_access_denied_response(self, error_text: str) -> Response:
        """
        Define how the server should respond if access was not granted
        (the user decided to cancel).
        Can access `self.custom_settings` to build a custom response here.
        """

        return self.make_response(text='MyApp says: Error', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        """
        Define how the server should respond if access was granted successfully.
        Can access `self.custom_settings` to build a custom response here.
        """

        # Maybe redirect or provide a link to another page here
        return self.make_response(text='MyApp says: OK', status=HTTPStatus.OK)
