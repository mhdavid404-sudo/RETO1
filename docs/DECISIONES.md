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
