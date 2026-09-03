# RETO1 — Brief de Inicio y Decisiones Consolidadas

> Documento de arranque para Claude Code. Reúne la problemática oficial del reto
> más todas las decisiones de arquitectura ya cerradas con el Product Owner (Jefe).
> No es un documento vivo de trabajo diario: es el punto de partida. Decisiones
> nuevas que surjan durante la construcción se documentan aparte (bitácora de cambios),
> no se edita este archivo salvo corrección de un dato incorrecto.

---

## 0. Identidad y filosofía de trabajo

Rol: **Arquitecto Principal**, no generador de código que solo cumple tareas.

Orden de prioridad: **Comprender → Diseñar → Validar → Documentar → Implementar.**
Nunca saltar directo a código sin haber pasado por las fases anteriores.

Criterio de decisión ante varias opciones: la más mantenible, no la más rápida.
Ante incertidumbre: documentar la decisión antes de implementarla.

Reglas de calidad:
- Responsabilidad única por módulo/archivo.
- Sin lógica duplicada entre los 9 servicios (por eso existe `shared/`).
- Sin código "temporal" ni que necesite explicarse constantemente.
- Errores siempre explícitos, nunca silenciosos.
- El dominio (reglas de negocio) nunca depende de infraestructura (DB, framework web).

Relación con el Product Owner: el PO define negocio, el arquitecto define arquitectura.
Si se detecta una inconsistencia entre este brief y la realidad del código, se documenta
y se propone alternativa — no se decide unilateralmente sobre alcance o reglas de negocio.

**Ajuste específico para este proyecto:** el reto penaliza explícitamente la
sobreingeniería, los patrones complejos sin necesidad y la abstracción prematura.
La mantenibilidad aquí se logra por **consistencia entre los 9 servicios** (mismo
esqueleto, mismo manejo de errores, mismo patrón de validación), no por profundidad
de capas. No aplicar DDD táctico completo ni CQRS — es deliberado, no un atajo.

---

## 1. Resumen del reto

- **Origen:** reto de evaluación individual (competencia), entrega solo.
- **Fecha límite:** viernes 7 de septiembre de 2026.
- **Objetivo:** diseñar, contenerizar, desplegar, documentar y entregar de forma
  reproducible un sistema de microservicios desacoplados por acción CRUD, expuestos
  vía API Gateway genérico, con DB compartida y front-end funcional.
- **No se premia complejidad innecesaria** — se premia una solución simple, estable,
  mantenible, desplegable y fácil de revisar por terceros en poco tiempo.
- **El uso de IA (Claude Code incluido) está permitido**, pero la solución final debe
  ser entendible, ejecutable, documentada y **defendible técnicamente** por quien la
  entrega. Esto significa: código explicable, no solo funcional.

### Rúbrica de evaluación (publicar tal cual en el README)
| Criterio | Peso |
|---|---|
| Funcionamiento (CRUDs) | 30% |
| Código y orden (estructura, validación, errores) | 25% |
| Contenedores y despliegue | 20% |
| Documentación y reproducibilidad | 15% |
| Pruebas manuales claras | 10% |
| Plus (pequeños extras bien hechos) | +10% |

---

## 2. Stack tecnológico (cerrado)

| Componente | Decisión | Motivo |
|---|---|---|
| Backend (8 microservicios + auth) | Python 3.13 + FastAPI | Stack ya dominado (reutilizado de ATLAS) |
| Front-end | React + Vite + TypeScript | Mismo stack de ATLAS |
| Base de datos | PostgreSQL | Recomendada por el reto, más simple de revisar |
| API Gateway | Nginx (reverse proxy puro) | Exigido por el reto, sin lógica de negocio |
| Contenedores | Docker + docker-compose | Exigido por el reto |
| Gestor de paquetes Python | uv | Ya instalado y usado en ATLAS |
| Auth (plus, +10%) | JWT simple | Ya hay experiencia previa (ATLAS), esfuerzo bajo |
| requestId propagado (plus) | **Diferido** — solo si sobra tiempo después de que los 8 CRUD + gateway + front + docs estén sólidos | No comprometer alcance base por un extra |

