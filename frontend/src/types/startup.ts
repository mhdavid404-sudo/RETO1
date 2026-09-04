// src/types/startup.ts
//
// Espejo en TypeScript de services/startups/*/schemas.py — camelCase,
// igual que el contrato de la API (brief seccion 6).

export interface Startup {
  id: number;
  name: string;
  foundedAt: string; // fecha ISO (YYYY-MM-DD)
  location: string | null;
  category: string | null;
  fundingAmount: string | null; // Decimal serializado como string por Pydantic
  createdAt: string;
  updatedAt: string;
}

export interface CrearStartupInput {
  name: string;
  foundedAt: string;
  location?: string;
  category?: string;
  fundingAmount?: number;
}

export interface ActualizarStartupInput {
  name?: string;
  foundedAt?: string;
  location?: string;
  category?: string;
  fundingAmount?: number;
}
