FROM python:3.10-slim

WORKDIR /

# PostgreSQL istemcisi yükleyelim
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# RUN FAKE DB SEEDS İÇİN

CMD ["bash", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
