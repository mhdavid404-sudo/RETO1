// src/auth/useAuth.ts
//
// Separado de AuthContext.tsx (que solo exporta el componente
// AuthProvider) para que React Fast Refresh funcione correctamente —
// un archivo que exporta un componente y tambien un hook rompe el
// fast-refresh de Vite.

import { useContext } from 'react';
import { AuthContext } from './context';

export function useAuth() {
  const contexto = useContext(AuthContext);
  if (!contexto) {
    throw new Error('useAuth debe usarse dentro de <AuthProvider>.');
  }
  return contexto;
}
