# Container image for running the FastAPI demo service.
FROM python:3.11-slim

WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ARG PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn

# Install Python dependencies before copying the full source for better layer caching.
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir --retries 5 --timeout 120 \
        -i ${PIP_INDEX_URL} \
        --trusted-host ${PIP_TRUSTED_HOST} \
        -r requirements.txt

COPY . .

# Uvicorn serves both the API and the static demo frontend.
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
