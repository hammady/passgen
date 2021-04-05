FROM python:3.9
LABEL maintainer="Hossam Hammady <github@hammady.net>"

WORKDIR /home

RUN apt update && \
    apt install -y swig

RUN pip install --upgrade pip
COPY requirements.txt /home
RUN pip install -r requirements.txt
