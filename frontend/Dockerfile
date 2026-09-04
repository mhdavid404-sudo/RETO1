# frontend/Dockerfile
#
# Multi-stage: build de Vite en la etapa "build" (Node), servido por
# Nginx en la etapa final (docs/DECISIONES.md). Contexto de build =
# frontend/ (no la raiz del repo, a diferencia de los 9
# microservicios): el frontend no depende de shared/, es un proyecto
# Node autonomo.
#
# VITE_API_BASE_URL es build-time — Vite la hornea en el bundle de JS
# al compilar, no se lee en runtime dentro del contenedor. Se recibe
# como build arg, no como variable de entorno del contenedor en
# ejecucion (ver docker-compose.yml).

FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
