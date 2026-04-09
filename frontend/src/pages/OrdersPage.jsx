import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { useCart } from "../state/CartContext";
import { useAuth } from "../state/AuthContext";
import CartPanel from "../components/CartPanel";
import OrderPlacementSuccess from "../components/OrderPlacementSuccess";
import FriendlyDataSummary from "../components/FriendlyDataSummary";
import KitchenOrderBoard from "../components/KitchenOrderBoard";
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
  const [history, setHistory] = useState([]);
  const [result, setResult] = useState(null);
  const [placementSuccess, setPlacementSuccess] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [tipMode, setTipMode] = useState("percent");
  const [tipPercentInput, setTipPercentInput] = useState("15");
  const [tipFixedInput, setTipFixedInput] = useState("");
  const [tipSuccess, setTipSuccess] = useState(null);
<<<<<<< Updated upstream
  const [paymentSimulate, setPaymentSimulate] = useState("auto");
  const [autoRefreshStatus, setAutoRefreshStatus] = useState(false);
=======
  const [paymentSuccess, setPaymentSuccess] = useState(null);
>>>>>>> Stashed changes

  useEffect(() => {
    if (resolvedRole === "driver" && user?.username) {
      setDriverName((prev) => (prev.trim() ? prev : user.username));
    }
  }, [resolvedRole, user?.username]);

  useEffect(() => {
    setTipSuccess(null);
    setPaymentSuccess(null);
  }, [orderId]);

  useEffect(() => {
    if (!autoRefreshStatus || resolvedRole !== "customer") return undefined;
    const valid = normalizedOrderId();
    if (!valid) return undefined;
    const id = window.setInterval(() => {
      api.orders
        .get(valid)
        .then((data) => {
          setResult(data);
          setError("");
        })
        .catch((err) => setError(err.message));
    }, 30000);
    return () => window.clearInterval(id);
  }, [autoRefreshStatus, orderId, resolvedRole]);

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

  async function payForOrder() {
    const valid = requireOrderId();
    if (!valid) return;
    setBusy(true);
    setError("");
    setPaymentSuccess(null);
    try {
      const data = await api.orders.pay(valid, { simulate: "auto" });
      setResult(data);
      const status = data?.payment_status != null ? String(data.payment_status) : "";
      if (status.toLowerCase() === "accepted") {
        setPaymentSuccess({ orderId: valid });
      } else {
        const reason =
          data?.payment_rejection_reason != null && String(data.payment_rejection_reason).trim()
            ? String(data.payment_rejection_reason)
            : "Payment was rejected.";
        setError(reason);
      }
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

  function formatTipCurrency(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "—";
    try {
      return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(n);
    } catch {
      return `$${n.toFixed(2)}`;
    }
  }

  async function applyCustomerTip() {
    const valid = requireOrderId();
    if (!valid) return;
    let payload;
    let percentUsed = null;
    let fixedEntered = null;
    if (tipMode === "percent") {
      const p = parseFloat(tipPercentInput);
      if (!Number.isFinite(p) || p < 0) {
        setError("Enter a valid tip percentage (0 or greater).");
        return;
      }
      payload = { tip_percent: p };
      percentUsed = p;
    } else {
      const amount = parseFloat(tipFixedInput);
      if (!Number.isFinite(amount) || amount < 0) {
        setError("Enter a valid tip amount in dollars (0 or greater).");
        return;
      }
      payload = { tip_amount: amount };
      fixedEntered = amount;
    }
    setBusy(true);
    setError("");
    try {
      const data = await api.orders.tip(valid, payload);
      setResult(data);
      let tipTotal = null;
      if (data && typeof data === "object" && data.tip_amount != null) {
        const parsed = Number(data.tip_amount);
        if (Number.isFinite(parsed)) tipTotal = parsed;
      }
      if (tipTotal == null && tipMode === "fixed" && fixedEntered != null) {
        tipTotal = fixedEntered;
      }
      setTipSuccess({
        orderId: valid,
        tipTotal,
        percentUsed,
        mode: tipMode,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
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
<<<<<<< Updated upstream
            <div className="row payment-sim-row">
              <label className="field payment-sim-field">
                <span>Simulated payment</span>
                <select
                  value={paymentSimulate}
                  onChange={(e) => setPaymentSimulate(e.target.value)}
                  disabled={busy}
                  aria-label="Simulated payment outcome"
                >
                  <option value="auto">Normal (accept any 15–16 digit card)</option>
                  <option value="accept">Force accept (same as normal)</option>
                  <option value="reject">Force reject (testing only)</option>
                </select>
              </label>
              <button
                type="button"
                disabled={busy || !orderId.trim()}
                onClick={() => {
                  const valid = requireOrderId();
                  if (valid) run(() => api.orders.pay(valid, { simulate: paymentSimulate }));
                }}
              >
                Pay for order
              </button>
            </div>
            <p className="muted small-print">
              Charges the card saved on your profile (15–16 digits). Normal mode always approves valid cards. Use “Force
              reject” only to test a declined payment—then pay again on the same order if needed.
            </p>
=======
            {paymentSuccess && (
              <section className="panel tip-applied-success" role="status" aria-live="polite">
                <div className="tip-applied-success__header">
                  <span className="tip-applied-success__icon" aria-hidden="true">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="28"
                      height="28"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                  </span>
                  <h3 className="tip-applied-success__title">Payment successful</h3>
                </div>
                <div className="tip-applied-success__body">
                  <p className="tip-applied-success__meta">
                    Order <span className="tip-applied-success__strong">#{paymentSuccess.orderId}</span> has been paid and
                    confirmed.
                  </p>
                </div>
                <div className="tip-applied-success__actions row">
                  <button type="button" className="tip-applied-success__dismiss" onClick={() => setPaymentSuccess(null)}>
                    Dismiss
                  </button>
                </div>
              </section>
            )}
>>>>>>> Stashed changes
            <fieldset className="tip-fieldset" disabled={busy}>
              <legend className="tip-legend">Tip on this order</legend>
              <p className="muted small-print">
                Choose a percentage of the order total or a fixed dollar amount. Only one applies per request.
              </p>
              <div className="row tip-mode-row">
                <label className="tip-mode-label">
                  <input
                    type="radio"
                    name="customer-tip-mode"
                    checked={tipMode === "percent"}
                    onChange={() => setTipMode("percent")}
                  />
                  Percent of total
                </label>
                <label className="tip-mode-label">
                  <input
                    type="radio"
                    name="customer-tip-mode"
                    checked={tipMode === "fixed"}
                    onChange={() => setTipMode("fixed")}
                  />
                  Fixed amount ($)
                </label>
              </div>
              <div className="row">
                {tipMode === "percent" ? (
                  <input
                    id="customer-tip-percent"
                    type="number"
                    min={0}
                    step="0.1"
                    placeholder="e.g. 15"
                    value={tipPercentInput}
                    onChange={(e) => setTipPercentInput(e.target.value)}
                    aria-label="Tip percentage"
                  />
                ) : (
                  <input
                    id="customer-tip-fixed"
                    type="number"
                    min={0}
                    step="0.01"
                    placeholder="e.g. 5.00"
                    value={tipFixedInput}
                    onChange={(e) => setTipFixedInput(e.target.value)}
                    aria-label="Tip amount in dollars"
                  />
                )}
              </div>
            </fieldset>
            {tipSuccess && (
              <section
                className="panel tip-applied-success"
                role="status"
                aria-live="polite"
                aria-labelledby="tip-applied-success-heading"
              >
                <div className="tip-applied-success__header">
                  <span className="tip-applied-success__icon" aria-hidden="true">
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="28"
                      height="28"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                  </span>
                  <h3 id="tip-applied-success-heading" className="tip-applied-success__title">
                    Tip applied successfully
                  </h3>
                </div>
                <div className="tip-applied-success__body">
                  <p className="tip-applied-success__meta">
                    Order <span className="tip-applied-success__strong">#{tipSuccess.orderId}</span> now includes your
                    tip.
                  </p>
                  {tipSuccess.tipTotal != null && (
                    <p className="tip-applied-success__amount" aria-label="Total tip amount">
                      Tip total: {formatTipCurrency(tipSuccess.tipTotal)}
                    </p>
                  )}
                  {tipSuccess.mode === "percent" && tipSuccess.percentUsed != null && (
                    <p className="muted small-print">
                      Based on {tipSuccess.percentUsed}% of the order subtotal (before tip).
                    </p>
                  )}
                  {tipSuccess.mode === "fixed" && (
                    <p className="muted small-print">You added a fixed-dollar tip to this order.</p>
                  )}
                </div>
                <div className="tip-applied-success__actions row">
                  <button type="button" className="tip-applied-success__dismiss" onClick={() => setTipSuccess(null)}>
                    Dismiss
                  </button>
                </div>
              </section>
            )}
            <div className="row action-toolbar customer-order-tools">
              <label className="checkbox-inline muted small-print">
                <input
                  type="checkbox"
                  checked={autoRefreshStatus}
                  onChange={(e) => setAutoRefreshStatus(e.target.checked)}
                  disabled={busy}
                />
                Auto-refresh status every 30s
              </label>
            </div>
            <div className="row action-toolbar">
              <button type="button" disabled={busy || !orderId.trim()} onClick={payForOrder}>
                Pay for order
              </button>
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
              <a
                className="button-link"
                href="https://www.openstreetmap.org/"
                target="_blank"
                rel="noreferrer"
              >
                Maps &amp; routing
              </a>
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
              <button type="button" disabled={busy || !orderId.trim()} onClick={applyCustomerTip}>
                Apply tip
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

      {resolvedRole === "owner" && <KitchenOrderBoard showRefund showAdvancedLink />}

      {resolvedRole === "staff" && <KitchenOrderBoard />}

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
