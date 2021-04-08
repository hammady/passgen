FROM python:3.9
LABEL maintainer="Hossam Hammady <github@hammady.net>"

WORKDIR /home

RUN apt update && \
    apt install -y swig

RUN pip install --upgrade pip
COPY requirements-prod.txt /home/requirements.txt
RUN pip install -r requirements.txt

COPY / /home/

CMD [ \
    "gunicorn", \
    "--worker-class", \
    "gevent", \
    "wsgi:app", \
    "--max-requests", \
    "10000", \
    "--timeout", \
    "5", \
    "--keep-alive", \
    "5", \
    "--log-level", \
    "info" \
]

EXPOSE 3000
