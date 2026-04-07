import { createContext, useContext, useMemo, useState } from 'react';

const STORAGE_KEY = 'food-delivery-auth';

const AuthContext = createContext(null);

function loadInitialAuthState() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return { user: null };
    }
    const parsed = JSON.parse(raw);
    return { user: parsed.user || null };
  } catch {
    return { user: null };
  }
}

export function AuthProvider({ children }) {
  const [{ user }, setState] = useState(loadInitialAuthState);

  const setUser = (nextUser) => {
    const nextState = { user: nextUser };
    setState(nextState);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextState));
  };

  const logout = () => {
    setState({ user: null });
    window.localStorage.removeItem(STORAGE_KEY);
  };

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      setUser,
      logout,
    }),
    [user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
