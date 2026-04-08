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
      setCreateError("Discount rate must be a positive number (price multiplier, e.g. 0.85).");
      return;
    }
    const code = createCode.trim().toUpperCase();
    if (!code || code.length < 2) {
      setCreateError("Discount code must be at least 2 characters.");
      return;
    }
    setCreateBusy(true);
    try {
      const res = await api.discounts.create({
        discount_rate: rate,
        discount_code: code,
        restaurant_id: rid,
      });
      setCreateMessage(typeof res?.message === "string" ? res.message : "Discount created.");
      setCreateCode("");
    } catch (err) {
      setCreateError(err?.message || "Create failed.");
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
      setDeleteError("Enter the discount code to remove.");
      return;
    }
    if (!deleteConfirm) {
      setDeleteError("Check the box to confirm removal.");
      return;
    }
    setDeleteBusy(true);
    try {
      const res = await api.discounts.remove(code);
      setDeleteMessage(typeof res?.message === "string" ? res.message : "Discount removed.");
      setDeleteCode("");
      setDeleteConfirm(false);
    } catch (err) {
      setDeleteError(err?.message || "Remove failed.");
    } finally {
      setDeleteBusy(false);
    }
  }

  return (
    <section className="card">
      <h2>Discounts</h2>
      <p className="muted">
        This page mirrors the backend discount API. There is no public endpoint to list codes—owners manage codes here;
        customers enter a code at checkout on the <Link to="/orders">Orders</Link> page cart.
      </p>

      <article className="panel discount-info">
        <h3>How it works</h3>
        <ul className="muted list-compact">
          <li>
            <strong>Apply (anyone):</strong> <code>POST /discounts/apply</code> with order total and code. The server
            returns <code>discounted_total = order_total × discount_rate</code> stored for that code (a price multiplier,
            not a percent label).
          </li>
          <li>
            <strong>Create / delete (owners only):</strong> Codes are tied to a <code>restaurant_id</code> in storage.
            The apply endpoint does not check that your cart matches that restaurant—see limitations below.
          </li>
        </ul>
      </article>

      <article className="panel">
        <h3>Customer: use a promo code</h3>
        <p className="muted">
          Build your cart on Restaurants, then open Orders and use the cart panel to apply your code before placing the
          order. The discounted total is sent as the order <code>cost</code>.
        </p>
        <Link className="button-link" to="/restaurants">Browse restaurants</Link>
      </article>

      {!user && (
        <article className="panel muted">
          <p>
            <strong>Restaurant owners:</strong> log in to create or remove discount codes for your venue.
          </p>
          <Link to="/login">Login</Link>
        </article>
      )}

      {user && !isOwner && (
        <article className="panel muted">
          <p>Only accounts with the owner role can create or delete discount codes. Your role: {user.role}.</p>
        </article>
      )}

      {isOwner && (
        <>
          <article className="panel owner-discount-panel">
            <h3>Owner: create a discount code</h3>
            <p className="muted small-print">
              Your session must belong to an owner account whose <code>restaurant_id</code> matches the ID you enter. The
              backend does not expose your restaurant ID on the login response—use the ID you use elsewhere (for example
              Operations or restaurant setup).
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
                  <span>Price multiplier (discount_rate)</span>
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
              <p className="muted small-print">
                Example: multiplier <strong>0.85</strong> means the customer pays 85% of the cart total (about 15% off).
                Values above 1 increase the total; the API does not enforce a maximum.
              </p>
              <button type="submit" disabled={createBusy}>
                {createBusy ? "Creating…" : "Create discount"}
              </button>
            </form>
            {createError && <p className="error">{createError}</p>}
            {createMessage && <p className="success">{createMessage}</p>}
          </article>

          <article className="panel owner-discount-panel">
            <h3>Owner: remove a discount code</h3>
            <p className="muted small-print">
              There is no list endpoint—you must know the code string to delete it.
            </p>
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
