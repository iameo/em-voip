#syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

WORKDIR /stage

ADD . /stage

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python3", "server.py"]