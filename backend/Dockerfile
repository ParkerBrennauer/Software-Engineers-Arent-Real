FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY src ./src

RUN adduser --uid 5678 --disabled-password --gecos "" appuser \
    && mkdir -p /app/src/data \
    && chown -R 5678:5678 /app/src \
    && chmod -R 666 /app/src/data

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
