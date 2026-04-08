import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

function inferRoleFromUsername(username) {
  if (!username) return "guest";
  if (username.includes("owner")) return "owner";
  if (username.includes("staff")) return "staff";
  if (username.includes("driver")) return "driver";
  return "customer";
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const cached = localStorage.getItem("frontend-auth-user");
    if (!cached) return null;
    try {
      return JSON.parse(cached);
    } catch {
      localStorage.removeItem("frontend-auth-user");
      return null;
    }
  });
  const [loading, setLoading] = useState(false);
  const [bootstrapping, setBootstrapping] = useState(true);

  useEffect(() => {
    localStorage.setItem("frontend-auth-user", JSON.stringify(user));
  }, [user]);

  useEffect(() => {
    let mounted = true;
    async function bootstrap() {
      if (!user?.username) {
        if (mounted) setBootstrapping(false);
        return;
      }
      try {
        const current = await api.users.currentUser();
        if (!current?.username && mounted) {
          setUser(null);
        }
      } catch {
        if (mounted) setUser(null);
      } finally {
        if (mounted) setBootstrapping(false);
      }
    }
    bootstrap();
    return () => {
      mounted = false;
    };
  }, []);

  async function login(payload) {
    setLoading(true);
    try {
      const result = await api.users.login(payload);
      const current = await api.users.currentUser();
      const username = current?.username || payload.username;
      const derivedRole = inferRoleFromUsername(username);
      setUser({
        id: result?.id ?? null,
        username,
        role: derivedRole,
        requires2FA: Boolean(result?.requires_2fa),
      });
      return result;
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    try {
      await api.users.logout();
    } catch {
      // If backend session is already gone, still clear local auth.
    }
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, loading, bootstrapping, login, logout, setUser }),
    [user, loading, bootstrapping]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

