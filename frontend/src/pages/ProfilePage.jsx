import React, { useEffect, useState } from "react";
import { api } from "../api/client";

export default function ProfilePage() {
  const [currentUser, setCurrentUser] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [addressInput, setAddressInput] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const [current, addr] = await Promise.all([api.users.currentUser(), api.users.getAddresses()]);
      setCurrentUser(current);
      setAddresses(Array.isArray(addr) ? addr : []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    let active = true;
    async function init() {
      setLoading(true);
      setError("");
      try {
        const [current, addr] = await Promise.all([api.users.currentUser(), api.users.getAddresses()]);
        if (!active) return;
        setCurrentUser(current);
        setAddresses(Array.isArray(addr) ? addr : []);
      } catch (err) {
        if (active) setError(err.message);
      } finally {
        if (active) setLoading(false);
      }
    }
    init();
    return () => {
      active = false;
    };
  }, []);

  async function addAddress() {
    setError("");
    if (!addressInput.trim()) {
      setError("Address is required.");
      return;
    }
    try {
      await api.users.addAddress(addressInput.trim());
      setAddressInput("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>Profile and customer data</h2>
      <button onClick={load} disabled={loading}>{loading ? "Refreshing..." : "Refresh profile"}</button>
      {currentUser && <pre className="json">{JSON.stringify(currentUser, null, 2)}</pre>}
      <div className="row">
        <input placeholder="Add address" value={addressInput} onChange={(e) => setAddressInput(e.target.value)} />
        <button disabled={!addressInput.trim()} onClick={addAddress}>Save address</button>
      </div>
      <h3>Saved addresses</h3>
      <ul>
        {addresses.map((address) => (
          <li key={address}>{address}</li>
        ))}
      </ul>
      {error && <p className="error">{error}</p>}
    </section>
  );
}

