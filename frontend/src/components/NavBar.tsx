// src/components/NavBar.tsx
import { NavLink } from 'react-router-dom';
import { useAuth } from '../auth/useAuth';

function claseEnlace({ isActive }: { isActive: boolean }): string {
  return isActive ? 'activo' : '';
}

export function NavBar() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <nav className="barra-navegacion">
      <span className="marca">RETO1</span>
      <NavLink to="/startups" className={claseEnlace}>
        Startups
      </NavLink>
      <NavLink to="/technologies" className={claseEnlace}>
        Technologies
      </NavLink>
      {isAuthenticated ? (
        <button type="button" onClick={logout}>
          Cerrar sesión
        </button>
      ) : (
        <NavLink to="/login" className={claseEnlace}>
          Iniciar sesión
        </NavLink>
      )}
    </nav>
  );
}
