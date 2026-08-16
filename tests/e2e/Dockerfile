FROM mcr.microsoft.com/playwright/python:v1.60.0-noble

# ffmpeg: Playwright ships a stripped build (no concat), and we need a full one
# to prepend the title card and append the result card to recorded videos.
# libpq5: runtime library required by psycopg to reach PostgreSQL.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements-test.txt /app/
RUN pip install --no-cache-dir -r requirements.txt -r requirements-test.txt

COPY . /app/
