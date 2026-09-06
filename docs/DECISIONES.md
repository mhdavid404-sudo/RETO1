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

---

## 2026-09-02 — Dónde se implementa CORS restringido al front

**Contexto:** el documento oficial del reto exige CORS restringido al
dominio del front. Esto no aparece textualmente en `RETO1-BRIEF.md`
(que es un resumen, no el documento completo) — se registra aquí por
instrucción explícita del Product Owner, que confirmó el requisito
directamente. No especifica dónde implementarlo.

**Decisión (confirmada con el Product Owner antes de construir el
gateway):** CORS se implementa en cada uno de los 9 microservicios
FastAPI, vía un helper compartido `shared/cors.py` (`configurar_cors(app)`,
`CORSMiddleware` restringido a una única variable `FRONTEND_ORIGIN`
obligatoria) — **no** en Nginx.

**Motivo:** el brief (§3) dice explícitamente que el gateway "no
valida, no transforma, no decide — solo enruta y hace strip de
prefijo". Decidir qué orígenes se aceptan es una decisión de política
de seguridad, no ruteo puro; ponerla en Nginx habría contradicho ese
principio. La alternativa (CORS en Nginx con `add_header` y manejo de
`OPTIONS`) habría concentrado la configuración en un solo lugar, pero
a costa de darle al gateway una responsabilidad que el documento no le
asigna.

**Cómo se aplica:** los 9 servicios llaman a `configurar_cors(app)`
justo después de crear su instancia de `FastAPI`, antes de
`registrar_manejadores_de_errores(app)`. `FRONTEND_ORIGIN` se agregó a
las anclas YAML de `docker-compose.yml` (`x-db-env`, `x-db-env-protegido`)
y al bloque de `auth-service`, y a los 10 `.env.example` (raíz + 9
servicios). El gateway (`gateway/nginx.conf`) no menciona CORS en
absoluto.

---

## 2026-09-03 — Bug: `secrets.compare_digest` con contraseñas no-ASCII

**Qué pasó:** probando el login del front-end en un navegador real
(no `curl`) con una contraseña que incluía una "ñ", `auth-service`
devolvió 500. El traceback: `TypeError: comparing strings with
non-ASCII characters is not supported` — `secrets.compare_digest`
exige `bytes`, o `str` compuesto solo por ASCII.

**Corrección:** ambos operandos se codifican a UTF-8
(`datos.username.encode("utf-8")`, etc.) antes de comparar. Sigue
siendo comparación de tiempo constante, ahora sobre bytes.

**Cómo se aplica:** `services/auth/main.py`. Cualquier futuro uso de
`compare_digest` en el proyecto debe codificar a bytes primero.

---

## 2026-09-03 — Bug: los errores 500 no llevaban headers CORS

