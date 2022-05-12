import argparse
import logging
from typing import Any

from aiohttp import web

from notion_oauth_handler.server.app import make_app_from_config, make_app_from_file
from notion_oauth_handler.server.config import AppConfiguration
from notion_oauth_handler.mock.app import make_mock_app
from notion_oauth_handler.entrypoints import (
    AUTH_VIEW_ENTRYPOINT_NAME, CONSUMER_ENTRYPOINT_NAME,
    list_entrypoint_item_names,
)


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser('Notion OAuth Handler Server')
    subparsers = parser.add_subparsers(title='command', dest='command')

    host_port_arg_parser = argparse.ArgumentParser(add_help=False)
    host_port_arg_parser.add_argument('--host', default='0.0.0.0', help='Server host')
    host_port_arg_parser.add_argument('--port', default='8000', type=int, help='Server port')

    serve_cmd_parser = subparsers.add_parser(
        'serve', help='Run HTTP server',
        parents=[host_port_arg_parser]
    )
    serve_cmd_parser.add_argument(
        '--config-file', default='',
        help='Load configuration from file',
    )
    serve_cmd_parser.add_argument(
        '--notion-client-id-key', default='NOTION_CLIENT_ID',
        help='Name of env var for Notion client ID',
    )
    serve_cmd_parser.add_argument(
        '--notion-client-secret-key', default='NOTION_CLIENT_SECRET',
        help='Name of env var for Notion client sercret',
    )
    serve_cmd_parser.add_argument(
        '--consumer', default='dummy',
        help='Consumer class entrypoint name',
    )
    serve_cmd_parser.add_argument(
        '--auth-view', default='dummy',
        help='Auth view class entrypoint name',
    )
    serve_cmd_parser.add_argument(
        '--base-path', default='', help='Base path for all endpoints')
    serve_cmd_parser.add_argument(
        '--redirect-path', default='/auth_redirect', help='Path of redirect endpoint')

    subparsers.add_parser(
        'mock', help='Run Notion mock server',
        parents=[host_port_arg_parser]
    )

    consumer_cmd_parser = subparsers.add_parser('consumer', help='Consumer information')
    consumer_cmd_subparsers = consumer_cmd_parser.add_subparsers(
        title='consumer_command', dest='consumer_command')
    consumer_cmd_subparsers.add_parser('list', help='List available consumers')

    auth_view_cmd_parser = subparsers.add_parser('auth_view', help='Auth view information')
    auth_view_cmd_subparsers = auth_view_cmd_parser.add_subparsers(
        title='auth_view_command', dest='auth_view_command')
    auth_view_cmd_subparsers.add_parser('list', help='List available auth views')

    return parser


class NotionOAuthTool:
    @classmethod
    def consumer_list(cls) -> None:
        for item_name in list_entrypoint_item_names(CONSUMER_ENTRYPOINT_NAME):
            print(item_name)

    @classmethod
    def auth_view_list(cls) -> None:
        for item_name in list_entrypoint_item_names(AUTH_VIEW_ENTRYPOINT_NAME):
            print(item_name)

    @classmethod
    def serve(
            cls,
            config_file: str,
            notion_client_id_key: str, notion_client_secret_key: str,
            consumer_name: str, auth_view_name: str,
            host: str, port: int,
            base_path: str, redirect_path: str,
    ) -> None:
        if config_file:
            app = make_app_from_file(
                filename=config_file,
            )
        else:
            app = make_app_from_config(
                config=AppConfiguration(
                    consumer_name=consumer_name,
                    auth_view_name=auth_view_name,
                    notion_client_id_key=notion_client_id_key,
                    notion_client_secret_key=notion_client_secret_key,
                    base_path=base_path,
                    redirect_path=redirect_path,
                )
            )
        web.run_app(app, host=host, port=port)

    @classmethod
    def mock(cls, host: str, port: int) -> None:
        app = make_mock_app()
        web.run_app(app, host=host, port=port)

    @classmethod
    def _print_http_response(cls, response: web.Response) -> None:
        print(f'Status: {response.status}')
        print(f'Headers:')
        for header_name, header_value in response.headers.items():
            print(f'    {header_name}: {header_value}')
        if isinstance(response.body, bytes):
            print(f'Body:\n{response.body.decode()}')

    @classmethod
    def run(cls, args: Any) -> None:
        if args.command == 'serve':
            cls.serve(
                config_file=args.config_file,
                notion_client_id_key=args.notion_client_id_key,
                notion_client_secret_key=args.notion_client_secret_key,
                consumer_name=args.consumer,
                auth_view_name=args.auth_view,
                host=args.host,
                port=args.port,
                base_path=args.base_path,
                redirect_path=args.redirect_path,
            )
        elif args.command == 'mock':
            cls.mock(host=args.host, port=args.port)
        elif args.command == 'consumer':
            if args.consumer_command == 'list':
                cls.consumer_list()
        elif args.command == 'auth_view':
            if args.auth_view_command == 'list':
                cls.auth_view_list()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
    )


def run() -> None:
    configure_logging()
    NotionOAuthTool.run(args=get_parser().parse_args())
