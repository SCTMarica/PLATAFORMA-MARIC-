FROM mcr.microsoft.com/playwright/python:v1.60.0-noble

WORKDIR /app

COPY requirements.txt requirements-test.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

COPY . /app/
