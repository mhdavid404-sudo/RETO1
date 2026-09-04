// src/components/TechnologyForm.tsx
//
// Mismo patron que StartupForm.tsx: reutilizado para crear y editar,
// actualizacion "completa" (envia todos los campos del formulario) —
// ver el comentario de StartupForm.tsx para el detalle de esa decision.

import { useState } from 'react';
import type { FormEvent } from 'react';
import { ErrorApi } from '../api/client';
import type { Technology } from '../types/technology';

export interface DatosFormularioTechnology {
  name: string;
  sector: string;
  description: string;
  adoptionLevel: string;
}

interface Props {
  technology?: Technology;
  onGuardar: (datos: DatosFormularioTechnology) => Promise<void>;
  onCancelar: () => void;
}

export function TechnologyForm({ technology, onGuardar, onCancelar }: Props) {
  const [name, setName] = useState(technology?.name ?? '');
  const [sector, setSector] = useState(technology?.sector ?? '');
  const [description, setDescription] = useState(technology?.description ?? '');
  const [adoptionLevel, setAdoptionLevel] = useState(technology?.adoptionLevel ?? '');
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function manejarEnvio(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setGuardando(true);
    try {
      await onGuardar({ name, sector, description, adoptionLevel });
    } catch (err) {
      setError(err instanceof ErrorApi ? err.detalles.join(' ') : 'No se pudo guardar.');
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={manejarEnvio} className="formulario">
      <h2>{technology ? 'Editar tecnología' : 'Nueva tecnología'}</h2>
      <label>
        Nombre
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        Sector
        <input value={sector} onChange={(e) => setSector(e.target.value)} required />
      </label>
      <label>
        Descripción
        <input value={description} onChange={(e) => setDescription(e.target.value)} />
      </label>
      <label>
        Nivel de adopción
        <input value={adoptionLevel} onChange={(e) => setAdoptionLevel(e.target.value)} />
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
