export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

export interface Statement {
  id: string;
  original_filename: string;
  file_type: string;
  bank_name?: string;
  statement_month?: number;
  statement_year?: number;
  total_transactions: number;
  total_debit: number;
  total_credit: number;
  uploaded_at: string;
}

export interface Transaction {
  id: string;
  transaction_date: string;
  description: string;
  amount: number;
  transaction_type: 'DEBIT' | 'CREDIT';
  category: string;
  subcategory?: string;
}

export interface Category {
  id: string;
  name: string;
  icon?: string;
  color?: string;
}

export interface MonthlySummary {
  year: number;
  month: number;
  category: string;
  total_amount: number;
  transaction_count: number;
}
