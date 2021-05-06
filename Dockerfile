# syntax=docker/dockerfile:1

FROM python:3.8.5-slim-buster

WORKDIR /src

COPY src/requirements.txt src/requirements.txt

RUN pip3 install -r src/requirements.txt

WORKDIR /

COPY . .

WORKDIR /src
EXPOSE 5000
CMD [ "python3", "app.py", "--host=0.0.0.0"]