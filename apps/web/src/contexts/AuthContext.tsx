"use client";

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react";

interface User {
  id: string;
  email: string;
  name: string;
  apiKey: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (email: string, password: string, name: string) => Promise<void>;
  signOut: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const STORAGE_KEY = "dialectica_user";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setLoading(false);
  }, []);

  const signIn = useCallback(async (email: string, _password: string) => {
    // Simple auth — store email as user identity
    // In production, replace with Supabase/Auth0/Clerk
    const u: User = {
      id: crypto.randomUUID().slice(0, 8),
      email,
      name: email.split("@")[0],
      apiKey: `sk-${crypto.randomUUID().replace(/-/g, "").slice(0, 32)}`,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
    localStorage.setItem("dialectica_api_key", u.apiKey);
    setUser(u);
  }, []);

  const signUp = useCallback(async (email: string, password: string, name: string) => {
    const u: User = {
      id: crypto.randomUUID().slice(0, 8),
      email,
      name,
      apiKey: `sk-${crypto.randomUUID().replace(/-/g, "").slice(0, 32)}`,
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
    localStorage.setItem("dialectica_api_key", u.apiKey);
    setUser(u);
  }, []);

  const signOut = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem("dialectica_api_key");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
