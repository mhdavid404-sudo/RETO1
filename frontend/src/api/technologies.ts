// src/api/technologies.ts
//
// Llamadas al gateway especificas de Technologies, mismo patron que
// api/startups.ts. Filtros del contrato (brief seccion 6): sector y
// adoptionLevel, sin filtro por name a diferencia de startups.

import { peticionApi } from './client';
import type {
  ActualizarTechnologyInput,
  CrearTechnologyInput,
  Technology,
} from '../types/technology';

export interface FiltrosTechnologies {
  sector?: string;
  adoptionLevel?: string;
}

export function listarTechnologies(filtros: FiltrosTechnologies = {}): Promise<Technology[]> {
  const params = new URLSearchParams();
  if (filtros.sector) params.set('sector', filtros.sector);
  if (filtros.adoptionLevel) params.set('adoptionLevel', filtros.adoptionLevel);
  const query = params.toString();
  return peticionApi<Technology[]>(`/technologies/read${query ? `?${query}` : ''}`);
}

export function obtenerTechnology(id: number): Promise<Technology> {
  return peticionApi<Technology>(`/technologies/read/${id}`);
}

export function crearTechnology(datos: CrearTechnologyInput): Promise<Technology> {
  return peticionApi<Technology>('/technologies/create', { method: 'POST', body: datos });
}

export function actualizarTechnology(
  id: number,
  datos: ActualizarTechnologyInput,
): Promise<Technology> {
  return peticionApi<Technology>(`/technologies/update/${id}`, { method: 'PUT', body: datos });
}

export function eliminarTechnology(id: number): Promise<void> {
  return peticionApi<void>(`/technologies/delete/${id}`, { method: 'DELETE' });
}
