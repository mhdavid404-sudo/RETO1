// src/types/technology.ts
//
// Espejo en TypeScript de services/technologies/*/schemas.py.

export interface Technology {
  id: number;
  name: string;
  sector: string;
  description: string | null;
  adoptionLevel: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface CrearTechnologyInput {
  name: string;
  sector: string;
  description?: string;
  adoptionLevel?: string;
}

export interface ActualizarTechnologyInput {
  name?: string;
  sector?: string;
  description?: string;
  adoptionLevel?: string;
}
