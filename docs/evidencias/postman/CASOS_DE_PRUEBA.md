# Casos de prueba — RETO1

Todos los casos siguientes fueron ejecutados **contra el sistema real desplegado**
(`https://gateway-fswl.onrender.com`), no solo en local. Las respuestas mostradas son las
que realmente devolvió el sistema durante las pruebas.

Colección importable de Postman: [`RETO1.postman_collection.json`](RETO1.postman_collection.json)

> Antes de importar la colección, configura tus propias credenciales en las variables
> `authUsername` / `authPassword` de Postman — nunca vienen incluidas en el archivo.

---

## Auth

### Login correcto
- **Objetivo:** confirmar que credenciales válidas devuelven un JWT.
- **Request:** `POST /v1/api/auth/login` — `{"username": "<usuario>", "password": "<password>"}`
- **Respuesta esperada:** `200 OK` — `{"token": "eyJhbGciOiJIUzI1NiIs..."}`
- **Resultado real:** confirmado — token JWT válido recibido, con claim `sub` correcto y
  expiración a 1 hora.

### Login incorrecto
- **Objetivo:** confirmar que no se revela si el usuario existe o no.
- **Request:** `POST /v1/api/auth/login` con password incorrecta.
- **Respuesta esperada:** `401` — `{"message": "Credenciales invalidas", "details": ["Credenciales invalidas"]}`
- **Resultado real:** confirmado, mensaje genérico único (no distingue usuario inexistente
  de password incorrecta, por diseño — ver `docs/DECISIONES.md`).

---

## Startups

| # | Caso | Request real | Resultado observado |
|---|---|---|---|
| 1 | Crear válido | `POST /startups/create` `{"name":"Prueba Deploy","foundedAt":"2024-01-01"}` | `201` — registro creado con `id: 1`, timestamps `createdAt`/`updatedAt` generados por el servidor |
| 2 | Crear inválido | `POST /startups/create` sin `name` | `400` — `{"message":"Validation error","details":[...]}` |
| 3 | Listar sin filtros | `GET /startups/read` | `200` — `[]` (lista vacía cuando no hay registros) o arreglo con los existentes |
| 4 | Listar con filtros | `GET /startups/read?category=Software` | `200` — lista filtrada |
| 5 | Leer detalle — ID correcto | `GET /startups/read/1` | `200` — objeto completo del registro |
| 6 | Leer detalle — ID incorrecto | `GET /startups/read/999999` | `404` — `{"message":"No existe...","details":[...]}` |
| 7 | Actualizar — campo permitido | `PUT /startups/update/1` `{"location":"CDMX"}` | `200` — registro con `location: "CDMX"`, `updatedAt` actualizado |
| 8 | Actualizar — campo no permitido | `PUT /startups/update/1` `{"campo_invalido":"x"}` | `400` — rechazado por `extra="forbid"` |
| 9 | Eliminar existente | `DELETE /startups/delete/1` | `204` — sin contenido (éxito silencioso) |
| 10 | Eliminar inexistente | `DELETE /startups/delete/1` (ya eliminado) | `404` — `{"message":"No existe...","details":[...]}` |

**Nota real de esta corrida:** el registro con `id 1` se creó, actualizó a `location: CDMX`,
y se eliminó — el caso 10 se probó reintentando el mismo `DELETE` una vez ya borrado,
confirmando el `404` correcto en un registro que legítimamente ya no existe.

---

## Technologies

| # | Caso | Request real | Resultado observado |
|---|---|---|---|
| 1 | Crear válido | `POST /technologies/create` `{"name":"Prueba Tech","sector":"Software"}` | `201` — registro creado con `id: 1` |
| 2 | Crear inválido | `POST /technologies/create` sin `name` | `400` — `Validation error` |
| 3 | Listar sin filtros | `GET /technologies/read` | `200` — lista |
| 4 | Listar con filtros | `GET /technologies/read?sector=Software` | `200` — lista filtrada |
| 5 | Leer detalle — ID correcto | `GET /technologies/read/1` | `200` — objeto completo |
| 6 | Leer detalle — ID incorrecto | `GET /technologies/read/999999` | `404` |
| 7 | Actualizar — campo permitido | `PUT /technologies/update/1` `{"description":"Actualizada"}` | `200` |
| 8 | Actualizar — registro ya eliminado | `PUT /technologies/update/1` (post-delete) | `404` — `{"message":"No existe una tecnologia con id 1","details":["No existe una tecnologia con id 1"]}` |
| 9 | Eliminar existente | `DELETE /technologies/delete/1` | `204` |
| 10 | Eliminar inexistente | `DELETE /technologies/delete/1` (ya eliminado) | `404` — `{"message":"No existe una tecnologia con id 1","details":["No existe una tecnologia con id 1"]}` |

---

## Seguridad

### Acción protegida sin token
- **Objetivo:** confirmar que `create`/`update`/`delete` exigen JWT, mientras `read` es público.
- **Request:** `POST /startups/create` sin header `Authorization`.
- **Respuesta esperada:** `401` — `{"message":"Falta el header Authorization: Bearer <token>", ...}`
- **Resultado real:** confirmado.

### Token expirado o inválido
- **Objetivo:** confirmar que un JWT vencido o mal formado se rechaza, no se acepta a medias.
- **Resultado real observado:** `{"message":"Token invalido","details":["Token invalido"]}` —
  se confirmó en producción real al reutilizar un token de más de 1 hora de antigüedad.

### CORS restringido
- **Objetivo:** confirmar que solo el origen del frontend real puede consumir la API desde
  un navegador.
- **Resultado real observado:** una petición desde un origen no autorizado es bloqueada por
  el navegador con `blocked by CORS policy` antes de llegar a mostrar cualquier dato —
  confirmado también en el caso real de que el gateway/servicio "dormido" (plan gratuito de
  Render) puede tardar en devolver el header de CORS durante el arranque — comportamiento
  esperado y documentado en el README, sección Limitaciones conocidas.

---

## Evidencia de despliegue

- **Backend:** 9 servicios confirmados `Live` en el dashboard de Render, cada uno probado
  individualmente vía `GET /health` → `{"status":"ok"}`.
- **Gateway:** `GET /status` → `{"status":"ok"}`; las 18 rutas de negocio + login enrutando
  correctamente hacia los servicios reales (no hacia servicios de otros usuarios — se
  corrigió un choque de nombres real durante el despliegue, ver `docs/DECISIONES.md`).
- **Frontend:** desplegado en Vercel, CRUD completo de ambas entidades verificado
  manualmente desde la interfaz real (no solo por API) — login, listar, crear, editar,
  eliminar, en ambos módulos.
