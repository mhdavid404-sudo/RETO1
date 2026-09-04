// src/components/NavBar.tsx
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

export function NavBar() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="barra-navegacion">
      <span className="marca">RETO1</span>
      <Link to="/startups">Startups</Link>
      {isAuthenticated ? (
        <button type="button" onClick={logout}>
          Cerrar sesión
        </button>
      ) : (
        <Link to="/login">Iniciar sesión</Link>
      )}
    </nav>
  );
}
