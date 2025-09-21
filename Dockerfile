FROM python:3.10.8-slim-buster

RUN apt update && apt upgrade -y
RUN apt install git -y

COPY requirements.txt /requirements.txt
RUN pip3 install -U pip && pip3 install -U -r /requirements.txt

RUN mkdir /VJ-FILTER-BOT
WORKDIR /VJ-FILTER-BOT
COPY . /VJ-FILTER-BOT

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
