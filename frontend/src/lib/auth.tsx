import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { AuthAPI } from "@/api/client";
import { apiErrorMessage, clearToken, getToken, setToken } from "@/lib/api";
import type { User } from "@/types";

interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  organisation: { name: string; sector: string; size?: string; location?: string; parent_organisation_id?: string };
  language: string;
}

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    AuthAPI.me()
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setLoading(false));
  }, []);

  async function login(email: string, password: string) {
    const result = await AuthAPI.login({ email, password });
    setToken(result.access_token);
    setUser(result.user);
  }

  async function register(payload: RegisterPayload) {
    const result = await AuthAPI.register(payload);
    setToken(result.access_token);
    setUser(result.user);
  }

  function logout() {
    clearToken();
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

export { apiErrorMessage };

export function useRequireAuth() {
  const { user, loading } = useAuth();
  const navigate = useNavigate();
  useEffect(() => {
    if (!loading && !user) navigate("/login");
  }, [loading, user, navigate]);
  return { user, loading };
}
