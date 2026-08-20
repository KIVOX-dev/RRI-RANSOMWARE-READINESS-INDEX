import axios from "axios";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { AuthAPI } from "@/api/client";
import { apiErrorMessage, AUTH_EXPIRED_EVENT, clearToken, getToken, setToken } from "@/lib/api";
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
  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      return;
    }
    AuthAPI.me()
      .then(setUser)
      .catch((err) => {
        // Only a real 401 means the session is actually invalid/expired —
        // a transient network failure or a 5xx shouldn't silently wipe a
        // perfectly valid token and log the user out with no explanation.
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          clearToken();
          setUser(null);
        }
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    function handleAuthExpired() {
      setUser(null);
      navigate("/login");
    }
    window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);
    return () => window.removeEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired);
  }, [navigate]);

  async function login(email: string, password: string) {
    const result = await AuthAPI.login({ email, password });
    if (!result?.access_token || !result?.user) {
      throw new Error("Login response was missing an access token or user.");
    }
    setToken(result.access_token);
    setUser(result.user);
  }

  async function register(payload: RegisterPayload) {
    const result = await AuthAPI.register(payload);
    if (!result?.access_token || !result?.user) {
      throw new Error("Registration response was missing an access token or user.");
    }
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
