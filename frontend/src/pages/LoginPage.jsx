import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";

export default function LoginPage() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [twoFactorCode, setTwoFactorCode] = useState("");
  const [needs2FA, setNeeds2FA] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    try {
      const result = await login(form);
      if (result?.requires_2fa) {
        await api.users.generate2FA();
        setNeeds2FA(true);
        return;
      }
      navigate("/orders");
    } catch (err) {
      setError(err.message);
    }
  }

  async function verify2FA() {
    setError("");
    try {
      await api.users.verify2FA(twoFactorCode);
      navigate("/orders");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>Login</h2>
      <form className="grid" onSubmit={onSubmit}>
        <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button disabled={loading}>{loading ? "Signing in..." : "Sign in"}</button>
      </form>
      {needs2FA && (
        <div className="panel">
          <h3>Two-factor verification</h3>
          <input placeholder="6-digit code" value={twoFactorCode} onChange={(e) => setTwoFactorCode(e.target.value)} />
          <button onClick={verify2FA}>Verify 2FA</button>
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  );
}

