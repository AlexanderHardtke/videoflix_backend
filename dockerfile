# syntax=docker/dockerfile:1 <-- Bei manchen Systemen muss diese Zeile weg

FROM python:3.13.5-bookworm


RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

COPY src/requirements.txt ./

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt



COPY src/ . 
RUN cd ./videoflix_backend
EXPOSE 8000
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]