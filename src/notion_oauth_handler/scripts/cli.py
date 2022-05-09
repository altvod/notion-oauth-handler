import argparse
import asyncio
import json
import logging
import os
from importlib import metadata
from typing import Any

from aiohttp import web

import notion_oauth_handler as package
from notion_oauth_handler.core.dto import TokenResponseInfo
from notion_oauth_handler.server.app import make_app_from_config, make_app_from_file
from notion_oauth_handler.server.config import AppConfiguration
from notion_oauth_handler.mock.app import make_mock_app


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser('Notion OAuth Handler Server')
    subparsers = parser.add_subparsers(title='command', dest='command')

    response_factory_arg_parser = argparse.ArgumentParser(add_help=False)
    response_factory_arg_parser.add_argument(
        '--response-factory', default='dummy',
        help='Response factory class entrypoint name',
    )

    host_port_arg_parser = argparse.ArgumentParser(add_help=False)
    host_port_arg_parser.add_argument('--host', default='0.0.0.0', help='Server host')
    host_port_arg_parser.add_argument('--port', default='8000', type=int, help='Server port')

    serve_cmd_parser = subparsers.add_parser(
        'serve', help='Run HTTP server',
        parents=[response_factory_arg_parser, host_port_arg_parser]
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

    response_factory_cmd_parser = subparsers.add_parser('response_factory', help='Response factory information')
    response_factory_cmd_subparsers = response_factory_cmd_parser.add_subparsers(
        title='response_factory_command', dest='response_factory_command')
    response_factory_cmd_subparsers.add_parser('list', help='List available response factories')

    response_cmd_parser = subparsers.add_parser(
        'response', help='Generate server response', parents=[response_factory_arg_parser]
    )
    response_cmd_subparsers = response_cmd_parser.add_subparsers(
        title='response_command', dest='response_command')

    response_auth_cmd_parser = response_cmd_subparsers.add_parser(
        'auth', help='Generate successful auth response')
    response_auth_cmd_parser.add_argument('--access-token', default='<access_token>', help='access_token value')
    response_auth_cmd_parser.add_argument('--workspace-id', default='<workspace_id>', help='workspace_id value')
    response_auth_cmd_parser.add_argument('--workspace-name', default='My Workspace', help='workspace_name value')
    response_auth_cmd_parser.add_argument('--workspace-icon', default='workspace.icon', help='workspace_icon value')
    response_auth_cmd_parser.add_argument('--bot-id', default='<bot_id>', help='bot_id value')
    response_auth_cmd_parser.add_argument('--owner', default='{}', help='owner value')

    response_error_cmd_parser = response_cmd_subparsers.add_parser(
        'error', help='Generate auth error response')
    response_error_cmd_parser.add_argument('--error', default='Error text', help='error value')

    return parser


class NotionOAuthTool:
    @classmethod
    @property
    def _consumer_entrypoint_key(cls) -> str:
        return f'{package.__name__}.consumer'

    @classmethod
    @property
    def _response_factory_entrypoint_key(cls) -> str:
        return f'{package.__name__}.response_factory'

    @classmethod
    def consumer_list(cls) -> None:
        entrypoints = metadata.entry_points()[cls._consumer_entrypoint_key]
        for ep in entrypoints:
            print(ep.name)

    @classmethod
    def response_factory_list(cls) -> None:
        entrypoints = metadata.entry_points()[cls._response_factory_entrypoint_key]
        for ep in entrypoints:
            print(ep.name)

    @classmethod
    def serve(
            cls,
            config_file: str,
            notion_client_id_key: str, notion_client_secret_key: str,
            consumer_name: str, response_factory_name: str,
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
                    response_factory_name=response_factory_name,
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
        print(f'Body:\n{response.body.decode()}')

    @classmethod
    def response_auth(
            cls,
            response_factory_name: str,
            access_token: str,
            workspace_id: str,
            workspace_name: str,
            workspace_icon: str,
            bot_id: str,
            owner: str,
    ) -> None:
        response_factory = cls._get_response_factory(response_factory_name=response_factory_name)
        token_info = TokenResponseInfo(
            access_token=access_token, workspace_id=workspace_id,
            workspace_name=workspace_name, workspace_icon=workspace_icon,
            bot_id=bot_id, owner=json.loads(owner),
        )
        response = asyncio.run(response_factory.make_auth_response(token_info=token_info))
        cls._print_http_response(response)

    @classmethod
    def response_error(
            cls,
            response_factory_name: str,
            error: str,
    ) -> None:
        response_factory = cls._get_response_factory(response_factory_name=response_factory_name)
        response = asyncio.run(response_factory.make_error_response(error=error))
        cls._print_http_response(response)

    @classmethod
    def run(cls, args: Any) -> None:
        if args.command == 'serve':
            cls.serve(
                config_file=args.config_file,
                notion_client_id_key=args.notion_client_id_key,
                notion_client_secret_key=args.notion_client_secret_key,
                consumer_name=args.consumer,
                response_factory_name=args.response_factory,
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
        elif args.command == 'response_factory':
            if args.response_factory_command == 'list':
                cls.response_factory_list()
        elif args.command == 'response':
            if args.response_command == 'auth':
                cls.response_auth(
                    response_factory_name=args.response_factory,
                    access_token=args.access_token,
                    workspace_id=args.workspace_id,
                    workspace_name=args.workspace_name,
                    workspace_icon=args.workspace_icon,
                    bot_id=args.bot_id,
                    owner=args.owner,
                )
            elif args.response_command == 'error':
                cls.response_error(
                    response_factory_name=args.response_factory,
                    error=args.error,
                )


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        handlers=[logging.StreamHandler()],
    )


def run() -> None:
    configure_logging()
    NotionOAuthTool.run(args=get_parser().parse_args())
