import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { login as apiLogin, registerUser as apiRegister, setAccessToken, logoutUser, refreshSession } from '../services/api';
import type { User } from '../types';

export interface AuthResponse {
  success: boolean;
  error?: string;
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<AuthResponse>;
  register: (name: string, email: string, password: string) => Promise<AuthResponse>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const session = await refreshSession();
        if (!session) return;
        setUser(session.user);
        setIsAuthenticated(true);
      } catch {
        // Expected when logged out or API unreachable
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string): Promise<AuthResponse> => {
    try {
      const data = await apiLogin(email, password);
      setAccessToken(data.access_token);
      setUser(data.user);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  };

  const register = async (name: string, email: string, password: string): Promise<AuthResponse> => {
    try {
      const data = await apiRegister(name, email, password);
      setAccessToken(data.access_token);
      setUser(data.user);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await logoutUser();
    } catch (err) {
      console.error('Logout error', err);
    }
    setAccessToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: 'var(--color-bg)' }}>
        <div className="loading-spinner" />
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
