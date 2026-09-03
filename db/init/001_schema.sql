-- db/init/001_schema.sql
--
-- Se ejecuta una sola vez, al crear el volumen de datos de Postgres por
-- primera vez (comportamiento estandar de la imagen oficial: todo .sql
-- en /docker-entrypoint-initdb.d/ corre en el primer arranque del
-- contenedor).
--
-- Por ahora solo se define la tabla `startups`, la unica que necesita
-- el primer microservicio construido (create-startup-service). La
-- tabla `technologies` se agrega cuando se construya esa entidad.

CREATE TABLE startups (
    id              SERIAL PRIMARY KEY,
    name            TEXT NOT NULL,
    founded_at      DATE NOT NULL,
    location        TEXT,
    category        TEXT,
    funding_amount  NUMERIC,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- updated_at se actualiza solo en cada UPDATE mediante un trigger, para
-- no depender de que cada microservicio recuerde setearlo a mano.
CREATE OR REPLACE FUNCTION actualizar_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER startups_actualizar_updated_at
    BEFORE UPDATE ON startups
    FOR EACH ROW
    EXECUTE FUNCTION actualizar_updated_at();
