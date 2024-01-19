FROM python:3.11

WORKDIR /de/backend

COPY ./requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .

ENV DB_NAME='auctionMaster'
ENV DB_USER='auctionMaster'
ENV DB_PASSWORD='auctionMaster'
ENV DB_HOST='db'
ENV DB_PORT='5432'
