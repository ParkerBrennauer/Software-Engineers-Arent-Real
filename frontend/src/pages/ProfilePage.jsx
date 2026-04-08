import React, { useEffect, useState } from "react";
import { api } from "../api/client";

export default function ProfilePage() {
  const [currentUser, setCurrentUser] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [addressInput, setAddressInput] = useState("");
  const [error, setError] = useState("");

  async function load() {
    setError("");
    try {
      setCurrentUser(await api.users.currentUser());
      setAddresses(await api.users.getAddresses());
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function addAddress() {
    setError("");
    try {
      await api.users.addAddress(addressInput);
      setAddressInput("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>Profile and customer data</h2>
      <button onClick={load}>Refresh profile</button>
      {currentUser && <pre className="json">{JSON.stringify(currentUser, null, 2)}</pre>}
      <div className="row">
        <input placeholder="Add address" value={addressInput} onChange={(e) => setAddressInput(e.target.value)} />
        <button onClick={addAddress}>Save address</button>
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

