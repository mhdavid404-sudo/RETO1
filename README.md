# 🚀 RETO1 — Microservicios CRUD con API Gateway

![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)
![React](https://img.shields.io/badge/React-Vite%20%2B%20TypeScript-61DAFB.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)
![Nginx](https://img.shields.io/badge/Nginx-Gateway-269539.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7.svg)
![Vercel](https://img.shields.io/badge/Frontend-Vercel-000000.svg)

> Sistema de microservicios desacoplados por acción CRUD (**Startups** y **Technologies**),
> expuestos a través de un API Gateway con Nginx, autenticación JWT, base de datos
> PostgreSQL compartida y frontend en React — desplegado y funcionando en producción real.

**🌐 Demo en vivo:** [reto-1-gamma.vercel.app](https://reto-1-gamma.vercel.app)
**🔌 Gateway:** [gateway-fswl.onrender.com](https://gateway-fswl.onrender.com/status)

---

## 📋 Descripción del reto

Reto de evaluación individual: diseñar, contenerizar, desplegar, documentar y entregar de
forma reproducible un sistema basado en **microservicios desacoplados por acción CRUD**,
divididos en dos dominios (Startups y Technologies), expuestos a través de un **API Gateway
genérico** (Nginx, sin lógica de negocio), con comunicación HTTP directa, base de datos
compartida y un frontend funcional que consume el gateway.

El uso de herramientas de IA (Claude, Claude Code) estuvo permitido durante el desarrollo,
pero cada decisión técnica documentada en este proyecto es explicable y defendible por el
autor — ver [`docs/DECISIONES.md`](docs/DECISIONES.md) para el detalle completo de cada
decisión de arquitectura, con su razón y las alternativas descartadas.

---

## 🎯 Objetivo de la solución

Entregar un sistema **simple, estable, mantenible y fácil de revisar** por un tercero en
10-15 minutos, evitando sobreingeniería y complejidad innecesaria. La solución incluye:

- ✅ 8 microservicios CRUD (4 por entidad: create/read/update/delete)
- ✅ 1 servicio de autenticación (JWT)
- ✅ 1 API Gateway (Nginx puro, sin lógica de negocio)
- ✅ 1 base de datos PostgreSQL compartida
- ✅ 1 frontend funcional (React + Vite + TypeScript)
- ✅ Contenerización completa con Docker y docker-compose
- ✅ Despliegue real en producción (Render + Vercel)

**Fuera de alcance, deliberadamente:** tests automatizados, arquitectura hexagonal completa,
requestId propagado gateway→servicios — ver [Limitaciones conocidas](#️-limitaciones-conocidas)
y [Siguientes pasos](#-siguientes-pasos).

---

## 🏗️ Arquitectura

Cada microservicio resuelve **una sola acción sobre una sola entidad** — no hay CRUD
monolítico por entidad. El gateway únicamente enruta y hace *strip* de prefijo; nunca valida,
transforma ni decide nada de negocio.

```
                        [ Frontend React (Vercel) ]
                                    │
                                    ▼
                    [ Nginx Gateway (Render) — solo ruteo ]
                                    │
          ┌──────────────┬─────────┴─────────┬──────────────┐
          ▼              ▼                   ▼              ▼
   ┌─────────────┐ ┌─────────────┐   ┌─────────────┐ ┌─────────────┐
   │  Startups   │ │Technologies │   │ Auth Service│ │   (health)  │
   │Create/Read/ │ │Create/Read/ │   │   (login,   │ │  por cada   │
   │Update/Delete│ │Update/Delete│   │  emite JWT) │ │  servicio   │
   └──────┬──────┘ └──────┬──────┘   └──────┬──────┘ └─────────────┘
          │               │                 │
          └───────┬───────┴─────────────────┘
                  ▼
         [ PostgreSQL (Render) ]
       tablas: startups, technologies
```

**Decisiones clave de arquitectura** (detalle completo en `docs/DECISIONES.md`):

- **Auth (JWT):** solo `create` / `update` / `delete` exigen token — `read` es público. Patrón
  REST estándar; simplifica pruebas manuales sin sacrificar seguridad real en mutaciones.
- **Sin capa de repositorio:** cada servicio ejecuta una sola consulta SQL directo en su
  endpoint. Agregar una capa de abstracción para una sola operación sería la sobreingeniería
  que el reto penaliza explícitamente.
- **CORS en cada servicio, no en el gateway:** el gateway solo enruta; la política de qué
  orígenes se permiten es una decisión de seguridad, no de ruteo.
- **`shared/`** (config, db, auth, errors, cors) evita duplicar lógica entre los 9 servicios
  sin crear una librería publicada aparte.

---

## 🧰 Tecnologías utilizadas

| Capa | Tecnología | Razón |
|---|---|---|
| Backend | Python 3.13 + FastAPI | Stack ya dominado, tipado y validación nativa con Pydantic |
| Base de datos | PostgreSQL 16 | Recomendada por el reto, más simple de revisar que Mongo |
| Driver de BD | `psycopg` v3 | `psycopg2-binary` no negociaba TLS con Postgres de Render — ver `DECISIONES.md` |
| API Gateway | Nginx | Exigido por el reto, reverse proxy puro sin lógica de negocio |
| Frontend | React + Vite + TypeScript | Recomendado por el reto, mismo stack ya dominado |
| Autenticación | JWT (HS256) | Plus del reto; ya había experiencia previa, esfuerzo bajo |
| Contenedores | Docker + docker-compose | Exigido por el reto, reproducibilidad total |
| Backend hosting | Render | Blueprint (`render.yaml`) para 9 servicios + gateway en un solo despliegue |
| Frontend hosting | Vercel | Detección automática de Vite, cero configuración manual |
| Control de versiones | Git + GitHub | Historial desde el día uno, commits legibles |

---

## 📁 Estructura del proyecto

```
reto1/
├── gateway/
│   ├── nginx.conf              # Configuración para docker-compose local
│   ├── nginx.render.conf       # Configuración para producción (URLs públicas)
│   ├── Dockerfile
│   └── Dockerfile.render
├── services/
│   ├── startups/
│   │   ├── create/  read/  update/  delete/
│   │   └── (cada uno: main.py, schemas.py, Dockerfile, requirements.txt, .env.example)
│   ├── technologies/
│   │   └── (misma estructura que startups)
│   └── auth/
│       └── main.py, schemas.py, Dockerfile, requirements.txt, .env.example
├── shared/                     # Código compartido por los 9 servicios
│   ├── config.py                # Helper de variables de entorno obligatorias
│   ├── db.py                    # Conexión PostgreSQL (psycopg v3)
│   ├── auth.py                  # Crear/verificar JWT
│   ├── errors.py                # Formato de error uniforme
│   └── cors.py                  # CORSMiddleware compartido
├── frontend/
│   ├── src/
│   │   ├── api/client.ts        # Único punto que arma el header Authorization
│   │   └── pages/                # Login, Startups, Technologies
│   ├── vercel.json               # Rewrites para SPA (React Router)
│   ├── Dockerfile
│   └── nginx.conf
├── db/
│   └── init/
│       ├── 001_schema.sql        # Tabla startups
│       └── 002_technologies_schema.sql
├── docs/
│   ├── DECISIONES.md             # Bitácora de cada decisión no cubierta por el reto
│   └── evidencias/
│       ├── postman/              # Colección / casos de prueba
│       └── capturas/             # Evidencia visual
├── docker-compose.yml            # Orquesta los 10 contenedores en local
├── render.yaml                   # Blueprint de despliegue en Render
├── RETO1-BRIEF.md                # Documento de decisiones consolidado
├── .env.example
├── .gitignore
└── README.md
```

---

## ✅ Requisitos

Para correr el proyecto completo en local:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y corriendo
- [Docker Compose](https://docs.docker.com/compose/) (incluido con Docker Desktop)
- [Git](https://git-scm.com/)

Opcional, solo si se quiere correr algo **fuera** de contenedores:

- Python 3.13 + [uv](https://docs.astral.sh/uv/)
- Node.js 18+

---

## 🔑 Variables de entorno

Cada servicio trae su propio `.env.example`. Resumen de qué necesita cada grupo:

| Variable | Dónde se usa | Descripción |
|---|---|---|
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | Los 8 microservicios CRUD | Conexión a PostgreSQL |
| `DB_SSLMODE` | Los 8 microservicios CRUD | `prefer` en local, `require` en producción (Render exige TLS) |
| `JWT_SECRET` | `create`/`update`/`delete` (ambas entidades) + `auth-service` | Firma y verificación de tokens — **debe ser idéntico** en los 5 |
| `AUTH_USERNAME` / `AUTH_PASSWORD` | `auth-service` | Credenciales del único usuario del sistema (sin tabla de usuarios) |
| `FRONTEND_ORIGIN` | Los 9 servicios de aplicación | Origen permitido por CORS — la URL real del frontend |
| `VITE_API_BASE_URL` | Frontend | URL del gateway (local o producción) |

```bash
cp .env.example .env
# edita .env con tus propios valores antes de levantar el proyecto
```

---

## 💻 Cómo correr localmente

```bash
git clone https://github.com/mhdavid404-sudo/RETO1.git
cd RETO1
cp .env.example .env
docker-compose up --build
```

Esto levanta los **10 contenedores** (PostgreSQL + 9 servicios + gateway + frontend) con un
solo comando. La primera vez tarda varios minutos (construye 9 imágenes de Python + 1 de
Node/Nginx); las siguientes veces es mucho más rápido gracias al cache de capas de Docker.

Verifica que todo esté sano:

```bash
curl http://localhost:8080/status
curl http://localhost:8080/v1/api/startups/read
```

---

## 🌐 URLs y puertos

### Producción (real, desplegado)

| Componente | URL |
|---|---|
| Frontend | https://reto-1-gamma.vercel.app |
| Gateway | https://gateway-fswl.onrender.com |
| Base de datos | PostgreSQL administrado en Render (no público) |

Los 9 servicios de aplicación también tienen URL pública individual en Render (necesario por
las restricciones de red del plan gratuito — ver *Limitaciones conocidas*), pero **nunca se
consumen directo**: el frontend solo le habla al gateway.

### Local (docker-compose)

| Componente | Puerto |
|---|---|
| Frontend | `localhost:3000` |
| Gateway | `localhost:8080` |
| PostgreSQL | `localhost:5432` |

Cada microservicio expone `GET /health` → `{"status": "ok"}`. El gateway expone
`GET /status` → `200 OK` si está operativo.

---

## 🔗 Rutas de API

Todas las rutas van prefijadas con `/v1/api`. Formato de error uniforme en los 9 servicios:

```json
{ "message": "Validation error", "details": ["name: field required"] }
```

Códigos: `201` creado · `200` éxito · `204` eliminado · `400` validación · `401` no
autenticado · `404` no encontrado · `500` error interno.

### Auth

| Método | Endpoint | Body | Protegido |
|---|---|---|---|
| POST | `/v1/api/auth/login` | `{username, password}` → `{token}` | No |

### Startups

| Método | Endpoint | Protegido |
|---|---|---|
| POST | `/v1/api/startups/create` | ✅ JWT |
| GET | `/v1/api/startups/read` (filtros: `?name=&category=`) | ❌ Público |
| GET | `/v1/api/startups/read/:id` | ❌ Público |
| PUT | `/v1/api/startups/update/:id` | ✅ JWT |
| DELETE | `/v1/api/startups/delete/:id` | ✅ JWT |

Body de `create` (camelCase): `{name, foundedAt, location, category, fundingAmount}`
— `name` y `foundedAt` obligatorios, el resto opcional.

### Technologies

| Método | Endpoint | Protegido |
|---|---|---|
| POST | `/v1/api/technologies/create` | ✅ JWT |
| GET | `/v1/api/technologies/read` (filtros: `?sector=&adoptionLevel=`) | ❌ Público |
| GET | `/v1/api/technologies/read/:id` | ❌ Público |
| PUT | `/v1/api/technologies/update/:id` | ✅ JWT |
| DELETE | `/v1/api/technologies/delete/:id` | ✅ JWT |

Body de `create` (camelCase): `{name, sector, description, adoptionLevel}`
— `name` y `sector` obligatorios, el resto opcional.

---

## 🖥️ Flujo del front-end

1. **Login** (`/login`): el usuario ingresa credenciales → el frontend llama a
   `POST /v1/api/auth/login` → guarda el JWT en `localStorage`.
2. **Sin sesión:** los módulos de Startups y Technologies son visibles y consultables
   (`read` es público), pero los botones de crear/editar/eliminar quedan ocultos.
3. **Con sesión:** `src/api/client.ts` adjunta automáticamente
   `Authorization: Bearer <token>` a toda petición de escritura.
4. **Token inválido o expirado:** el gateway responde `401` → el cliente limpia el token y
   redirige a `/login` con un aviso — el frontend nunca valida el JWT por su cuenta, deja que
   el backend decida.
5. **Módulos:** `/startups` y `/technologies`, cada uno con listar (con filtros), crear,
   editar y eliminar (con confirmación).

---

## ☁️ Cómo desplegar

Despliegue real usado en este proyecto — **Opción B** del reto (frontend separado del backend):

### Backend + Gateway (Render)

1. Crear la base de datos PostgreSQL manualmente en Render (no forma parte del Blueprint).
2. Crear un **Blueprint** desde `render.yaml` (raíz del repo) — despliega los 9 servicios de
   aplicación + el gateway en un solo paso.
3. Llenar las variables marcadas `sync: false` (secretos) con los valores reales de la base de
   datos, un `JWT_SECRET` generado, y las credenciales de `AUTH_USERNAME`/`AUTH_PASSWORD`.
4. Los 9 servicios de aplicación son de tipo `web` (el plan gratuito no ofrece `pserv`);
   el gateway les habla por su URL pública real, no por nombre interno.

### Frontend (Vercel)

1. Importar el repositorio en Vercel.
2. **Root Directory: `frontend`** (crítico — el repo no es un proyecto de una sola app).
3. Framework detectado automáticamente: Vite.
4. Variable de entorno: `VITE_API_BASE_URL` = URL real del gateway + `/v1/api`.
5. Deploy.

### Último ajuste, siempre después de desplegar el frontend

Actualizar `FRONTEND_ORIGIN` en los **9 servicios de Render** con la URL real de Vercel
(sin `/` al final) — si no, CORS rechaza todas las peticiones del frontend en producción.

---

## 🧪 Pruebas manuales

Casos mínimos verificados por entidad, todos probados **contra el sistema real desplegado**,
no solo en local:

| Caso | Startups | Technologies |
|---|---|---|
| Crear registro válido | ✅ | ✅ |
| Crear registro inválido (campo faltante / no permitido) | ✅ | ✅ |
| Listar sin filtros | ✅ | ✅ |
| Listar con filtros | ✅ | ✅ |
| Leer detalle — ID correcto | ✅ | ✅ |
| Leer detalle — ID incorrecto (404) | ✅ | ✅ |
| Actualizar — campos permitidos | ✅ | ✅ |
| Actualizar — campo inexistente (404) | ✅ | ✅ |
| Eliminar registro existente | ✅ | ✅ |
| Eliminar registro inexistente (404) | ✅ | ✅ |
| Login correcto / incorrecto | ✅ | — |
| Acción protegida sin token (401) | ✅ | ✅ |

Colección de Postman / scripts curl completos: [`docs/evidencias/postman/`](docs/evidencias/postman/).

---

## 📸 Evidencias

- **Frontend funcionando:** capturas del login, listado con filtros, creación y edición —
  [`docs/evidencias/capturas/`](docs/evidencias/capturas/).
- **API a través del gateway:** respuestas reales de cada caso de la tabla anterior.
- **Sistema levantando en contenedores:** captura de `docker-compose up --build` completando
  los 10 servicios en local.
- **Despliegue real:** capturas del dashboard de Render (9 servicios `Live`) y Vercel.

---

## ⚠️ Limitaciones conocidas

- **Servicios "dormidos" (plan gratuito de Render):** tras ~15 minutos sin tráfico, un
  servicio se duerme y la primera petición puede tardar o fallar (`502`/timeout) mientras
  despierta — un reintento resuelve. Comportamiento normal del plan gratuito, no un error
  del sistema.
- **Microservicios accesibles de forma directa:** por costo, los 9 servicios de aplicación
  son `web` (públicos), no `pserv` (privados) — Render no ofrece `pserv` en el plan
  gratuito. El frontend nunca los llama directo, pero técnicamente son alcanzables sin pasar
  por el gateway. Documentado y aceptado conscientemente, ver `docs/DECISIONES.md`.
- **El error 500 genérico expone el mensaje real de la excepción** (no solo un texto
  genérico) — correcto para depurar en este alcance, se ajustaría en un entorno de
  producción real con usuarios externos.
- **Sin tests automatizados:** el reto no los exige: se priorizó tiempo en arquitectura,
  contenerización, despliegue real y documentación.
- **`requestId` propagado gateway→servicios:** no implementado — quedó como plus opcional
  desde el diseño inicial, sin afectar ningún requisito obligatorio del reto.

---

## 🔜 Siguientes pasos

- Migrar los 9 microservicios a `pserv` (servicios privados) si el proyecto continuara más
  allá del reto, para aislar la red y reforzar a nivel de infraestructura la regla de "solo
  se accede vía gateway".
- Agregar `requestId` generado en el gateway y propagado por header a los microservicios,
  para trazabilidad de peticiones en logs.
- Suite de tests automatizados (pytest) para los 9 servicios.
- Ocultar el detalle interno de la excepción en el manejador de error 500 genérico.
- Migrar la comunicación gateway↔microservicios en Render de URLs públicas a red privada
  si en algún momento se justifica el costo de un plan pagado.

---

## 📦 Información del repositorio Git

| Campo | Valor |
|---|---|
| Repositorio | [github.com/mhdavid404-sudo/RETO1](https://github.com/mhdavid404-sudo/RETO1) |
| Rama principal | `master` |
| Historial | Commits desde el primer día del proyecto, con mensajes descriptivos |
| Acceso | Público |

```bash
git clone https://github.com/mhdavid404-sudo/RETO1.git
cd RETO1
cp .env.example .env
docker-compose up --build
```

---

## 📊 Rúbrica de evaluación

| Criterio | Peso |
|---|---|
| Funcionamiento (CRUDs) | 30% |
| Código y orden (estructura, validación, errores) | 25% |
| Contenedores y despliegue | 20% |
| Documentación y reproducibilidad | 15% |
| Pruebas manuales claras | 10% |
| Plus (pequeños extras bien hechos) | +10% |

---

## 👨‍💻 Autor

**David Axel Manzano Hernández**
📧 mhdavid404@gmail.com · 🐙 [github.com/mhdavid404-sudo](https://github.com/mhdavid404-sudo)

Proyecto construido para el reto de microservicios — Instituto Politécnico Nacional, UPIICSA.
