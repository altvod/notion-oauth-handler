# Main Gunicorn configuration

wsgi_app = 'notion_oauth_handler.server.app:make_app_from_file_async'
bind = '0.0.0.0:443'
workers = 1
worker_class = 'aiohttp.GunicornWebWorker'
# HTTPS
certfile = '/ssl-certs/fullchain.pem'
keyfile = '/ssl-certs/privkey.pem'
