# Dockerfile
FROM python:3.9.10-alpine3.14
WORKDIR /srv
RUN apk add --no-cache git
RUN pip install --upgrade pip
COPY . /srv
RUN pip install -r /srv/requirements.txt
CMD ["python","/srv/main.py"]