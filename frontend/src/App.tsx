// src/App.tsx
import { Navigate, Route, Routes } from 'react-router-dom';
import { NavBar } from './components/NavBar';
import { LoginPage } from './pages/LoginPage';
import { StartupsPage } from './pages/StartupsPage';
import { TechnologiesPage } from './pages/TechnologiesPage';

export function App() {
  return (
    <>
      <NavBar />
      <main className="contenido">
        <Routes>
          <Route path="/" element={<Navigate to="/startups" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/startups" element={<StartupsPage />} />
          <Route path="/technologies" element={<TechnologiesPage />} />
        </Routes>
      </main>
    </>
  );
}
