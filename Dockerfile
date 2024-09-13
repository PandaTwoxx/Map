# syntax=docker/dockerfile:1
FROM python:3.12-alpine

WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
EXPOSE 3306
COPY . .
CMD ["python3", "manage.py", "run"]