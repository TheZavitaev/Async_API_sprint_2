FROM python:3.9-slim

WORKDIR /api

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBIAN_FRONTEND noninteractive

RUN set -xe; \
    apt-get update -yqq && \
    apt-get upgrade -yqq && \
    apt-get install -yqq netcat

# Clean up
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY requirements.txt /api/

# install python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /api/

CMD ["python", "/api/main.py"]