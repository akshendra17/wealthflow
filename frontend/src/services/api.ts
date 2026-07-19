/**
 * WealthFlow API service — fetch wrapper for backend communication.
 */

import type { Statement, Transaction, User, Category, MonthlySummary } from '../types';

const API_BASE = '/api/v1';

let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

interface RequestOptions extends RequestInit {
  headers?: Record<string, string>;
}

async function request<T>(endpoint: string, options: RequestOptions = {}, isRetry = false): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const config: RequestOptions = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    credentials: 'include',
    ...options,
  };

  if (accessToken) {
    config.headers!['Authorization'] = `Bearer ${accessToken}`;
  }

  // Don't set content-type for FormData (file uploads)
  if (options.body instanceof FormData) {
    delete config.headers!['Content-Type'];
  }

  let response = await fetch(url, config);

  // Handle 401 Unauthorized for token refresh
  if (response.status === 401 && !isRetry && endpoint !== '/auth/login' && endpoint !== '/auth/refresh') {
    try {
      const refreshResponse = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      });

      if (refreshResponse.ok) {
        const data = await refreshResponse.json();
        accessToken = data.access_token;
        
        // Retry the original request
        config.headers!['Authorization'] = `Bearer ${accessToken}`;
        response = await fetch(url, config);
      } else {
        // Refresh failed, clear token and let the 401 propagate
        accessToken = null;
      }
    } catch (err) {
      accessToken = null;
    }
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: { message: 'Network error' } }));
    throw new Error(error.error?.message || error.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) return null as unknown as T;
  return response.json();
}

// ── Auth ──
export async function login(email: string, password: string): Promise<{ access_token: string, token_type: string, user: User }> {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function registerUser(name: string, email: string, password: string): Promise<{ access_token: string, token_type: string, user: User }> {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ name, email, password }),
  });
}

export async function getCurrentUser(): Promise<User> {
  return request('/auth/me');
}

export async function logoutUser(): Promise<void> {
  accessToken = null;
  return request('/auth/logout', { method: 'POST' });
}


// ── Statements ──
export async function uploadStatement(file: File, bankName: string | null = null): Promise<Statement> {
  const formData = new FormData();
  formData.append('file', file);
  if (bankName) {
    formData.append('bank_name', bankName);
  }
  return request('/statements/upload', { method: 'POST', body: formData });
}

export async function getStatements(): Promise<Statement[]> {
  return request('/statements/');
}

export async function getStatement(id: string): Promise<Statement> {
  return request(`/statements/${id}`);
}

export async function deleteStatement(id: string): Promise<void> {
  return request(`/statements/${id}`, { method: 'DELETE' });
}

export async function deleteAllStatements(): Promise<void> {
  return request('/statements/all', { method: 'DELETE' });
}

// ── Transactions ──
interface TransactionParams {
  page?: number;
  pageSize?: number;
  category?: string;
  month?: number;
  year?: number;
  type?: string;
  search?: string;
  bankName?: string;
}

export async function getTransactions(params: TransactionParams = {}): Promise<{ items: Transaction[], total: number }> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set('page', params.page.toString());
  if (params.pageSize) searchParams.set('page_size', params.pageSize.toString());
  if (params.category) searchParams.set('category', params.category);
  if (params.month) searchParams.set('month', params.month.toString());
  if (params.year) searchParams.set('year', params.year.toString());
  if (params.type) searchParams.set('transaction_type', params.type);
  if (params.search) searchParams.set('search', params.search);
  if (params.bankName) searchParams.set('bank_name', params.bankName);
  
  const query = searchParams.toString();
  return request(`/transactions/${query ? `?${query}` : ''}`);
}

export async function categorizeTransaction(id: string, category: string, subcategory: string | null = null): Promise<Transaction> {
  return request(`/transactions/${id}/categorize`, {
    method: 'PATCH',
    body: JSON.stringify({ category, subcategory }),
  });
}

// ── Analytics ──
export async function getDashboard(bankName?: string): Promise<any> { // Typing can be refined based on backend response
  const query = bankName ? `?bank_name=${bankName}` : '';
  return request(`/analytics/dashboard${query}`);
}

export async function getMonthlySummary(year: number, month: number, bankName?: string): Promise<MonthlySummary[]> {
  const query = bankName ? `&bank_name=${bankName}` : '';
  return request(`/analytics/monthly-summary?year=${year}&month=${month}${query}`);
}

export async function getCategoryBreakdown(year: number, month: number, bankName?: string): Promise<any> {
  const query = bankName ? `&bank_name=${bankName}` : '';
  return request(`/analytics/category-breakdown?year=${year}&month=${month}${query}`);
}

export async function getTrends(months: number = 6, bankName?: string): Promise<any> {
  const query = bankName ? `&bank_name=${bankName}` : '';
  return request(`/analytics/trends?months=${months}${query}`);
}

// ── Categories ──
export async function getCategories(): Promise<Category[]> {
  return request('/categories/');
}

export async function createCategory(data: Partial<Category>): Promise<Category> {
  return request('/categories/', { method: 'POST', body: JSON.stringify(data) });
}