**Qué pasó:** el 500 de arriba, visto desde el navegador, no se
mostró como "error 500" sino como un bloqueo de CORS puro
("blocked by CORS policy: No 'Access-Control-Allow-Origin' header is
present") — `fetch()` nunca llegó a exponerle a React el status code
real.

**Causa raíz:** Starlette trata especial a los handlers registrados
para la clase base `Exception` (como `_manejar_error_no_controlado`
en `shared/errors.py`): en vez de pasar por `ExceptionMiddleware`
(que queda DENTRO de `CORSMiddleware` en el stack), los enruta a
`ServerErrorMiddleware`, que es la capa más externa de toda la
aplicación — por fuera de cualquier middleware agregado con
`add_middleware`, `CORSMiddleware` incluido. Consecuencia: cualquier
excepción no anticipada en cualquiera de los 9 servicios responde
sin headers CORS, y el navegador la reporta como fallo de CORS en vez
de como el error 500 real que es. Los otros tres handlers
(`ErrorAplicacion`, `RequestValidationError` — 400/401/404) no tienen
este problema: Starlette sí los enruta por `ExceptionMiddleware`,
dentro de `CORSMiddleware`.

**Corrección:** `_manejar_error_no_controlado` agrega manualmente
`Access-Control-Allow-Origin`/`Access-Control-Allow-Credentials` a su
propia respuesta cuando el header `Origin` de la petición coincide con
`FRONTEND_ORIGIN` — replicando a mano, solo para este caso, lo que
`CORSMiddleware` no alcanza a hacer.

**Cómo se aplica:** `shared/errors.py` importa `FRONTEND_ORIGIN` de
`shared/cors.py` (seguro: los 9 servicios ya importan `shared.cors`
para llamar `configurar_cors(app)`, así que ningún servicio hereda una
obligación nueva). Detectado probando manualmente en navegador, no con
`curl` ni con los 28 casos scriptados — ninguno de esos forzaba un 500
real con verificación de CORS.

---

## 2026-09-04 — Cómo containerizar el frontend en el compose local

**Contexto:** el documento oficial del reto permite dos formas de
servir el frontend: "detrás de Nginx" o "como hosting estático". No
especifica cuál usar para el `docker-compose.yml` local — se propuso y
confirmó antes de construir.

**Decisión:** Dockerfile multi-stage — build de Vite en una etapa Node,
resultado servido por Nginx en la etapa final. Mismo patrón que
`gateway/Dockerfile` (`nginx:alpine`), consistente con el resto del
proyecto.

**Motivo:** todo el sistema queda reproducible con un solo
`docker-compose up --build`, sin depender de nada externo. Reutiliza
una imagen base (`nginx:alpine`) y un patrón que el proyecto ya usa
para el gateway, en vez de introducir una herramienta nueva (ej. un
servidor Node tipo `serve`) solo para este contenedor.

**Detalle técnico importante:** `VITE_API_BASE_URL` es una variable de
**build time** de Vite (se hornea en el bundle de JS al compilar, no
se lee en runtime dentro del contenedor) — el Dockerfile la recibe
como build arg, no como variable de entorno del contenedor en
ejecución. Distinto de como funcionan las variables de los 9
microservicios (esas sí son de runtime).

**Segundo detalle, encontrado al conectar el frontend al compose:**
`FRONTEND_ORIGIN` (CORS) acepta un único origen, no una lista — y el
frontend ahora corre en dos puertos distintos según el escenario:
`npm run dev` (servidor de Vite, hot reload) en `:5173`, o el
contenedor Nginx del compose completo en `:3000`. Un solo valor de
`FRONTEND_ORIGIN` sirve para uno de los dos a la vez. Se cambió el
default del `.env.example` raíz a `http://localhost:3000` (el
escenario "todo con un comando" que este `docker-compose.yml` existe
para resolver), documentando en el propio archivo que hay que
cambiarlo a `:5173` si se está iterando con `npm run dev`.

---

## 2026-09-04 — Opción de despliegue real: B (Vercel + Render/Railway)

**Contexto:** el documento oficial del reto ofrece dos opciones de
despliegue — Opción A (backend+gateway en Render/Railway, DB
administrada) u Opción B (frontend en Vercel, backend+gateway en
Render/Railway). Tampoco aparece en `RETO1-BRIEF.md` — información
directa del documento oficial, confirmada por el Product Owner.

**Decisión (confirmada con el Product Owner):** Opción B — frontend en
Vercel, backend+gateway en Render/Railway.

**Motivo (corregido por el Product Owner — la razón real, no la que
propuse primero):** Vercel detecta y despliega un proyecto Vite+React
sin configuración manual. Esa es la razón — no un argumento de
"separación arquitectónica", que ya la da el código (el frontend solo
habla con el gateway, brief sección 8) y no depende de en qué
plataforma quede hospedado cada pieza.

**Cómo se aplica:** el deploy real (crear cuentas, conectar
repositorios, hacer clic en "deploy") lo hace el Product Owner, no
Claude Code — el trabajo de construcción es dejar Dockerfiles,
configuración y variables de entorno listos para que ese paso sea
simple. Detalle de despliegue (comandos exactos, variables por
plataforma) se documenta más adelante, en la sección "Cómo desplegar"
del README — todavía no construida.

---

## 2026-09-04 — render.yaml: tipo de servicio, secretos, nombres

**Contexto:** antes de escribir `render.yaml` se verificó contra la
documentación oficial de Render (no se asumió nada de memoria, dado
que esto lo va a usar el Product Owner para desplegar de verdad).

**Decisión 1 — los 10 servicios son `type: web`, no `pserv`:**
Render no ofrece "private services" en el plan gratuito (confirmado:
solo Web Services, Static Sites, Postgres y Key Value tienen instancia
gratis). Pagar un plan de pago por 9 `pserv` solo para mantenerlos sin
URL pública no se justificaba para un proyecto de evaluación —
decisión revertida sobre la marcha después de proponer `pserv`
inicialmente y encontrar el costo real.

**Consecuencia encontrada después de decidir lo anterior:** un `web`
service **gratuito** de Render puede *enviar* tráfico por la red
privada, pero **no puede recibirlo** (confirmado en la documentación:
"Free web services can send private network requests, but they can't
receive them"). Esto significa que el gateway **no puede** alcanzar a
los 9 microservicios por su hostname interno — al contrario de
`docker-compose.yml`, donde sí funciona porque ahí todos los
contenedores están en la misma red Docker sin esa restricción.

**Corrección:** se creó `gateway/Dockerfile.render` +
`gateway/nginx.render.conf`, específicos para Render — cada `location`
apunta a la URL pública real del microservicio
(`https://<nombre-del-servicio>.onrender.com`) en vez del hostname
interno (`create-startup-service:8000`). `docker-compose.yml` y
`gateway/nginx.conf` (desarrollo local) **no cambiaron**.
`proxy_ssl_server_name on;` agregado porque ahora se habla HTTPS con
SNI a un host compartido, cosa que no aplicaba al proxy HTTP interno
original.

**Riesgo aceptado (documentado, no resuelto con infraestructura
extra):** los nombres de servicio en Render son globales — si
"create-startup-service" (por ejemplo) ya estuviera tomado por otro
usuario de Render, esa URL específica cambiaría con un sufijo, y esa
línea de `nginx.render.conf` habría que corregirla a mano tras el
primer deploy. Se evaluó una alternativa más robusta (templating con
`envsubst` + variables de entorno en el gateway) y se descartó por
agregar piezas móviles a un problema de baja probabilidad — decisión
del Product Owner, explícita, no un atajo tomado en silencio.

**Decisión 2 — secretos con `sync: false`:** `JWT_SECRET`,
`DB_PASSWORD` y `AUTH_PASSWORD` (los tres que pidió el Product Owner)
más, por consistencia, `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER` (no
pedidos explícitamente, pero son igual de "credenciales de conexión" —
mejor no dejar ninguno de los 5 valores de la DB escrito en el
archivo). Render pide estos valores una sola vez desde el dashboard al
crear el Blueprint y nunca los escribe en `render.yaml`. `AUTH_USERNAME`
queda en texto plano (no pedido, y no es tan sensible como una
contraseña).

**Por qué no se usó `envVarGroups`** (el mecanismo nativo de Render
para compartir variables entre servicios, evitaría repetir la lista
7-8 veces): confirmado en la documentación que **Render ignora en
silencio cualquier `sync: false` dentro de un grupo** — y casi todo lo
que estos servicios comparten es `sync: false`. Usarlo habría
significado que los secretos quedaran sin ocultar sin ningún error
visible. Se repite la lista de variables en cada servicio en su lugar
— es el patrón que la propia documentación de Render muestra cuando
hay secretos de por medio.

**Decisión 3 — nombres de servicio:** idénticos a los de
`docker-compose.yml` (y por lo tanto a los upstreams ya escritos en
`gateway/nginx.conf` para desarrollo local). Confirmado en la
documentación de Render que el `name` de un servicio en el blueprint
es su hostname en la red privada — la decisión de nombrarlos igual no
es solo por reconocibilidad en el dashboard (lo que pidió el Product
Owner), también evita tener que mantener dos esquemas de nombres
distintos para el mismo sistema.

---

## 2026-09-04 — Incidente real: los 9 nombres "limpios" ya estaban tomados

**Qué pasó:** el riesgo que ya se había documentado como "aceptado, de
baja probabilidad" (ver la decisión de `render.yaml` de más arriba) se
materializó de verdad: los 9 nombres simples (`create-startup-service`,
etc.) ya estaban tomados por otros usuarios de Render, así que Render
le agregó un sufijo a cada uno de los 9 servicios al crearlos (ej.
`read-technology-service-ztgl`, no `read-technology-service`).
`gateway/nginx.render.conf` seguía escrito con los nombres sin sufijo.

**Síntoma:** el gateway no fallaba con un 404 "servicio no existe" —
resolvía `read-technology-service.onrender.com` contra el servicio de
**otro dueño** que por casualidad eligió el mismo nombre base, y ese
servicio estaba suspendido. El error visible (502/503) no apuntaba a
la causa real (nombre equivocado) sin revisar el dashboard de Render.

**Corrección:** se pegaron las 9 URLs reales (confirmadas por el
Product Owner desde el dashboard) en los 9 `location` de
`gateway/nginx.render.conf`. Verificado con `curl` contra cada una de
las 9 URLs corregidas en `/health` — las 9 responden
`{"status":"ok"}`, confirmando que apuntan a nuestros propios
servicios y no a los de otro usuario.

**Cómo se aplica:** si cualquiera de estos 9 servicios se recrea en
Render (borrado y vuelto a crear, blueprint reaplicado desde cero,
etc.), hay que volver a verificar su URL real en el dashboard antes de
asumir que el nombre limpio sigue libre — no es algo que se resuelva
una sola vez y quede fijo para siempre.

---

## 2026-09-04 — Incidente real: TLS con la DB externa de Render

**Qué pasó:** los 8 servicios CRUD desplegados en Render no podían
conectar a la base de datos (externa, ya existente, ver decisiones de
`render.yaml` más arriba) — el error era
`SSL connection has been closed unexpectedly` durante la negociación
TLS. Diagnóstico del Product Owner, confirmado contra la documentación
oficial de Render: las conexiones externas a Postgres en Render exigen
TLS explícito, y `sslmode=prefer` (el default de psycopg2/libpq, que
usábamos implícitamente al no pasar `sslmode` en absoluto) no siempre
negocia bien ese requisito.

**Corrección:** `DB_SSLMODE` nueva en `shared/db.py`, leída con
`os.getenv("DB_SSLMODE", "prefer")` — default idéntico al
comportamiento anterior, así que `docker-compose.yml` (que no define
esta variable) no cambia en nada; se pasa a
`psycopg2.connect(sslmode=DB_SSLMODE, ...)`. En `render.yaml`, los 8
servicios CRUD (no `auth-service`, que no toca la DB) reciben
`DB_SSLMODE: require`. No es secreto — va con valor fijo, sin
`sync: false`.

**Cómo se aplica:** cualquier variable nueva que solo afecte a un
entorno (aquí: solo producción contra una DB externa) debe tener un
default que reproduzca el comportamiento actual, para que agregarla no
sea un cambio de comportamiento local — mismo principio ya aplicado a
`DB_HOST`/`DB_PORT` (default `db`/`5432` para desarrollo local) desde
el principio del proyecto.

**Verificado:** `shared/db.py` compila; creación real de una startup
contra Postgres local con el nuevo código (sin `DB_SSLMODE` definida,
igual que antes) sigue devolviendo 201 — comportamiento local
confirmado sin cambios, no solo argumentado.

**Servicios a redesplegar:** los 8 CRUD (`create`/`read`/`update`/
`delete` × Startups/Technologies) — cambiaron tanto `shared/db.py`
(código, empaquetado en cada imagen) como su propia variable de
entorno en `render.yaml`. `auth-service` y `gateway` no cambiaron, no
hace falta tocarlos.

---

## 2026-09-04 — Migración de psycopg2 a psycopg (v3): causa raíz real

**Qué pasó:** `DB_SSLMODE: require` (decisión anterior) no resolvió el
problema — la conexión seguía cortándose durante la negociación TLS
contra la DB externa de Render (`SSL connection has been closed
unexpectedly`). El Product Owner aisló la causa raíz **fuera** del
código del proyecto: probó la misma base de datos y las mismas
credenciales cambiando únicamente la librería cliente — `psycopg2`
falla la negociación TLS contra Postgres de Render, `psycopg` (v3) sí
conecta. No fue un error de configuración (`sslmode`, credenciales,
red) sino de la librería misma.

**Corrección — migración de `psycopg2-binary` a `psycopg[binary]` v3
en los 8 servicios que tocan la DB** (no `auth-service`):

- Los 8 `requirements.txt`: `psycopg2-binary==2.9.10` →
  `psycopg[binary]==3.3.5`.
- `shared/db.py`: `import psycopg2` / `psycopg2.extras` →
  `import psycopg` / `from psycopg.rows import dict_row`.
  `psycopg.connect(...)` acepta los mismos parámetros que psycopg2
  (`host`, `port`, `dbname`, `user`, `password`, `sslmode`) — se
  agregó `row_factory=dict_row` al `connect()` para que
  `cursor.fetchone()`/`fetchall()` sigan devolviendo cada fila como
  `dict`, igual que con `RealDictCursor` antes. El resto de
  `obtener_cursor()` (commit/rollback/close) no cambió — los nombres
  de esos métodos son iguales entre psycopg2 y psycopg v3.
- Ningún `main.py` ni `schemas.py` cambió: psycopg v3 soporta el mismo
  estilo de placeholders `%(nombre)s` que ya usan las consultas SQL de
  los 8 servicios, y ninguno importaba `psycopg2` directamente (se
  verificó con grep antes de dar la migración por completa).

**Verificado antes de subir nada** (no solo argumentado): sistema
completo reconstruido con `docker-compose up --build` contra Postgres
**local** (no Render) — mismo set de pruebas de siempre a través del
gateway (login, CRUD completo de ambas entidades, filtros, validación,
404, trigger `updated_at`) — todos los casos devuelven exactamente lo
mismo que antes de la migración.

**Cómo se aplica:** cuando una librería de infraestructura (driver de
DB, cliente HTTP, etc.) falla contra un proveedor externo específico
sin una causa de configuración clara, vale la pena aislar la variable
"librería" antes de seguir ajustando parámetros de conexión — el
Product Owner lo hizo probando la misma DB/credenciales con
`psycopg` v3 directamente, fuera de este proyecto, antes de pedir el
cambio aquí.

---

## 2026-09-04 — Incidente real: base de datos original irrecuperable, DB nueva

**Nota:** esta entrada documenta trabajo que hizo directamente el
Product Owner fuera de esta sesión (en el dashboard de Render, no en
el repositorio) — se registra aquí por instrucción suya explícita,
para que la bitácora quede completa, no porque Claude Code lo haya
ejecutado o verificado de primera mano.

**Qué pasó:** la migración de `psycopg2` a `psycopg` v3 (entrada
anterior) confirmó que el problema no era la librería cliente en
abstracto, sino algo irrecuperable en la base de datos Postgres
original de Render — aislado comparando `psycopg2` contra `psycopg`
v3 con **la misma DB y las mismas credenciales**: si el fallo persistía
incluso con la librería que sí funciona en general, la causa ya no
podía ser la conexión desde el lado del cliente.

**Corrección:** se creó una base de datos Postgres nueva en Render. El
esquema (`db/init/001_schema.sql` y `002_technologies_schema.sql`) se
aplicó a mano contra la DB nueva — estos archivos solo se ejecutan
automáticamente en el primer arranque de un volumen local vía
`docker-entrypoint-initdb.d` (`docker-compose.yml`); una DB administrada
de Render, nueva o vieja, siempre requirió aplicarlos a mano desde el
principio (ver la decisión de `render.yaml`: "la base de datos ya
existe, creada manualmente"). Las 5 credenciales de conexión de la DB
nueva se actualizaron directamente en el dashboard de Render, en los 8
servicios CRUD — son las mismas 5 variables `sync: false`
(`DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD`) que ya existían
en `render.yaml` desde que se escribió el Blueprint; **no fue necesario
tocar el archivo**, porque su función es justamente no guardar el valor
real, solo el nombre de la variable a rellenar.

**Cómo se aplica:** el diseño de `render.yaml` con `sync: false` para
las 5 credenciales de DB (decisión previa, antes de que este incidente
ocurriera) resultó ser lo que permitió resolver esto sin ningún commit
ni redeploy del blueprint — solo redeploy de los 8 servicios CRUD para
que tomaran las nuevas variables de entorno. Si esas 5 variables
hubieran tenido valores fijos escritos en el archivo, este incidente
habría requerido además un commit exponiendo (brevemente, en el
historial de Git) las credenciales de la DB vieja.

---

## 2026-09-04 — Ajuste final de FRONTEND_ORIGIN tras desplegar en Vercel

**Nota:** igual que la entrada anterior, este ajuste lo hizo el Product
Owner directamente en el dashboard de Render, no a través de esta
sesión.

**Qué pasó:** una vez desplegado el frontend en Vercel y conocida su
URL real, `FRONTEND_ORIGIN` se actualizó en los 9 servicios (los 8 CRUD
+ `auth-service`) para que CORS deje de apuntar al placeholder
`https://TU-APP.vercel.app` que traía `render.yaml` desde que se
escribió (ver la decisión de `render.yaml` más arriba) y apunte al
dominio real del frontend en Vercel.

**Resuelto:** el drift entre `render.yaml` (placeholder) y el valor
real en el dashboard de Render duró desde que se escribió el Blueprint
hasta que se conoció la URL real del frontend
(`https://reto-1-gamma.vercel.app`). En cuanto se tuvo esa URL, se
actualizó también en `render.yaml` (los 9 `value: FRONTEND_ORIGIN`) —
el archivo volvió a ser la fuente de verdad completa, ya no depende de
que el dashboard y el repo coincidan por casualidad.

**Cómo se aplica:** a diferencia de las credenciales de DB (`sync:
false`, entrada anterior), `FRONTEND_ORIGIN` es un valor literal en el
archivo — por diseño, para que no haya que rellenarlo a mano en el
dashboard en un despliegue nuevo desde cero. La consecuencia es que
**si se edita solo en el dashboard sin actualizar también el archivo**,
un futuro redeploy del blueprint revierte el cambio silenciosamente.
Este es exactamente el tipo de mecanismo (`sync: false` vs. valor
literal) que ya se documentó al escribir `render.yaml` — la elección
correcta depende de si el valor es secreto, no de si cambia con el
tiempo.

---

## 2026-09-04 — Servicios dormidos en el plan gratuito de Render (502/timeouts intermitentes)

**Qué pasó:** durante las pruebas manuales sobre el sistema desplegado,
aparecieron 502 y timeouts intermitentes sin patrón aparente — no
coincidían con ningún bug de código ya conocido (auth, CORS, DB).

**Causa (comportamiento documentado de Render, no un bug del
proyecto):** los "web services" del plan gratuito de Render se
duermen tras un período sin tráfico entrante. La primera petición que
les llega después de dormir no se sirve de inmediato: Render tiene que
arrancar el contenedor de nuevo ("cold start"), lo que puede tardar
más que el timeout normal de un cliente HTTP o del propio
`proxy_read_timeout` de 30s configurado en `gateway/nginx.render.conf`
— de ahí el 502/timeout. Una segunda petición inmediatamente después,
con el servicio ya despierto, normalmente responde bien. Con **10
servicios independientes** (9 microservicios + gateway) en plan
gratuito, cualquiera de ellos puede estar dormido en un momento dado,
así que el síntoma aparece en puntos distintos del flujo cada vez.

**No se "corrigió" con código** — es una limitación conocida y
aceptada del plan gratuito, no un defecto del sistema. La alternativa
(planes pagos que no duermen) ya se descartó antes por costo, en la
misma decisión que llevó a los 10 servicios como `web` en vez de
`pserv` (ver más arriba).

**Cómo se aplica:** al hacer pruebas manuales o evidencias para el
README, conviene "despertar" el sistema con una petición de
calentamiento (ej. pegarle a `/status` del gateway y a `/health` de
cada microservicio) y esperar unos segundos antes de correr las
pruebas reales, en vez de interpretar el primer 502 como un bug.
Documentar esto también como limitación conocida en la sección
correspondiente del README (brief sección 9) cuando se escriba.
