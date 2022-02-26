FROM python:3.10

ENV PYTHONUNBUFFERED 1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip install supervisor
COPY . /code/
COPY supervisor/ /etc/
RUN useradd celery && \
    mkdir /var/log/celery/ /var/log/supervisor/ /var/run/supervisor/ && \
    chown -R celery:celery /var/log/celery/
