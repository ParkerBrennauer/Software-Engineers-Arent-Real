import React, { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "../api/client";

const AuthContext = createContext(null);

function inferRoleFromUsername(username) {
  if (!username) return "guest";
  const lower = String(username).toLowerCase();
  if (lower.includes("owner")) return "owner";
  if (lower.includes("staff")) return "staff";
  if (lower.includes("driver")) return "driver";
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
    if (!user) {
      localStorage.removeItem("frontend-auth-user");
      return;
    }
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
      const requires2FA = Boolean(result?.requires_2fa);
      setUser({
        id: result?.id ?? null,
        username,
        role: derivedRole,
        requires2FA,
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

  function completeTwoFactor() {
    setUser((prev) => (prev ? { ...prev, requires2FA: false } : prev));
  }

  const value = useMemo(
    () => ({ user, loading, bootstrapping, login, logout, setUser, completeTwoFactor }),
    [user, loading, bootstrapping]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

