// src/auth/context.ts
//
// Solo el contexto y su tipo — separado de AuthContext.tsx (el
// componente AuthProvider) y de useAuth.ts (el hook), para que React
// Fast Refresh funcione: un archivo que mezcla un componente con
// otros exports (contexto, hooks) rompe el fast-refresh de Vite.

import { createContext } from 'react';

export interface AuthContextValor {
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValor | null>(null);
