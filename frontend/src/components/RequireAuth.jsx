import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../state/AuthContext";

export default function RequireAuth({ children, roles }) {
  const { user, bootstrapping } = useAuth();
  if (bootstrapping) return <section className="card">Checking session...</section>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.requires2FA) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
}

