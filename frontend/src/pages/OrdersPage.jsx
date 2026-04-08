import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import { useAuth } from "../state/AuthContext";
import CartPanel from "../components/CartPanel";
import OrderPlacementSuccess from "../components/OrderPlacementSuccess";
import FriendlyDataSummary from "../components/FriendlyDataSummary";
import { resolveOrdersUiRole } from "../utils/ordersRoleUi";

function OrderIdFields({ orderId, setOrderId, disabled, idPrefix = "" }) {
  const id = idPrefix ? `${idPrefix}-order-id` : undefined;
  return (
    <div className="row">
      <input
        id={id}
        placeholder="Order number"
        value={orderId}
        onChange={(e) => setOrderId(e.target.value)}
        disabled={disabled}
        aria-label="Order number"
      />
    </div>
  );
}

export default function OrdersPage() {
  const { user } = useAuth();
  const { items, restaurant, grandTotal, clear } = useCart();
  const resolvedRole = resolveOrdersUiRole(user);

  const [orderId, setOrderId] = useState("");
  const [deliveryInstructions, setDeliveryInstructions] = useState("");
  const [driverName, setDriverName] = useState("");
  const [restaurantId, setRestaurantId] = useState("");
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);
  const [placementSuccess, setPlacementSuccess] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (resolvedRole === "driver" && user?.username) {
      setDriverName((prev) => (prev.trim() ? prev : user.username));
    }
  }, [resolvedRole, user?.username]);

  async function run(call) {
    setBusy(true);
    setError("");
    try {
      const data = await call();
      setResult(data);
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
      setError("Enter a valid order number.");
      return null;
    }
    return value;
  }

  async function checkoutOrder() {
    if (!items.length || !restaurant?.restaurant_id) {
      setError("Your cart is empty. Add items from a restaurant menu first.");
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
    setBusy(true);
    setError("");
    try {
      const created = await api.orders.place(payload);
      if (created?.id) setOrderId(String(created.id));
      clear();
      setResult(null);
      setPlacementSuccess(created);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  if (resolvedRole == null) {
    return (
      <section className="card orders-page">
        <h1 className="page-title">Orders</h1>
        <div className="panel access-restricted-notice" role="status">
          <p>
            We couldn&apos;t verify your account type. Please sign out and sign back in. If the problem continues,
            contact support.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="card orders-page">
      <header className="page-header-block">
        <h1 className="page-title">Orders</h1>
        <p className="page-lede muted">Signed in as {user?.username}</p>
      </header>

      {resolvedRole === "customer" && (
        <>
          <article className="panel orders-role-section">
            <h2 className="section-heading">Place an order</h2>
            <p className="muted small-print">Choose a restaurant, add dishes to your cart, then check out here.</p>
            <div className="row">
              <input
                placeholder="Delivery instructions (optional)"
                value={deliveryInstructions}
                onChange={(e) => setDeliveryInstructions(e.target.value)}
                disabled={busy}
                aria-label="Delivery instructions"
              />
              <button type="button" disabled={busy || items.length === 0} onClick={checkoutOrder}>
                Place order
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() =>
                  run(async () => {
                    const r = await api.customer.orderHistory();
                    setHistory(Array.isArray(r) ? r : []);
                    return r;
                  })
                }
              >
                Refresh order history
              </button>
            </div>
          </article>

          {placementSuccess && (
            <OrderPlacementSuccess orderPayload={placementSuccess} onDismiss={() => setPlacementSuccess(null)} />
          )}

          <article className="panel orders-role-section" id="track-order-section">
            <h2 className="section-heading">Track or change an order</h2>
            <p className="muted small-print">
              Look up an order by number. Some actions may not be available depending on order status.
            </p>
            <OrderIdFields orderId={orderId} setOrderId={setOrderId} disabled={busy} idPrefix="customer" />
            <div className="row action-toolbar">
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.get(valid));
                }}
              >
                View order
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.cancel(valid));
                }}
              >
                Cancel order
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.tracking(valid));
                }}
              >
                Tracking
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.refreshTracking(valid));
                }}
              >
                Refresh tracking
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.refund(valid));
                }}
              >
                Request refund
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.tip(valid, { tip_percent: 15 }));
                }}
              >
                Add 15% tip
              </button>
            </div>
          </article>

          <CartPanel />
        </>
      )}

      {resolvedRole === "driver" && (
        <>
          <article className="panel orders-role-section">
            <h2 className="section-heading">Deliveries</h2>
            <p className="muted small-print">Pick up orders, track the route, and report delays if needed.</p>
            <OrderIdFields orderId={orderId} setOrderId={setOrderId} disabled={busy} idPrefix="driver" />
            <div className="row action-toolbar">
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.get(valid));
                }}
              >
                View order
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.pickup(valid));
                }}
              >
                Confirm pickup
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.tracking(valid));
                }}
              >
                Tracking
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.refreshTracking(valid));
                }}
              >
                Refresh tracking
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.driverDelay(valid, "Traffic delay"));
                }}
              >
                Report delay
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.payoutTip(valid));
                }}
              >
                Tip payout
              </button>
            </div>
          </article>

          <article className="panel orders-role-section">
            <h2 className="section-heading">Your assignments</h2>
            <p className="muted small-print">Shows orders assigned to a driver account (defaults to you).</p>
            <div className="row">
              <input
                placeholder="Driver username"
                value={driverName}
                onChange={(e) => setDriverName(e.target.value)}
                disabled={busy}
                aria-label="Driver username"
              />
              <button type="button" disabled={busy || !driverName.trim()} onClick={() => run(() => api.orders.byDriver(driverName))}>
                Load my orders
              </button>
            </div>
          </article>
        </>
      )}

      {resolvedRole === "owner" && (
        <>
          <article className="panel orders-role-section">
            <h2 className="section-heading">Kitchen &amp; dispatch</h2>
            <p className="muted small-print">Mark orders ready, assign drivers, and handle refunds when allowed.</p>
            <OrderIdFields orderId={orderId} setOrderId={setOrderId} disabled={busy} idPrefix="owner" />
            <div className="row action-toolbar">
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.get(valid));
                }}
              >
                View order
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.ready(valid));
                }}
              >
                Mark ready
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.refund(valid));
                }}
              >
                Refund
              </button>
            </div>
            <div className="row">
              <input
                placeholder="Driver username"
                value={driverName}
                onChange={(e) => setDriverName(e.target.value)}
                disabled={busy}
                aria-label="Driver username to assign"
              />
              <button
                type="button"
                disabled={busy || !orderId.trim() || !driverName.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.assignDriver(valid, driverName));
                }}
              >
                Assign driver
              </button>
            </div>
            <div className="row action-toolbar">
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.tracking(valid));
                }}
              >
                Tracking
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.refreshTracking(valid));
                }}
              >
                Refresh tracking
              </button>
            </div>
          </article>

          <article className="panel orders-role-section">
            <h2 className="section-heading">Restaurant queue</h2>
            <p className="muted small-print">Load active orders for one of your locations by ID.</p>
            <div className="row">
              <input
                placeholder="Restaurant ID"
                value={restaurantId}
                onChange={(e) => setRestaurantId(e.target.value)}
                disabled={busy}
                aria-label="Restaurant ID"
              />
              <button
                type="button"
                disabled={busy || !restaurantId.trim()}
                onClick={() => run(() => api.restaurantAdministration.orders(restaurantId))}
              >
                Load orders
              </button>
            </div>
            <Link className="button-link" to="/operations">
              Advanced filters &amp; team tools
            </Link>
          </article>
        </>
      )}

      {resolvedRole === "staff" && (
        <>
          <article className="panel orders-role-section">
            <h2 className="section-heading">Kitchen</h2>
            <p className="muted small-print">Mark orders ready when they&apos;re prepared to go out.</p>
            <OrderIdFields orderId={orderId} setOrderId={setOrderId} disabled={busy} idPrefix="staff" />
            <div className="row action-toolbar">
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.get(valid));
                }}
              >
                View order
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.ready(valid));
                }}
              >
                Mark ready
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.tracking(valid));
                }}
              >
                Tracking
              </button>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.refreshTracking(valid));
                }}
              >
                Refresh tracking
              </button>
            </div>
          </article>

          <article className="panel orders-role-section">
            <h2 className="section-heading">Order queue</h2>
            <p className="muted small-print">Load live orders for your restaurant using its ID.</p>
            <div className="row">
              <input
                placeholder="Restaurant ID"
                value={restaurantId}
                onChange={(e) => setRestaurantId(e.target.value)}
                disabled={busy}
                aria-label="Restaurant ID"
              />
              <button
                type="button"
                disabled={busy || !restaurantId.trim()}
                onClick={() => run(() => api.restaurantAdministration.orders(restaurantId))}
              >
                Load orders
              </button>
            </div>
          </article>
        </>
      )}

      {resolvedRole === "customer" && history.length > 0 && (
        <section className="panel orders-role-section">
          <h2 className="section-heading">Past orders</h2>
          <div className="grid cards">
            {history.map((h, idx) => (
              <article className="panel order-history-card" key={`${h.id || idx}`}>
                <p className="order-history-card__id">Order #{h.id || idx}</p>
                <p>{h.order_status || "Status unavailable"}</p>
                <p className="order-history-card__total">${Number(h.cost || 0).toFixed(2)}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {error && (
        <p className="error app-inline-alert" role="alert">
          {error}
        </p>
      )}
      {result && (
        <FriendlyDataSummary data={result} title="Details" onDismiss={() => setResult(null)} />
      )}
    </section>
  );
}
