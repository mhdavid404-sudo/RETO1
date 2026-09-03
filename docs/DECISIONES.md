# Bitácora de decisiones

Decisiones tomadas durante la construcción que no estaban cerradas en
`RETO1-BRIEF.md`. El brief es el punto de partida y no se edita salvo
corrección de un dato incorrecto; las decisiones nuevas se registran aquí,
en orden cronológico.

---

## 2026-09-02 — Alcance de la protección JWT en los 8 servicios CRUD

**Duda:** el brief (§3) dice que "los otros 8 servicios solo verifican
firma [JWT]", pero no especifica qué endpoints exactos exigen el token.

**Decisión (confirmada con el Product Owner):** solo los endpoints de
**escritura** (`create`, `update`, `delete`) exigen
`Authorization: Bearer <token>` válido. Los endpoints de **lectura**
(`read` — listar y detalle) quedan públicos, sin token.

**Motivo:** patrón REST más común — lectura abierta, mutación protegida.
Mantiene el alcance de auth-service acotado (autenticar quien modifica
datos) sin sobre-restringir un endpoint de solo consulta.

**Cómo se aplica:** los servicios `startups/create`, `startups/update`,
`startups/delete`, `technologies/create`, `technologies/update`,
`technologies/delete` llaman a `shared.auth.verificar_token()` sobre el
header `Authorization`. Los servicios `startups/read` y
`technologies/read` no importan `shared.auth` en absoluto.

---

## 2026-09-02 — Semántica de actualización parcial (PUT update)

**Duda:** el modelo de datos permite actualización parcial, pero no
especifica cómo distinguir "el cliente no mandó este campo" (no tocar)
de "el cliente mandó este campo en null o vacío" (sí aplicar el cambio).

**Decisión (arquitectura, no requiere al Product Owner — es un detalle
de implementación, no una regla de negocio nueva):** se usa
`payload.model_dump(exclude_unset=True)` de Pydantic v2, que solo incluye
las claves que el cliente realmente envió en el JSON, sin importar su
valor. Un campo ausente del body no entra al diccionario y no se toca en
el UPDATE. Un campo presente —aunque sea `null`— sí entra y se aplica.

Excepción: `name` y `founded_at` (startups) / `name` y `sector`
(technologies) son `NOT NULL` en la tabla. Si el cliente los envía
explícitamente como `null`, se rechaza con 400 antes de tocar la DB, en
vez de dejar que Postgres lance un error de constraint menos claro.

**Cómo se aplica:** ver `services/startups/update/main.py` y
`services/technologies/update/main.py` — ambos comparten el mismo
patrón: `CAMPOS_NO_NULEABLES` + construcción dinámica del `SET` solo con
las claves presentes en `exclude_unset=True`.

---

## 2026-09-02 — Bug: JWT_SECRET exigido por servicios que no lo usan

**Qué pasó:** al probar `read-startup-service` end-to-end, el contenedor
no arrancaba. `shared/config.py` exigía `JWT_SECRET` como variable
obligatoria al importarse — pero Python ejecuta el módulo completo al
importarlo, sin importar qué nombres se usen. Como `shared/db.py` importa
`shared/config.py`, y todo servicio importa `shared/db.py`, hasta los
servicios de solo lectura (que nunca verifican tokens y correctamente no
tienen `JWT_SECRET` en su `.env`) fallaban al arrancar.

**Corrección:** `JWT_SECRET` (y `JWT_ALGORITHM`/`JWT_EXPIRATION_MINUTES`)
se movieron de `shared/config.py` a `shared/auth.py`. `auth.py` exige
`JWT_SECRET` únicamente para los servicios que efectivamente lo
importan (`create`/`update`/`delete`, ambas entidades).
`variable_obligatoria()` se dejó pública en `config.py` para que
`auth.py` reutilice el mismo criterio de fallo rápido sin duplicarlo.

*(Nota: en su momento esto dejaba `config.py` con las variables de DB
como "lo único verdaderamente universal". Al construir `auth-service`
—que no toca la DB— se vio que ni eso era universal; ver la entrada del
2026-09-02 "Bug: DB_* exigidas por auth-service" más abajo, que termina
de vaciar `config.py`.)

**Cómo se aplica:** cualquier variable de entorno nueva que solo un
subconjunto de servicios necesite debe vivir en el módulo de `shared/`
que efectivamente la usa, no en `config.py` — `config.py` es solo para lo
verdaderamente universal (DB).

---

## 2026-09-02 — Semántica de los filtros de `read`

**Duda:** el brief lista los filtros opcionales por query string pero no
dice si son coincidencia exacta o parcial.

**Decisión (arquitectura, detalle menor de comportamiento):** los campos
de texto libre (`name` en startups) usan coincidencia parcial
insensible a mayúsculas (`ILIKE '%valor%'`), pensados como búsqueda. Los
campos categóricos (`category` en startups; `sector` y `adoptionLevel`
en technologies) usan coincidencia exacta, por representar valores de un
conjunto cerrado.

---

## 2026-09-02 — Bug: DB_* exigidas por auth-service (que no usa la DB)

**Qué pasó:** al diseñar `auth-service` —el único de los 9 servicios que
no toca la base de datos, brief §3— se detectó el mismo problema de la
entrada anterior mirado desde el otro lado: `shared/config.py` seguía
definiendo `DB_NAME`/`DB_USER`/`DB_PASSWORD` como obligatorias. Como
`shared/auth.py` importa `variable_obligatoria` desde `shared/config.py`,
y Python ejecuta el módulo completo al importarlo, `auth-service`
habría heredado la obligación de tener credenciales de DB configuradas
sin usarlas jamás.

**Corrección:** `shared/config.py` se vació a solo `variable_obligatoria()`
— ninguna variable concreta vive ahí. Las variables `DB_HOST`/`DB_PORT`/
`DB_NAME`/`DB_USER`/`DB_PASSWORD` se movieron a `shared/db.py`, el único
módulo que las usa.

**Cómo se aplica (regla ya estable para el resto del proyecto):**
`shared/config.py` es solo el helper genérico de "leer variable
obligatoria y fallar rápido". Cada módulo de `shared/` que
efectivamente necesita una variable la declara ahí mismo, usando ese
helper. Ningún servicio hereda una obligación de configuración por una
variable que no usa — solo por los módulos de `shared/` que
efectivamente importa.
