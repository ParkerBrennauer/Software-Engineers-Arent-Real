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
    return cached ? JSON.parse(cached) : null;
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    localStorage.setItem("frontend-auth-user", JSON.stringify(user));
  }, [user]);

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
    await api.users.logout();
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, loading, login, logout, setUser }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

