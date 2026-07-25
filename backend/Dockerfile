FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD alembic upgrade head && \
    python -c "import asyncio; from app.seed import seed_demo_data; from app.core.database import async_session_factory; asyncio.run(seed_demo_data(async_session_factory()))" && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
