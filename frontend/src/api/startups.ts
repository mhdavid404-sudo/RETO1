// src/api/startups.ts
//
// Llamadas al gateway especificas de Startups, sobre el cliente
// generico de api/client.ts. Rutas identicas al contrato del brief
// (seccion 6): /startups/create, /startups/read[/:id], /startups/update/:id,
// /startups/delete/:id.

import { peticionApi } from './client';
import type { ActualizarStartupInput, CrearStartupInput, Startup } from '../types/startup';

export interface FiltrosStartups {
  name?: string;
  category?: string;
}

export function listarStartups(filtros: FiltrosStartups = {}): Promise<Startup[]> {
  const params = new URLSearchParams();
  if (filtros.name) params.set('name', filtros.name);
  if (filtros.category) params.set('category', filtros.category);
  const query = params.toString();
  return peticionApi<Startup[]>(`/startups/read${query ? `?${query}` : ''}`);
}

export function obtenerStartup(id: number): Promise<Startup> {
  return peticionApi<Startup>(`/startups/read/${id}`);
}

export function crearStartup(datos: CrearStartupInput): Promise<Startup> {
  return peticionApi<Startup>('/startups/create', { method: 'POST', body: datos });
}

export function actualizarStartup(id: number, datos: ActualizarStartupInput): Promise<Startup> {
  return peticionApi<Startup>(`/startups/update/${id}`, { method: 'PUT', body: datos });
}

export function eliminarStartup(id: number): Promise<void> {
  return peticionApi<void>(`/startups/delete/${id}`, { method: 'DELETE' });
}
