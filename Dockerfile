FROM python:3.9-slim

WORKDIR /secretbot

RUN pip install aiogram pandas

COPY main.py .

ARG TOKEN
ENV TOKEN=${TOKEN}

ARG URL_PHOTO
ENV URL_PHOTO=${URL_PHOTO}

CMD [ "python", "main.py" ]
