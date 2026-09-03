-- db/init/002_technologies_schema.sql
--
-- Tabla technologies (brief, seccion 5). Reutiliza la funcion
-- actualizar_updated_at() creada en 001_schema.sql — mismo trigger que
-- startups, sin duplicar la funcion.
--
-- Nota: los scripts en db/init/ solo corren al crear el volumen de
-- Postgres por primera vez. Si el volumen ya existe de una sesion
-- anterior, hay que recrearlo (docker compose down -v) para que este
-- script se aplique.

CREATE TABLE technologies (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    sector          TEXT NOT NULL,
    description     TEXT,
    adoption_level  TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TRIGGER technologies_actualizar_updated_at
    BEFORE UPDATE ON technologies
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_updated_at();
