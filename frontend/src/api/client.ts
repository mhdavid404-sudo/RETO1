// src/api/client.ts
//
// Cliente HTTP centralizado: unico punto por el que pasan TODAS las
// peticiones al gateway. Arma la URL sobre VITE_API_BASE_URL, agrega
// el header Authorization cuando hay token guardado, y centraliza el
// manejo de 401 — nadie mas en la app arma headers o construye la URL
// del gateway a mano (evita logica duplicada, mismo criterio que
// shared/ en el backend).
//
// Diseno del token (confirmado antes de construir, ver
// docs/DECISIONES.md): se guarda en localStorage bajo una sola clave.
// No se decodifica el JWT en el cliente ni se revisa `exp` aqui — el
// backend ya lo valida. "Nunca hizo login" y "el token expiro" se
// tratan igual: se deja salir la peticion, y si el gateway responde
// 401 se limpia el token guardado y se avisa via registrarManejador401
// (conectado desde AuthContext) — un solo camino para ambos casos.

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!BASE_URL) {
  throw new Error(
    'Falta la variable de entorno VITE_API_BASE_URL (ver .env.example).',
  );
}

const CLAVE_TOKEN = 'reto1_token';

export function obtenerToken(): string | null {
  return localStorage.getItem(CLAVE_TOKEN);
}

export function guardarToken(token: string): void {
  localStorage.setItem(CLAVE_TOKEN, token);
}

export function borrarToken(): void {
  localStorage.removeItem(CLAVE_TOKEN);
}

/** Error de la API — mismo formato uniforme {message, details} de shared/errors.py. */
export class ErrorApi extends Error {
  status: number;
  detalles: string[];

  constructor(status: number, detalles: string[], message: string) {
    super(message);
    this.status = status;
    this.detalles = detalles;
  }
}

// Un solo listener global para 401, registrado una vez desde
// AuthProvider al montar la app (necesita useNavigate, que solo existe
// dentro del Router — por eso no vive aqui directamente).
let manejador401: (() => void) | null = null;
export function registrarManejador401(fn: () => void): void {
  manejador401 = fn;
}

interface OpcionesPeticion {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  body?: unknown;
  /**
   * Solo para /auth/login: un 401 ahi es "credenciales incorrectas",
   * no "sesion expirada" — la pagina de login ya maneja ese error por
   * su cuenta, no debe disparar el redirect global.
   */
  omitirManejador401?: boolean;
}

export async function peticionApi<T>(
  ruta: string,
  opciones: OpcionesPeticion = {},
): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = obtenerToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const respuesta = await fetch(`${BASE_URL}${ruta}`, {
    method: opciones.method ?? 'GET',
    headers,
    body: opciones.body !== undefined ? JSON.stringify(opciones.body) : undefined,
  });

  if (respuesta.status === 401 && !opciones.omitirManejador401) {
    borrarToken();
    manejador401?.();
  }

  if (respuesta.status === 204) {
    return undefined as T;
  }

  const datos = await respuesta.json().catch(() => null);

  if (!respuesta.ok) {
    const mensaje: string = datos?.message ?? 'Error de la API';
    const detalles: string[] = datos?.details ?? [mensaje];
    throw new ErrorApi(respuesta.status, detalles, mensaje);
  }

  return datos as T;
}
