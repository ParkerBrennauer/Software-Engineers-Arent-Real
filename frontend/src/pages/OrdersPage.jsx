import { useState } from "react";
import { api } from "../api/client";

export default function OrdersPage() {
  const [orderId, setOrderId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

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
      <h2>Orders and tracking</h2>
      <p className="muted">Use these controls to exercise order, tip, and tracking endpoints.</p>
      <div className="row">
        <input placeholder="Order ID" value={orderId} onChange={(e) => setOrderId(e.target.value)} />
        <button disabled={busy} onClick={() => run(() => api.orders.get(orderId))}>Load order</button>
        <button disabled={busy} onClick={() => run(() => api.orders.cancel(orderId))}>Cancel</button>
        <button disabled={busy} onClick={() => run(() => api.orders.tracking(orderId))}>Tracking</button>
        <button disabled={busy} onClick={() => run(() => api.orders.refreshTracking(orderId))}>Refresh tracking</button>
      </div>
      <div className="row">
        <button disabled={busy} onClick={() => run(() => api.orders.ready(orderId))}>Mark ready</button>
        <button disabled={busy} onClick={() => run(() => api.orders.pickup(orderId))}>Pickup</button>
        <button disabled={busy} onClick={() => run(() => api.orders.refund(orderId))}>Refund</button>
        <button disabled={busy} onClick={() => run(() => api.orders.tip(orderId, { tip_percent: 15 }))}>Add 15% tip</button>
        <button disabled={busy} onClick={() => run(() => api.orders.payoutTip(orderId))}>Payout tip</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && <pre className="json">{JSON.stringify(result, null, 2)}</pre>}
    </section>
  );
}

