FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080
COPY start.sh /start.sh
RUN chmod +x /start.sh
CMD ["./start.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
