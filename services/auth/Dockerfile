# services/auth/Dockerfile — contexto de build: raiz del repo.
FROM python:3.13-slim

WORKDIR /app

COPY services/auth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY shared/ /app/shared
COPY services/auth/ /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
