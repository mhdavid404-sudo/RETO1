// src/components/StartupForm.tsx
//
// Formulario reutilizado para crear y editar (se le pasa `startup`
// para editar; sin esa prop, es de creacion). En modo edicion se
// pre-llena con los valores actuales; al guardar se envian TODOS los
// campos del formulario, no solo los que cambiaron — el backend
// soporta actualizacion parcial (exclude_unset), pero el formulario
// hace una actualizacion "completa" a proposito: es mas simple que
// rastrear que campos toco el usuario, y el resultado es el mismo
// (todos los campos visibles quedan con el valor que se ve en pantalla).

import { useState } from 'react';
import type { FormEvent } from 'react';
import { ErrorApi } from '../api/client';
import type { Startup } from '../types/startup';

export interface DatosFormularioStartup {
  name: string;
  foundedAt: string;
  location: string;
  category: string;
  fundingAmount: string;
}

interface Props {
  startup?: Startup;
  onGuardar: (datos: DatosFormularioStartup) => Promise<void>;
  onCancelar: () => void;
}

export function StartupForm({ startup, onGuardar, onCancelar }: Props) {
  const [name, setName] = useState(startup?.name ?? '');
  const [foundedAt, setFoundedAt] = useState(startup?.foundedAt ?? '');
  const [location, setLocation] = useState(startup?.location ?? '');
  const [category, setCategory] = useState(startup?.category ?? '');
  const [fundingAmount, setFundingAmount] = useState(startup?.fundingAmount ?? '');
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function manejarEnvio(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setGuardando(true);
    try {
      await onGuardar({ name, foundedAt, location, category, fundingAmount });
    } catch (err) {
      setError(err instanceof ErrorApi ? err.detalles.join(' ') : 'No se pudo guardar.');
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={manejarEnvio} className="formulario">
      <h2>{startup ? 'Editar startup' : 'Nueva startup'}</h2>
      <label>
        Nombre
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        Fecha de fundación
        <input
          type="date"
          value={foundedAt}
          onChange={(e) => setFoundedAt(e.target.value)}
          required
        />
      </label>
      <label>
        Ubicación
        <input value={location} onChange={(e) => setLocation(e.target.value)} />
      </label>
      <label>
        Categoría
        <input value={category} onChange={(e) => setCategory(e.target.value)} />
      </label>
      <label>
        Monto de financiamiento
        <input
          type="number"
          step="0.01"
          min="0"
          value={fundingAmount}
          onChange={(e) => setFundingAmount(e.target.value)}
        />
      </label>
      {error && <p className="error">{error}</p>}
      <div className="acciones-formulario">
        <button type="submit" disabled={guardando}>
          {guardando ? 'Guardando…' : 'Guardar'}
        </button>
        <button type="button" onClick={onCancelar} disabled={guardando}>
          Cancelar
        </button>
      </div>
    </form>
  );
}
