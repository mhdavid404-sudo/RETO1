# services/startups/create/Dockerfile
#
# Contexto de build: la raiz del repo (no esta carpeta), para poder
# copiar shared/ ademas del codigo propio del servicio. En
# docker-compose.yml, build.context = "." y build.dockerfile apunta aqui.

FROM python:3.13-slim

WORKDIR /app

# Dependencias primero, para aprovechar la cache de capas de Docker: si
# solo cambia el codigo (main.py/schemas.py) no hace falta reinstalar
# nada en el siguiente build.
COPY services/startups/create/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# shared/ se copia igual en los 9 servicios (brief, seccion 4).
COPY shared/ /app/shared
COPY services/startups/create/ /app/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
