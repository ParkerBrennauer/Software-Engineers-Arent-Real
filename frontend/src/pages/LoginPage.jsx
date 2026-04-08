import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";

export default function LoginPage() {
  const { login, loading, completeTwoFactor } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [twoFactorCode, setTwoFactorCode] = useState("");
  const [needs2FA, setNeeds2FA] = useState(false);
  const [verifying2FA, setVerifying2FA] = useState(false);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    if (!form.username.trim() || !form.password.trim()) {
      setError("Username and password are required.");
      return;
    }
    try {
      const result = await login(form);
      if (result?.requires_2fa) {
        await api.users.generate2FA();
        setNeeds2FA(true);
        return;
      }
      navigate("/restaurants");
    } catch (err) {
      setError(err.message);
    }
  }

  async function verify2FA() {
    setError("");
    if (!/^\d{6}$/.test(twoFactorCode.trim())) {
      setError("2FA code must be 6 digits.");
      return;
    }
    setVerifying2FA(true);
    try {
      await api.users.verify2FA(twoFactorCode.trim());
      completeTwoFactor();
      navigate("/restaurants");
    } catch (err) {
      setError(err.message);
    } finally {
      setVerifying2FA(false);
    }
  }

  return (
    <section className="card">
      <h2>Login</h2>
      <form className="grid" onSubmit={onSubmit}>
        <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button disabled={loading || !form.username.trim() || !form.password.trim()}>
          {loading ? "Signing in..." : "Sign in"}
        </button>
      </form>
      {needs2FA && (
        <div className="panel">
          <h3>Two-factor verification</h3>
          <input
            placeholder="6-digit code"
            inputMode="numeric"
            value={twoFactorCode}
            onChange={(e) => setTwoFactorCode(e.target.value.replace(/\D/g, "").slice(0, 6))}
          />
          <button disabled={verifying2FA || twoFactorCode.trim().length !== 6} onClick={verify2FA}>
            {verifying2FA ? "Verifying..." : "Verify 2FA"}
          </button>
        </div>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  );
}

