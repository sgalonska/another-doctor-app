export * from './schemas';

// Utility functions for API handling
export const API_ENDPOINTS = {
  CASES: '/api/v1/cases',
  DOCTORS: '/api/v1/doctors',
  MATCHING: '/api/v1/matching',
  UPLOAD: '/api/v1/upload',
} as const;

// Common HTTP client utilities
export interface APIResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export async function handleAPIResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new APIError(
      errorData.message || `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }
  
  return response.json();
}

// Date utilities for medical case handling
export function formatDateAnchor(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  return `${year}-${month}`;
}

export function parseDateAnchor(dateAnchor: string): Date {
  const [year, month] = dateAnchor.split('-').map(Number);
  return new Date(year, month - 1, 1);
}

// Validation helpers
export function isValidNCTId(nctId: string): boolean {
  return /^NCT[0-9]{8}$/.test(nctId);
}

export function isValidPMID(pmid: string): boolean {
  return /^[0-9]+$/.test(pmid);
}

export function isValidDOI(doi: string): boolean {
  return /^10\.[0-9]+\/.+/.test(doi);
}