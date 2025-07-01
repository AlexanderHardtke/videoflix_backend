# syntax=docker/dockerfile:1 <-- Bei manchen Systemen muss diese Zeile weg

FROM python:3.13.5-bookworm


RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY src/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8000