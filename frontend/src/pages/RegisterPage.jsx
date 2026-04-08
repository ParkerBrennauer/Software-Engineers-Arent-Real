import React, { useState } from "react";
import { api } from "../api/client";

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: "",
    name: "",
    role: "customer",
    username: "",
    password: "",
    payment_type: "credit card",
    payment_details: "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    try {
      const payload = { ...form };
      if (form.role === "customer") {
        if (!/^\d{15,16}$/.test(form.payment_details)) {
          setError("Card number must be 15 or 16 digits.");
          return;
        }
        await api.users.registerCustomer(payload);
      }
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
        {form.role === "customer" && (
          <>
            <select
              value={form.payment_type}
              onChange={(e) => setForm({ ...form, payment_type: e.target.value })}
            >
              <option value="credit card">Credit Card</option>
              <option value="debit card">Debit Card</option>
            </select>
            <input
              placeholder="Card number (15-16 digits)"
              inputMode="numeric"
              value={form.payment_details}
              onChange={(e) =>
                setForm({
                  ...form,
                  payment_details: e.target.value.replace(/\D/g, ""),
                })
              }
            />
          </>
        )}
        <button>Create account</button>
      </form>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}
    </section>
  );
}

