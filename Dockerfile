FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENV STREAMLIT_PORT=8501
ENV PYTHONUNBUFFERED=1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false", "--server.headless=true"]
