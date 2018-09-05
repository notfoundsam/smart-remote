FROM python:2

RUN mkdir /app
WORKDIR /app

RUN pip install -U pip
RUN pip install -U setuptools
RUN pip install -U wheel

COPY requirements.txt ./
RUN pip install -r requirements.txt
