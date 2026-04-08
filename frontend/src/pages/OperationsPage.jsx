import React, { useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";

export default function OperationsPage() {
  const { user } = useAuth();
  const [restaurantId, setRestaurantId] = useState("");
  const [discountCode, setDiscountCode] = useState("SAVE10");
  const [staffUsername, setStaffUsername] = useState("");
  const [startTime, setStartTime] = useState("0");
  const [endTime, setEndTime] = useState("9999999999");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function parseTimeRange() {
    const start = Number(startTime);
    const end = Number(endTime);
    if (!Number.isFinite(start) || !Number.isFinite(end)) {
      setError("Start and end time must be valid numbers.");
      return null;
    }
    if (start > end) {
      setError("Start time cannot be greater than end time.");
      return null;
    }
    return { start, end };
  }

  async function run(call) {
    setBusy(true);
    setError("");
    try {
      setResult(await call());
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h2>Role operations</h2>
      <p className="muted">Current role: {user?.role}. Backend auth is session-global and not token-based.</p>
      <div className="row">
        <input placeholder="Restaurant ID" value={restaurantId} onChange={(e) => setRestaurantId(e.target.value)} />
        <button disabled={busy || !restaurantId.trim()} onClick={() => run(() => api.restaurantAdministration.orders(restaurantId))}>Owner orders</button>
        <button disabled={busy || !restaurantId.trim()} onClick={() => run(() => api.restaurantAdministration.ordersByStatus(restaurantId, "delayed"))}>Owner orders by status</button>
        <button disabled={busy || !restaurantId.trim()} onClick={() => {
          const range = parseTimeRange();
          if (range) run(() => api.restaurantAdministration.ordersByDate(restaurantId, range.start, range.end));
        }}>Orders by date</button>
        <button disabled={busy || !restaurantId.trim()} onClick={() => {
          const range = parseTimeRange();
          if (range) run(() => api.restaurantAdministration.ordersByStatusAndDate(restaurantId, "delayed", range.start, range.end));
        }}>Status + date</button>
      </div>
      <div className="row">
        <input placeholder="Start unix time" value={startTime} onChange={(e) => setStartTime(e.target.value)} />
        <input placeholder="End unix time" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
      </div>
      <div className="row">
        <input placeholder="Staff username" value={staffUsername} onChange={(e) => setStaffUsername(e.target.value)} />
        <button disabled={busy || !staffUsername.trim()} onClick={() => run(() => api.restaurantAdministration.assignStaff(staffUsername))}>Assign staff</button>
      </div>
      <div className="row">
        <input placeholder="Discount code" value={discountCode} onChange={(e) => setDiscountCode(e.target.value)} />
        <button disabled={busy || !discountCode.trim()} onClick={() => run(() => api.discounts.apply({ order_total: 50, discount_code: discountCode }))}>Apply discount</button>
        <button disabled={busy || !discountCode.trim() || !restaurantId.trim()} onClick={() => run(() => api.discounts.create({ discount_rate: 0.9, discount_code: discountCode, restaurant_id: Number(restaurantId || 1) }))}>Create discount</button>
        <button disabled={busy || !discountCode.trim()} onClick={() => run(() => api.discounts.remove(discountCode))}>Delete discount</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && <pre className="json">{JSON.stringify(result, null, 2)}</pre>}
    </section>
  );
}

