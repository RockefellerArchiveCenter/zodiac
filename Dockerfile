FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /code/
ADD celery/scripts/* /etc/init.d/
ADD celery/config* /etc/default/
RUN useradd celery && mkdir /var/log/celery/ && chown -R celery:celery /var/log/celery/
WORKDIR /code/zodiac
