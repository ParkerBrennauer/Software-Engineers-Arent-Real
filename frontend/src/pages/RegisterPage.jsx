import React, { useState } from "react";
import { api } from "../api/client";

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: "",
    name: "",
    role: "customer",
    username: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    try {
      const payload = { ...form };
      if (form.role === "customer") await api.users.registerCustomer(payload);
      else if (form.role === "driver") await api.users.registerDriver(payload);
      else await api.users.register(payload);
      setMessage("Account created. You can now log in.");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>Create account</h2>
      <form className="grid" onSubmit={submit}>
        <input placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <select value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="customer">Customer</option>
          <option value="driver">Driver</option>
          <option value="owner">Owner</option>
          <option value="staff">Staff</option>
        </select>
        <input placeholder="Username" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        <button>Create account</button>
      </form>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
}

