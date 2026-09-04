// src/pages/LoginPage.tsx
import { useState } from 'react';
import type { FormEvent } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ErrorApi } from '../api/client';
import { useAuth } from '../auth/useAuth';

interface EstadoNavegacion {
  mensaje?: string;
}

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const mensajeInicial = (location.state as EstadoNavegacion | null)?.mensaje ?? null;

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function manejarEnvio(evento: FormEvent) {
    evento.preventDefault();
    setError(null);
    setCargando(true);
    try {
      await login(username, password);
      navigate('/startups');
    } catch (err) {
      setError(err instanceof ErrorApi ? err.detalles.join(' ') : 'No se pudo conectar con el servidor.');
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="pagina-login">
      <h1>Iniciar sesión</h1>
      {mensajeInicial && <p className="aviso">{mensajeInicial}</p>}
      <form onSubmit={manejarEnvio}>
        <label>
          Usuario
          <input value={username} onChange={(e) => setUsername(e.target.value)} required autoFocus />
        </label>
        <label>
          Contraseña
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={cargando}>
          {cargando ? 'Ingresando…' : 'Ingresar'}
        </button>
      </form>
    </div>
  );
}
