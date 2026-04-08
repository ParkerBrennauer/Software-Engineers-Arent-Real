import React, { useState } from "react";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import { useAuth } from "../state/AuthContext";
import CartPanel from "../components/CartPanel";

export default function OrdersPage() {
  const { user } = useAuth();
  const { items, restaurant, total, clear } = useCart();
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

  async function checkoutOrder() {
    if (!items.length || !restaurant?.restaurant_id) {
      setError("Add menu items to cart before checkout.");
      return;
    }
    const payload = {
      items: items.map((i) => ({ item_name: i.item_name, price: Number(i.price) * i.quantity })),
      cost: Number(total.toFixed(2)),
      restaurant: `Restaurant_${restaurant.restaurant_id}`,
      customer: user?.username || "",
      time: 25,
      cuisine: restaurant.cuisine || "unknown",
      distance: 2.5,
      delivery_instructions: deliveryInstructions || null,
    };
    await run(async () => {
      const created = await api.orders.place(payload);
      setOrderId(String(created.id ?? ""));
      clear();
      return created;
    });
  }

  return (
    <section className="card">
      <h2>Orders and tracking</h2>
      <p className="muted">
        Checkout uses backend order creation; payment is simulated in UI because no payment router endpoint exists.
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
      <div className="row">
        <input placeholder="Driver username" value={driverName} onChange={(e) => setDriverName(e.target.value)} />
        <button disabled={busy} onClick={() => run(() => api.orders.byDriver(driverName))}>Driver orders</button>
        <button disabled={busy} onClick={() => run(() => api.orders.assignDriver(orderId, driverName))}>Assign driver</button>
        <button disabled={busy} onClick={() => run(() => api.orders.driverDelay(orderId, "Traffic delay"))}>Report driver delay</button>
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

