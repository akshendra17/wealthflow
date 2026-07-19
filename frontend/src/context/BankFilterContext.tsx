import { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';

interface BankFilterContextType {
  bankName: string;
  setBankName: (name: string) => void;
}

const BankFilterContext = createContext<BankFilterContextType | undefined>(undefined);

export function BankFilterProvider({ children }: { children: ReactNode }) {
  const [bankName, setBankName] = useState<string>('');

  return (
    <BankFilterContext.Provider value={{ bankName, setBankName }}>
      {children}
    </BankFilterContext.Provider>
  );
}

export function useBankFilter() {
  const context = useContext(BankFilterContext);
  if (context === undefined) {
    throw new Error('useBankFilter must be used within a BankFilterProvider');
  }
  return context;
}
