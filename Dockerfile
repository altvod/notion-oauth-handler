FROM python:3.10.0-buster

COPY . /code/

RUN pip install -e /code
ENTRYPOINT notion-oauth-handler
