// src/auth/AuthContext.tsx
//
// Estado de autenticacion global. isAuthenticated es simplemente "hay
// un token guardado" — no se valida su firma ni expiracion en el
// cliente, eso lo hace el backend en cada peticion protegida.

import { useCallback, useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  borrarToken,
  guardarToken,
  obtenerToken,
  peticionApi,
  registrarManejador401,
} from '../api/client';
import { AuthContext } from './context';

interface RespuestaLogin {
  token: string;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => obtenerToken());
  const navigate = useNavigate();

  useEffect(() => {
    registrarManejador401(() => {
      setToken(null);
      navigate('/login', {
        state: {
          mensaje: 'Tu sesion expiro o no has iniciado sesion. Inicia sesion para continuar.',
        },
      });
    });
  }, [navigate]);

  const login = useCallback(async (username: string, password: string) => {
    const respuesta = await peticionApi<RespuestaLogin>('/auth/login', {
      method: 'POST',
      body: { username, password },
      omitirManejador401: true,
    });
    guardarToken(respuesta.token);
    setToken(respuesta.token);
  }, []);

  const logout = useCallback(() => {
    borrarToken();
    setToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated: token !== null, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
