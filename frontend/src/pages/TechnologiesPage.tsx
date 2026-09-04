// src/pages/TechnologiesPage.tsx
//
// Mismo patron que StartupsPage.tsx: listar (con filtros), crear,
// editar, eliminar; acciones ocultas sin sesion.

import { useCallback, useEffect, useState } from 'react';
import { ErrorApi } from '../api/client';
import {
  actualizarTechnology,
  crearTechnology,
  eliminarTechnology,
  listarTechnologies,
} from '../api/technologies';
import { useAuth } from '../auth/useAuth';
import { TechnologyForm } from '../components/TechnologyForm';
import type { DatosFormularioTechnology } from '../components/TechnologyForm';
import type { Technology } from '../types/technology';

type ModoFormulario =
  | { tipo: 'ninguno' }
  | { tipo: 'crear' }
  | { tipo: 'editar'; technology: Technology };

function aTextoOIndefinido(valor: string): string | undefined {
  return valor.trim() === '' ? undefined : valor;
}

export function TechnologiesPage() {
  const { isAuthenticated } = useAuth();
  const [technologies, setTechnologies] = useState<Technology[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtroSector, setFiltroSector] = useState('');
  const [filtroAdopcion, setFiltroAdopcion] = useState('');
  const [modo, setModo] = useState<ModoFormulario>({ tipo: 'ninguno' });

  const cargar = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const datos = await listarTechnologies({
        sector: aTextoOIndefinido(filtroSector),
        adoptionLevel: aTextoOIndefinido(filtroAdopcion),
      });
      setTechnologies(datos);
    } catch (err) {
      setError(err instanceof ErrorApi ? err.detalles.join(' ') : 'No se pudo cargar la lista.');
    } finally {
      setCargando(false);
    }
  }, [filtroSector, filtroAdopcion]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  async function manejarCrear(datos: DatosFormularioTechnology) {
    await crearTechnology({
      name: datos.name,
      sector: datos.sector,
      description: aTextoOIndefinido(datos.description),
      adoptionLevel: aTextoOIndefinido(datos.adoptionLevel),
    });
    setModo({ tipo: 'ninguno' });
    await cargar();
  }

  async function manejarActualizar(id: number, datos: DatosFormularioTechnology) {
    await actualizarTechnology(id, {
      name: datos.name,
      sector: datos.sector,
      description: aTextoOIndefinido(datos.description),
      adoptionLevel: aTextoOIndefinido(datos.adoptionLevel),
    });
    setModo({ tipo: 'ninguno' });
    await cargar();
  }

  async function manejarEliminar(id: number) {
    if (!window.confirm('¿Eliminar esta tecnología? Esta acción no se puede deshacer.')) {
      return;
    }
    setError(null);
    try {
      await eliminarTechnology(id);
      await cargar();
    } catch (err) {
      setError(err instanceof ErrorApi ? err.detalles.join(' ') : 'No se pudo eliminar.');
    }
  }

  return (
    <div className="pagina-technologies">
      <h1>Technologies</h1>

      <div className="filtros">
        <input
          placeholder="Sector exacto"
          value={filtroSector}
          onChange={(e) => setFiltroSector(e.target.value)}
        />
        <input
          placeholder="Nivel de adopción exacto"
          value={filtroAdopcion}
          onChange={(e) => setFiltroAdopcion(e.target.value)}
        />
      </div>

      {!isAuthenticated && (
        <p className="aviso">Inicia sesión para crear, editar o eliminar tecnologías.</p>
      )}
      {isAuthenticated && modo.tipo === 'ninguno' && (
        <button type="button" onClick={() => setModo({ tipo: 'crear' })}>
          + Nueva tecnología
        </button>
      )}

      {modo.tipo === 'crear' && (
        <TechnologyForm onGuardar={manejarCrear} onCancelar={() => setModo({ tipo: 'ninguno' })} />
      )}
      {modo.tipo === 'editar' && (
        <TechnologyForm
          technology={modo.technology}
          onGuardar={(datos) => manejarActualizar(modo.technology.id, datos)}
          onCancelar={() => setModo({ tipo: 'ninguno' })}
        />
      )}

      {error && <p className="error">{error}</p>}

      {cargando ? (
        <p className="cargando">Cargando…</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Sector</th>
              <th>Descripción</th>
              <th>Nivel de adopción</th>
              {isAuthenticated && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {technologies.map((technology) => (
              <tr key={technology.id}>
                <td>{technology.name}</td>
                <td>{technology.sector}</td>
                <td>{technology.description ?? '—'}</td>
                <td>{technology.adoptionLevel ?? '—'}</td>
                {isAuthenticated && (
                  <td className="acciones-fila">
                    <button type="button" onClick={() => setModo({ tipo: 'editar', technology })}>
                      Editar
                    </button>
                    <button type="button" onClick={() => manejarEliminar(technology.id)}>
                      Eliminar
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {technologies.length === 0 && (
              <tr>
                <td colSpan={isAuthenticated ? 5 : 4}>No hay tecnologías para mostrar.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
