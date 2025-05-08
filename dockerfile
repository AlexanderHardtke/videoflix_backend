# syntax=docker/dockerfile:1 <-- Bei manchen Systemen muss diese Zeile weg

FROM python:3.13.3-bookworm



WORKDIR /usr/src/app



COPY requirements.txt ./

RUN /usr/local/bin/python -m pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt



COPY . . 
RUN cd ./videoflix_backend
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]