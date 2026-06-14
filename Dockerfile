# Container image for running the FastAPI demo service.
FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies before copying the full source for better layer caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Uvicorn serves both the API and the static demo frontend.
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
