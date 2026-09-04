// src/pages/StartupsPage.tsx
//
// Modulo completo de Startups: listar (con filtros), crear, editar,
// eliminar. Las acciones de crear/editar/eliminar se ocultan cuando no
// hay sesion (isAuthenticated) — decision opcional tomada para no
// dejar que alguien llene un formulario completo antes de enterarse
// que necesita loguearse; igual quedan protegidas en el backend
// (create/update/delete exigen JWT), esto es solo UX.

import { useCallback, useEffect, useState } from 'react';
import { ErrorApi } from '../api/client';
import {
  actualizarStartup,
  crearStartup,
  eliminarStartup,
  listarStartups,
} from '../api/startups';
import { useAuth } from '../auth/useAuth';
import { StartupForm } from '../components/StartupForm';
import type { DatosFormularioStartup } from '../components/StartupForm';
import type { Startup } from '../types/startup';

type ModoFormulario =
  | { tipo: 'ninguno' }
  | { tipo: 'crear' }
  | { tipo: 'editar'; startup: Startup };

function aNumeroOIndefinido(valor: string): number | undefined {
  return valor.trim() === '' ? undefined : Number(valor);
}

function aTextoOIndefinido(valor: string): string | undefined {
  return valor.trim() === '' ? undefined : valor;
}

export function StartupsPage() {
  const { isAuthenticated } = useAuth();
  const [startups, setStartups] = useState<Startup[]>([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filtroNombre, setFiltroNombre] = useState('');
  const [filtroCategoria, setFiltroCategoria] = useState('');
  const [modo, setModo] = useState<ModoFormulario>({ tipo: 'ninguno' });

  const cargar = useCallback(async () => {
    setCargando(true);
    setError(null);
    try {
      const datos = await listarStartups({
        name: aTextoOIndefinido(filtroNombre),
        category: aTextoOIndefinido(filtroCategoria),
      });
      setStartups(datos);
    } catch (err) {
      setError(err instanceof ErrorApi ? err.detalles.join(' ') : 'No se pudo cargar la lista.');
    } finally {
      setCargando(false);
    }
  }, [filtroNombre, filtroCategoria]);

  useEffect(() => {
    cargar();
  }, [cargar]);

  async function manejarCrear(datos: DatosFormularioStartup) {
    await crearStartup({
      name: datos.name,
      foundedAt: datos.foundedAt,
      location: aTextoOIndefinido(datos.location),
      category: aTextoOIndefinido(datos.category),
      fundingAmount: aNumeroOIndefinido(datos.fundingAmount),
    });
    setModo({ tipo: 'ninguno' });
    await cargar();
  }

  async function manejarActualizar(id: number, datos: DatosFormularioStartup) {
    await actualizarStartup(id, {
      name: datos.name,
      foundedAt: datos.foundedAt,
      location: aTextoOIndefinido(datos.location),
      category: aTextoOIndefinido(datos.category),
      fundingAmount: aNumeroOIndefinido(datos.fundingAmount),
    });
    setModo({ tipo: 'ninguno' });
    await cargar();
  }

  async function manejarEliminar(id: number) {
    if (!window.confirm('¿Eliminar esta startup? Esta acción no se puede deshacer.')) {
      return;
    }
    setError(null);
    try {
      await eliminarStartup(id);
      await cargar();
    } catch (err) {
      setError(err instanceof ErrorApi ? err.detalles.join(' ') : 'No se pudo eliminar.');
    }
  }

  return (
    <div className="pagina-startups">
      <h1>Startups</h1>

      <div className="filtros">
        <input
          placeholder="Buscar por nombre"
          value={filtroNombre}
          onChange={(e) => setFiltroNombre(e.target.value)}
        />
        <input
          placeholder="Categoría exacta"
          value={filtroCategoria}
          onChange={(e) => setFiltroCategoria(e.target.value)}
        />
      </div>

      {!isAuthenticated && (
        <p className="aviso">Inicia sesión para crear, editar o eliminar startups.</p>
      )}
      {isAuthenticated && modo.tipo === 'ninguno' && (
        <button type="button" onClick={() => setModo({ tipo: 'crear' })}>
          + Nueva startup
        </button>
      )}

      {modo.tipo === 'crear' && (
        <StartupForm onGuardar={manejarCrear} onCancelar={() => setModo({ tipo: 'ninguno' })} />
      )}
      {modo.tipo === 'editar' && (
        <StartupForm
          startup={modo.startup}
          onGuardar={(datos) => manejarActualizar(modo.startup.id, datos)}
          onCancelar={() => setModo({ tipo: 'ninguno' })}
        />
      )}

      {error && <p className="error">{error}</p>}

      {cargando ? (
        <p>Cargando…</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Fundación</th>
              <th>Ubicación</th>
              <th>Categoría</th>
              <th>Financiamiento</th>
              {isAuthenticated && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {startups.map((startup) => (
              <tr key={startup.id}>
                <td>{startup.name}</td>
                <td>{startup.foundedAt}</td>
                <td>{startup.location ?? '—'}</td>
                <td>{startup.category ?? '—'}</td>
                <td>{startup.fundingAmount ?? '—'}</td>
                {isAuthenticated && (
                  <td className="acciones-fila">
                    <button type="button" onClick={() => setModo({ tipo: 'editar', startup })}>
                      Editar
                    </button>
                    <button type="button" onClick={() => manejarEliminar(startup.id)}>
                      Eliminar
                    </button>
                  </td>
                )}
              </tr>
            ))}
            {startups.length === 0 && (
              <tr>
                <td colSpan={isAuthenticated ? 6 : 5}>No hay startups para mostrar.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}
