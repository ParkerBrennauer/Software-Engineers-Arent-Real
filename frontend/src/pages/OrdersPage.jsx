import React, { useState } from "react";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import { useAuth } from "../state/AuthContext";
import CartPanel from "../components/CartPanel";

export default function OrdersPage() {
  const { user } = useAuth();
  const { items, restaurant, grandTotal, clear } = useCart();
  const [orderId, setOrderId] = useState("");
  const [deliveryInstructions, setDeliveryInstructions] = useState("");
  const [driverName, setDriverName] = useState("");
  const [history, setHistory] = useState([]);
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

  function normalizedOrderId() {
    const parsed = Number(orderId);
    if (!Number.isInteger(parsed) || parsed <= 0) return null;
    return String(parsed);
  }

  function requireOrderId() {
    const value = normalizedOrderId();
    if (!value) {
      setError("Order ID must be a positive number.");
      return null;
    }
    return value;
  }

  async function checkoutOrder() {
    if (!items.length || !restaurant?.restaurant_id) {
      setError("Add menu items to cart before checkout.");
      return;
    }
    const payload = {
      items: items.map((i) => ({ item_name: i.item_name, price: Number(i.price) * i.quantity })),
      cost: Number(grandTotal.toFixed(2)),
      restaurant: `Restaurant_${restaurant.restaurant_id}`,
      customer: user?.username || "",
      time: 25,
      cuisine: restaurant.cuisine || "unknown",
      distance: 2.5,
      delivery_instructions: deliveryInstructions || null,
    };
    await run(async () => {
      const created = await api.orders.place(payload);
      if (created?.id) setOrderId(String(created.id));
      clear();
      return created;
    });
  }

  return (
    <section className="card">
      <h2>Orders and tracking</h2>
      <p className="muted">
        Checkout uses backend order creation; payment is simulated in UI because no payment router endpoint exists.
        Cart discounts use <code>POST /discounts/apply</code>; the discounted total is sent as <code>cost</code>.
      </p>
      <div className="row">
        <input
          placeholder="Delivery instructions"
          value={deliveryInstructions}
          onChange={(e) => setDeliveryInstructions(e.target.value)}
        />
        <button disabled={busy || items.length === 0} onClick={checkoutOrder}>
          Place order from cart
        </button>
        <button disabled={busy} onClick={() => run(async () => {
          const r = await api.customer.orderHistory();
          setHistory(Array.isArray(r) ? r : []);
          return r;
        })}>Load order history</button>
      </div>
      <div className="row">
        <input placeholder="Order ID" value={orderId} onChange={(e) => setOrderId(e.target.value)} />
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.get(valid));
        }}>Load order</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.cancel(valid));
        }}>Cancel</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.tracking(valid));
        }}>Tracking</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.refreshTracking(valid));
        }}>Refresh tracking</button>
      </div>
      <div className="row">
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.ready(valid));
        }}>Mark ready</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.pickup(valid));
        }}>Pickup</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.refund(valid));
        }}>Refund</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.tip(valid, { tip_percent: 15 }));
        }}>Add 15% tip</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.payoutTip(valid));
        }}>Payout tip</button>
      </div>
      <div className="row">
        <input placeholder="Driver username" value={driverName} onChange={(e) => setDriverName(e.target.value)} />
        <button disabled={busy || !driverName.trim()} onClick={() => run(() => api.orders.byDriver(driverName))}>Driver orders</button>
        <button disabled={busy || !orderId.trim() || !driverName.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.assignDriver(valid, driverName));
        }}>Assign driver</button>
        <button disabled={busy || !orderId.trim()} onClick={() => {
          const valid = requireOrderId();
          if (valid) run(() => api.orders.driverDelay(valid, "Traffic delay"));
        }}>Report driver delay</button>
      </div>
      <CartPanel />
      {history.length > 0 && (
        <section className="panel">
          <h3>Order history</h3>
          <div className="grid cards">
            {history.map((h, idx) => (
              <article className="panel" key={`${h.id || idx}`}>
                <p>Order #{h.id || idx}</p>
                <p>Status: {h.order_status || "unknown"}</p>
                <p>Total: ${Number(h.cost || 0).toFixed(2)}</p>
              </article>
            ))}
          </div>
        </section>
      )}
      {error && <p className="error">{error}</p>}
      {result && <pre className="json">{JSON.stringify(result, null, 2)}</pre>}
    </section>
  );
}

