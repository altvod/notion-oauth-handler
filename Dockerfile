FROM python:3.10.0-buster

COPY . /code/

RUN pip install -e /code
ENTRYPOINT ["notion-oauth-handler"]
CMD ["serve", "--host", "0.0.0.0", "--port", "80"]
