import React, { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";

function parseRestaurantId(value) {
  const n = Number(String(value).trim());
  if (!Number.isInteger(n) || n <= 0) return null;
  return n;
}

function parseDiscountRate(value) {
  const n = Number(String(value).trim());
  if (!Number.isFinite(n)) return null;
  return n;
}

export default function DiscountsPage() {
  const { user } = useAuth();
  const isOwner = user?.role === "owner";

  const [createRate, setCreateRate] = useState("0.9");
  const [createCode, setCreateCode] = useState("");
  const [createRestaurantId, setCreateRestaurantId] = useState("");
  const [createBusy, setCreateBusy] = useState(false);
  const [createMessage, setCreateMessage] = useState("");
  const [createError, setCreateError] = useState("");

  const [deleteCode, setDeleteCode] = useState("");
  const [deleteBusy, setDeleteBusy] = useState(false);
  const [deleteMessage, setDeleteMessage] = useState("");
  const [deleteError, setDeleteError] = useState("");
  const [deleteConfirm, setDeleteConfirm] = useState(false);

  async function submitCreate(e) {
    e.preventDefault();
    setCreateMessage("");
    setCreateError("");
    const rid = parseRestaurantId(createRestaurantId);
    if (!rid) {
      setCreateError("Restaurant ID must be a positive whole number.");
      return;
    }
    const rate = parseDiscountRate(createRate);
    if (rate == null || rate <= 0) {
      setCreateError("Enter a valid price multiplier (for example, 0.85 for about 15% off).");
      return;
    }
    const code = createCode.trim().toUpperCase();
    if (!code || code.length < 2) {
      setCreateError("Code must be at least 2 characters.");
      return;
    }
    setCreateBusy(true);
    try {
      const res = await api.discounts.create({
        discount_rate: rate,
        discount_code: code,
        restaurant_id: rid,
      });
      setCreateMessage(typeof res?.message === "string" ? res.message : "Promo code created.");
      setCreateCode("");
    } catch (err) {
      setCreateError(err?.message || "Something went wrong. Try again.");
    } finally {
      setCreateBusy(false);
    }
  }

  async function submitDelete(e) {
    e.preventDefault();
    setDeleteMessage("");
    setDeleteError("");
    const code = deleteCode.trim();
    if (!code) {
      setDeleteError("Enter the code you want to remove.");
      return;
    }
    if (!deleteConfirm) {
      setDeleteError("Confirm below to remove this code.");
      return;
    }
    setDeleteBusy(true);
    try {
      const res = await api.discounts.remove(code);
      setDeleteMessage(typeof res?.message === "string" ? res.message : "Code removed.");
      setDeleteCode("");
      setDeleteConfirm(false);
    } catch (err) {
      setDeleteError(err?.message || "Could not remove that code.");
    } finally {
      setDeleteBusy(false);
    }
  }

  return (
    <section className="card discounts-page">
      <header className="page-header-block">
        <h1 className="page-title">Promos &amp; codes</h1>
        <p className="page-lede muted">
          Customers enter codes at checkout on the <Link to="/orders">Orders</Link> page. Restaurant owners can create
          or remove codes for their venue.
        </p>
      </header>

      <article className="panel">
        <h2 className="section-heading">Using a code</h2>
        <p className="muted small-print">
          Add food to your cart, open Orders, and apply your code before you place the order. The total updates to
          reflect your savings.
        </p>
        <Link className="button-link" to="/restaurants">
          Find food
        </Link>
      </article>

      {!user && (
        <article className="panel muted">
          <p>
            <strong>Restaurant owner?</strong> Sign in to manage promo codes for your restaurant.
          </p>
          <Link className="button-link" to="/login">
            Sign in
          </Link>
        </article>
      )}

      {user && !isOwner && (
        <article className="panel muted">
          <p>Creating and removing promo codes is limited to restaurant owner accounts.</p>
        </article>
      )}

      {isOwner && (
        <>
          <article className="panel owner-discount-panel">
            <h2 className="section-heading">Create a promo code</h2>
            <p className="muted small-print">
              Enter your restaurant&apos;s numeric ID and choose a code guests can type at checkout. Use a multiplier
              under 1 for a discount (for example, 0.85 means guests pay about 85% of the cart total).
            </p>
            <form className="discount-form" onSubmit={submitCreate}>
              <div className="row form-grid">
                <label className="field">
                  <span>Restaurant ID</span>
                  <input
                    inputMode="numeric"
                    value={createRestaurantId}
                    onChange={(e) => setCreateRestaurantId(e.target.value.replace(/\D/g, ""))}
                    placeholder="e.g. 1"
                    required
                  />
                </label>
                <label className="field">
                  <span>Price multiplier</span>
                  <input
                    value={createRate}
                    onChange={(e) => setCreateRate(e.target.value)}
                    placeholder="0.85"
                    required
                  />
                </label>
                <label className="field field-wide">
                  <span>Code</span>
                  <input
                    value={createCode}
                    onChange={(e) => setCreateCode(e.target.value.toUpperCase())}
                    placeholder="SAVE10"
                    autoComplete="off"
                    required
                  />
                </label>
              </div>
              <button type="submit" disabled={createBusy}>
                {createBusy ? "Creating…" : "Create code"}
              </button>
            </form>
            {createError && <p className="error">{createError}</p>}
            {createMessage && <p className="success">{createMessage}</p>}
          </article>

          <article className="panel owner-discount-panel">
            <h2 className="section-heading">Remove a code</h2>
            <p className="muted small-print">Enter the exact code you want to retire from your restaurant.</p>
            <form className="discount-form" onSubmit={submitDelete}>
              <div className="row">
                <input
                  placeholder="Code to remove"
                  value={deleteCode}
                  onChange={(e) => setDeleteCode(e.target.value.toUpperCase())}
                  disabled={deleteBusy}
                />
                <label className="checkbox-inline">
                  <input
                    type="checkbox"
                    checked={deleteConfirm}
                    onChange={(e) => setDeleteConfirm(e.target.checked)}
                    disabled={deleteBusy}
                  />
                  I want to remove this code
                </label>
              </div>
              <button type="submit" disabled={deleteBusy || !deleteCode.trim()}>
                {deleteBusy ? "Removing…" : "Remove code"}
              </button>
            </form>
            {deleteError && <p className="error">{deleteError}</p>}
            {deleteMessage && <p className="success">{deleteMessage}</p>}
          </article>
        </>
      )}
    </section>
  );
}
