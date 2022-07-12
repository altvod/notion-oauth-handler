# notion-oauth-handler
Python server/handler of Notion's OAuth 2 for public integrations

Provides:
- basic code for handling OAuth in Notion;
- a configurable HTTP server that can be extended by plugging in custom application code via Python entrypoints;
- a [boilerplate](boilerplate) to be used as a starting point for your integration.

## Prerequisites

1. First of all you will need to create a public integration in Notion
   and save its ID and secret key.
2. Notion OAuth requires an HTTPS URL. 
   This means you will need to register a domain name
   and create a valid certificate for it.
   There is no way to fully test it using `127.0.0.1:8000`!


## Usage

There is a wide range of different ways you can use `notion-oauth-handler`
in your project, but we'll cover just the two main options here.

### As a standalone server

To integrate `notion-oauth-handler` into your app you will need to do the following:
- implement a "consumer" class (by subclassing `NotionOAuthConsumer` or its existing subclasses)
  that will accept user tokens and save them somewhere in your app (e.g. in a database)
- define custom methods for the main web server view (subclass of `NotionOAuthRedirectView`)
- add entrypoints for these classes to your python package
- define your `notion-oauth-handler` configuration
- run your web server

See the corresponding sections below for mnore in-depth descriptions


### As part of an existing `aiohttp` application

In this case you will still need to:
- define the consumer and view classes
- and register them as package entrypoints
from the above description, but plugging the handler into your app is
entirely up to you.

See [make_app in the default app module](src/notion_oauth_handler/server/app.py)


### Consumer class

This class defines how the authentication info is handled (e.g. saved to a database).
You can also add some external API hooks here.
This is the place to define any actions that need to be taken
when a user grants access to your public integration.

```python
from notion_oauth_handler.core.dto import AuthRedirectInfo, TokenResponseInfo
from notion_oauth_handler.core.consumer import DefaultNotionOAuthConsumer


class MyAppNotionOAuthConsumer(DefaultNotionOAuthConsumer):

    async def consume_redirect_error(self, error_text: str) -> None:
        # Optional.
        # What to do if an error has been raised.
        # Log it, call an API hook, whatever.
        pass

    async def consume_token_info(self, token_info: TokenResponseInfo, state_info: AuthRedirectInfo) -> None:
        # Required.
        # The main logic goes here.
        # `token_info` contains the user access token received from Notion
        # while `state_info.state` is the data intially passed to Notion in the URL
        # (e.g. it may contain a user or app ID or something like that)
        pass
```

For a bit more flexibility you can use the parent class, `NotionOAuthConsumer`,
and redefine some more of its methods.

### Web view class

In the basic scenario, you only need to define the server's responses,
without any token-handling logic here.

```python
from http import HTTPStatus
from aiohttp.web import Response
from notion_oauth_handler.core.dto import TokenResponseInfo
from notion_oauth_handler.server.auth_view import DefaultNotionOAuthRedirectView


class MyAppNotionOAuthRedirectView(DefaultNotionOAuthRedirectView):

    async def make_access_denied_response(self, error_text: str) -> Response:
        return self.make_response(text='MyApp says: Error', status=HTTPStatus.FORBIDDEN)

    async def make_auth_response(self, token_info: TokenResponseInfo) -> Response:
        return self.make_response(text='MyApp says: OK', status=HTTPStatus.OK)
```

One possibility is to generate a redirect or link back to your main app here.
Whether to return HTML, JSON or plain  text here is completely up to you.

Try to stick to the idea that there should be any complex business logic
for token handling here - all that should go into your consumer class.

### Registering entrypoints

Once you've defined all the logic in the classes above,
you need to make them available for `notion-auth-handler`
by declaring them as entrypoints in your Python project configuration

If you are using a `setup.cfg` file for all your settings,
then it will look like this:
```ini
[options.entry_points]
# Your app-specific entrypoints (if any)
# ...

# Notion OAuth entrypoints
notion_oauth_handler.consumer =
    my_app = my_app.web.notion_auth.consumer:MyAppNotionOAuthConsumer
notion_oauth_handler.auth_view =
    my_app = my_app.web.notion_auth.view:MyAppNotionOAuthRedirectView
```

And for a `setup.py` file, like this:
```python
from setuptools import setup

setup(
    # Your project settings
    # ...

    entry_points={
        'notion_oauth_handler.consumer': [
            'my_app = my_app.web.notion_auth.consumer:MyAppNotionOAuthConsumer',
        ],
        'notion_oauth_handler.auth_view': [
            'my_app = my_app.web.notion_auth.view:MyAppNotionOAuthRedirectView',
        ],
    },
)
```

where `my_app.web.notion_auth.consumer:MyAppNotionOAuthConsumer` and
`my_app.web.notion_auth.view:MyAppNotionOAuthRedirectView` indicate
where to find these classes in your code.


### Configuration file

Now you need to tell `notion-auth-handler`, which of the possibly many
implementation entrypoints to call, which url paths to use in the server,
how to connect to your Notion integration, etc.
This is done via a configuration file.

See [the boilerplate config file](boilerplate/notion-oauth-handler.ini)
for all the options.

Note that all public Notion integrations are required to have "Terms of Use"
and "Privacy Policy" documents.
Since using the standalone server mode assumes that you don't have another
web server, `notion-auth-handler` can host these documents for you.
See the `[notion_oauth_handler.documents]` section of the example configuration file.

### Web server

`notion-oauth-handler` can run in practically any setup,
but a sample `Gunicorn` [configuratuon file](boilerplate/gunicorn.conf.py)
is included just for convenience.
