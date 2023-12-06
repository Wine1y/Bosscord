FROM python:3.10.11

WORKDIR /app

COPY ./bot /app/bot
COPY ./configs /app/configs
COPY ./core /app/core
COPY ./db /app/db
COPY ./logic /app/logic

COPY requirements.txt /app
COPY config.json /app
COPY main.py /app

RUN pip install -r requirements.txt

CMD python main.py