Ya instalado en la máquina local (no reinstalar): Docker Desktop, Python 3.13,
Node.js, uv. Nuevo por-proyecto (instalar la primera vez): FastAPI, uvicorn,
psycopg2-binary (o psycopg), PyJWT, react-router-dom.

**Entorno local:** carpeta nueva y separada de ATLAS, ej. `C:\dev\proyectos\reto1`
(fuera de OneDrive). A diferencia de ATLAS, **Git se inicializa desde el día uno**
con commits reales durante la construcción — el reto exige historial legible como
parte de la entrega, no se puede dejar para el final.

---

## 3. Arquitectura general

```
[ Frontend React ]
        |
        v
[ Nginx Gateway ]  (solo ruteo, /v1/api/... , sin lógica de negocio)
   |  |  |  |  |
   v  v  v  v  v
[Create][Read][Update][Delete] Startups     [Auth Service]
[Create][Read][Update][Delete] Technologies
   |__________________________________|
                  |
                  v
           [ PostgreSQL ]
       (tablas: startups, technologies)
```

Principios:
- Cada microservicio hace **una sola acción sobre una sola entidad**. No hay CRUD
  monolítico por entidad.
- El gateway no valida, no transforma, no decide — solo enruta y hace strip de prefijo.
- Cada microservicio abre y cierra su propia conexión a PostgreSQL por request
  (no se justifica un pool complejo para este alcance).
- Autenticación: el `auth-service` emite el JWT; los otros 8 servicios solo
  verifican firma (no hay lógica de negocio de usuarios fuera de auth-service).

---

## 4. Estructura de repositorio

```
reto1/
  gateway/
    nginx.conf
    Dockerfile
  services/
    startups/{create,read,update,delete}/
      main.py
      schemas.py
      Dockerfile
      requirements.txt
      .env.example
    technologies/{create,read,update,delete}/
      (misma estructura)
    auth/
      main.py
      Dockerfile
      requirements.txt
      .env.example
  shared/
    config.py      # variables de entorno comunes
    db.py          # conexión PostgreSQL
    auth.py        # crear/verificar JWT
    errors.py      # formato de error uniforme + exception handlers
  frontend/
    (Vite + React + TS: módulos Startups, Technologies, Login)
  db/
    init/
      001_schema.sql
  docs/
    evidencias/
      postman/
      capturas/
  docker-compose.yml
  README.md
  .env.example
  .gitignore
```

`shared/` se monta en cada contenedor vía build context en la raíz del repo
(cada Dockerfile hace `COPY shared/ /app/shared` además de su propio código),
evitando duplicar lógica entre los 9 servicios sin crear una librería publicada aparte.

---

## 5. Modelo de datos

### Tabla `startups`
| Campo | Tipo | Obligatorio al crear |
|---|---|---|
| id | serial / uuid PK | auto |
| name | text | **sí** |
| founded_at | date | **sí** |
| location | text | no |
| category | text | no |
| funding_amount | numeric | no |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

### Tabla `technologies`
| Campo | Tipo | Obligatorio al crear |
|---|---|---|
| id | serial / uuid PK | auto |
| name | text | **sí** |
| sector | text | **sí** |
| description | text | no |
| adoption_level | text | no |
| created_at | timestamp | auto |
| updated_at | timestamp | auto |

> Decisión tomada por el arquitecto (recomendación, no venía definida en el
> documento del reto): mínimo indispensable obligatorio por entidad, el resto
> opcional pero solo esos campos son aceptados (`extra="forbid"` en el schema
> de validación). Ajustar aquí si el Product Owner decide lo contrario antes
> de construir.

Actualizar (`update`) acepta únicamente los mismos campos, todos opcionales
(actualización parcial), rechazando cualquier campo no listado arriba.

---

## 6. Contratos de API (vía gateway, prefijo `/v1/api`)

Formato de error estándar en todos los servicios:
```json
{ "message": "Validation error", "details": ["name is required", "fundingAmount must be a number"] }
```
Códigos: 201 creado · 200 éxito · 204 eliminado sin contenido · 400 validación ·
401 no autenticado · 404 no encontrado · 500 error interno.

