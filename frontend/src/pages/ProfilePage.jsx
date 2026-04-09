import React, { useEffect, useState } from "react";
import { api } from "../api/client";

export default function ProfilePage() {
  const [currentUser, setCurrentUser] = useState(null);
  const [addresses, setAddresses] = useState([]);
  const [addressInput, setAddressInput] = useState("");
  const [latInput, setLatInput] = useState("");
  const [lngInput, setLngInput] = useState("");
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
    if (!addressInput.trim() || !latInput.trim() || !lngInput.trim()) {
      setError("Enter an address, latitude, and longitude.");
      return;
    }
    const lat = parseFloat(latInput);
    const lng = parseFloat(lngInput);
    if (isNaN(lat) || isNaN(lng)) {
      setError("Latitude and longitude must be numbers.");
      return;
    }
    try {
      await api.users.addAddress(addressInput.trim(), lat, lng);
      setAddressInput("");
      setLatInput("");
      setLngInput("");
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card profile-page">
      <header className="page-header-block">
        <h1 className="page-title">Profile</h1>
        <p className="page-lede muted">Your account and saved addresses.</p>
      </header>

      <div className="row profile-toolbar">
        <button type="button" onClick={load} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {currentUser && (
        <article className="panel profile-summary">
          <h2 className="section-heading">Account</h2>
          {currentUser.username == null && currentUser.email == null && currentUser.name == null ? (
            <p className="muted">We couldn&apos;t load profile details. Try refreshing.</p>
          ) : (
            <dl className="app-data-summary__dl">
              {currentUser.username != null && (
                <div className="app-data-summary__row">
                  <dt>Username</dt>
                  <dd>{String(currentUser.username)}</dd>
                </div>
              )}
              {currentUser.email != null && String(currentUser.email).trim() !== "" && (
                <div className="app-data-summary__row">
                  <dt>Email</dt>
                  <dd>{String(currentUser.email)}</dd>
                </div>
              )}
              {currentUser.name != null && String(currentUser.name).trim() !== "" && (
                <div className="app-data-summary__row">
                  <dt>Name</dt>
                  <dd>{String(currentUser.name)}</dd>
                </div>
              )}
            </dl>
          )}
        </article>
      )}

      <article className="panel">
        <h2 className="section-heading">Addresses</h2>
        <div className="row">
          <input
            placeholder="Street, city, postal code"
            value={addressInput}
            onChange={(e) => setAddressInput(e.target.value)}
            aria-label="New address"
          />
          <input
            placeholder="Latitude (e.g. 40.7128)"
            value={latInput}
            onChange={(e) => setLatInput(e.target.value)}
            aria-label="Latitude"
            style={{ maxWidth: "120px" }}
          />
          <input
            placeholder="Longitude (e.g. -74.0060)"
            value={lngInput}
            onChange={(e) => setLngInput(e.target.value)}
            aria-label="Longitude"
            style={{ maxWidth: "120px" }}
          />
          <button type="button" disabled={!addressInput.trim() || !latInput.trim() || !lngInput.trim()} onClick={addAddress}>
            Save address
          </button>
        </div>
        {addresses.length === 0 ? (
          <p className="muted">No saved addresses yet.</p>
        ) : (
          <ul className="profile-address-list">
            {addresses.map((addr, idx) => (
              <li key={idx}>
                {typeof addr === "string" ? addr : addr.address}
              </li>
            ))}
          </ul>
        )}
      </article>

      {error && (
        <p className="error app-inline-alert" role="alert">
          {error}
        </p>
      )}
    </section>
  );
}