### Startups
- `POST /v1/api/startups/create` — body `{name, foundedAt, location, category, fundingAmount}` (camelCase en payload, snake_case en DB) → 201 / 400
- `GET /v1/api/startups/read` — filtros opcionales `?name=&category=` → 200
- `GET /v1/api/startups/read/:id` → 200 / 404
- `PUT /v1/api/startups/update/:id` — solo campos permitidos → 200 / 400 / 404
- `DELETE /v1/api/startups/delete/:id` → 204 / 404

### Technologies
- `POST /v1/api/technologies/create` — body `{name, sector, description, adoptionLevel}` → 201 / 400
- `GET /v1/api/technologies/read` — filtros opcionales `?sector=&adoptionLevel=` → 200
- `GET /v1/api/technologies/read/:id` → 200 / 404
- `PUT /v1/api/technologies/update/:id` → 200 / 400 / 404
- `DELETE /v1/api/technologies/delete/:id` → 204 / 404

### Auth (plus)
- `POST /v1/api/auth/login` — body `{username, password}` validados contra variables
  de entorno (sin tabla de usuarios, para no ampliar el alcance de la DB) → devuelve
  `{token}` firmado JWT (HS256, expira en 1h) → 200 / 401

### Salud
- Cada uno de los 9 servicios expone `GET /health` → `{"status": "ok"}`.
- El gateway expone opcionalmente `GET /status` → 200 si está operativo.

---

## 7. Nginx — reglas de ruteo

Prefijo `/v1/api` obligatorio en todas las rutas. Timeout 30s, logging de acceso
activado, buffering por defecto. Patrón de strip de prefijo (ejemplo Startups,
replicar para Technologies y Auth):

```nginx
location = /v1/api/startups/read { proxy_pass http://read-startup-service:8000/; }
location /v1/api/startups/read/  { proxy_pass http://read-startup-service:8000/; }
location = /v1/api/startups/create { proxy_pass http://create-startup-service:8000/; }
location /v1/api/startups/update/  { proxy_pass http://update-startup-service:8000/; }
location /v1/api/startups/delete/  { proxy_pass http://delete-startup-service:8000/; }
```

---

## 8. Front-end

- React + Vite + TS, dos módulos obligatorios: `/startups`, `/technologies`
  (listar, crear, editar, eliminar cada uno).
- Consume exclusivamente el gateway (`VITE_API_BASE_URL=http://localhost:8080/v1/api`),
  nunca los microservicios directo.
- Login simple para obtener el JWT y adjuntarlo como `Authorization: Bearer <token>`
  en las peticiones protegidas.
- Formularios con validación básica, mensajes claros de error, estados de carga.

---

## 9. Documentación obligatoria (README.md — 17 secciones exactas)

Descripción del reto · Objetivo de la solución · Arquitectura (con diagrama ASCII) ·
Tecnologías utilizadas · Estructura del proyecto · Requisitos · Variables de entorno ·
Cómo correr localmente · URLs y puertos · Rutas de API · Flujo del front-end ·
Cómo desplegar · Pruebas manuales · Evidencias · Limitaciones conocidas ·
Siguientes pasos · Información del repositorio Git · Rúbrica de evaluación (publicarla tal cual).

Pruebas manuales mínimas por entidad: crear válido/inválido, listar sin/con filtros,
leer detalle correcto/incorrecto, actualizar con campos permitidos/no permitidos,
eliminar existente/inexistente — documentadas con request, respuesta esperada y evidencia.

---

## 10. Entregables finales (checklist de cierre)

- [ ] URL activa del gateway y del front-end
- [ ] Código fuente completo, contenerizado, `docker-compose up --build` reproducible
- [ ] Repositorio Git con rama principal clara y commits legibles desde el día uno
- [ ] README completo (17 secciones) + `.env.example` completo
- [ ] Colección Postman o scripts curl con los 10 casos mínimos por entidad
- [ ] Capturas del front-end y de las pruebas de API

---

## 11. Pendientes explícitos (no decidir sin aprobación del Product Owner)

- requestId propagado gateway→servicios: no construir salvo que sobre tiempo real
  después de cerrar todo lo demás.
- Cualquier campo, regla de validación o entidad no listada aquí: no se agrega
  por iniciativa propia — se documenta la duda y se pregunta.
