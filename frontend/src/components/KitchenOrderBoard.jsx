import React, { useCallback, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { useRestaurantWorkspace } from "../state/RestaurantWorkspaceContext";
import FriendlyDataSummary from "./FriendlyDataSummary";
import {
  canShowAssignDriver,
  canShowMarkReady,
  canShowRefund,
  mergeDriverCandidates,
  normalizeStatusKey,
  pickAutoDriver,
  summarizeItems,
} from "../utils/orderKitchenUi";

function formatMoney(n) {
  const x = Number(n);
  if (!Number.isFinite(x)) return "—";
  try {
    return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(x);
  } catch {
    return `$${x.toFixed(2)}`;
  }
}

function orderKey(o, idx) {
  const id = o?.id ?? o?.order_id;
  if (id != null) return `order-${id}`;
  return `order-idx-${idx}`;
}

function getOrderId(o) {
  const id = o?.id ?? o?.order_id;
  if (id == null) return null;
  return String(id);
}

/**
 * Restaurant kitchen queue: list orders, mark ready, assign driver without typing order IDs.
 * Driver list: backend has no GET /drivers — candidates come from orders, VITE_SUGGESTED_DRIVERS, and saved names.
 */
export default function KitchenOrderBoard({ showRefund = false, showAdvancedLink = false }) {
  const { linkedRestaurant, status: workspaceStatus, beginSwitchRestaurant } = useRestaurantWorkspace();
  const linkedIdStr =
    workspaceStatus === "ready" && linkedRestaurant?.id != null ? String(linkedRestaurant.id).trim() : "";

  const [restaurantId, setRestaurantId] = useState("");
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [detailOrder, setDetailOrder] = useState(null);
  const [manualDriverInput, setManualDriverInput] = useState("");
  const [savedDrivers, setSavedDrivers] = useState([]);
  const [perOrderDriver, setPerOrderDriver] = useState({});
  const [working, setWorking] = useState(null);

  const envDrivers = useMemo(
    () =>
      String(import.meta.env.VITE_SUGGESTED_DRIVERS || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean),
    []
  );

  const candidates = useMemo(
    () => mergeDriverCandidates(orders, savedDrivers, envDrivers),
    [orders, savedDrivers, envDrivers]
  );

  const refreshOrders = useCallback(async () => {
    const rid = linkedIdStr || String(restaurantId || "").trim();
    if (!rid) {
      setError(
        linkedIdStr
          ? "Could not resolve your venue. Use “Switch venue” in the bar above."
          : "Enter your venue number below, or choose your venue from the bar above."
      );
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await api.restaurantAdministration.orders(rid);
      const list = Array.isArray(data) ? data : [];
      setOrders(list);
    } catch (e) {
      setError(e?.message || "Could not load orders.");
      setOrders([]);
    } finally {
      setLoading(false);
    }
  }, [linkedIdStr, restaurantId]);

  useEffect(() => {
    if (!linkedIdStr) return;
    let cancelled = false;
    setLoading(true);
    setError("");
    (async () => {
      try {
        const data = await api.restaurantAdministration.orders(linkedIdStr);
        if (cancelled) return;
        setOrders(Array.isArray(data) ? data : []);
      } catch (e) {
        if (!cancelled) {
          setError(e?.message || "Could not load orders.");
          setOrders([]);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [linkedIdStr]);

  async function runOrderAction(orderIdStr, fn) {
    if (!orderIdStr || working) return;
    setWorking(orderIdStr);
    setError("");
    try {
      await fn();
      await refreshOrders();
      setDetailOrder(null);
    } catch (e) {
      setError(e?.message || "Something went wrong.");
    } finally {
      setWorking(null);
    }
  }

  function addSavedDriver() {
    const t = manualDriverInput.trim();
    if (!t) return;
    setSavedDrivers((prev) => (prev.includes(t) ? prev : [...prev, t]));
    setManualDriverInput("");
  }

  function handleMarkReady(o) {
    const oid = getOrderId(o);
    if (!oid) return;
    return runOrderAction(oid, () => api.orders.ready(oid));
  }

  function handleAssign(o, driverUsername) {
    const oid = getOrderId(o);
    const d = String(driverUsername || "").trim();
    if (!oid || !d) {
      setError("Choose a driver to assign.");
      return;
    }
    return runOrderAction(oid, () => api.orders.assignDriver(oid, d));
  }

  function handleAutoAssign(o) {
    const oid = getOrderId(o);
    if (!oid) return;
    const pick = pickAutoDriver(candidates, orders);
    if (!pick) {
      setError("Add a driver name below, or wait until another order shows a driver you can reuse.");
      return;
    }
    return handleAssign(o, pick);
  }

  function handleRefund(o) {
    const oid = getOrderId(o);
    if (!oid) return;
    return runOrderAction(oid, () => api.orders.refund(oid));
  }

  function handleRestaurantDelay(o) {
    const oid = getOrderId(o);
    if (!oid) return;
    const reason = window.prompt("Describe the delay for this order (shown to customers and drivers):", "Kitchen running behind");
    if (reason == null || !String(reason).trim()) return;
    return runOrderAction(oid, () => api.orders.restaurantDelay(oid, String(reason).trim()));
  }

  const needsKitchen = orders.filter((o) => canShowMarkReady(o?.order_status));
  const other = orders.filter((o) => !canShowMarkReady(o?.order_status));

  const usingLinkedVenue = Boolean(linkedIdStr);
  const effectiveRidForEmpty = linkedIdStr || String(restaurantId).trim();

  function renderOrderCard(o, idx) {
    const oid = getOrderId(o);
    const st = normalizeStatusKey(o?.order_status);
    const pay = o?.payment_status != null ? String(o.payment_status) : "—";
    const itemsLine = summarizeItems(o?.items);
    const cost = formatMoney(o?.cost);
    const driver = o?.driver != null && String(o.driver).trim() ? String(o.driver) : "—";
    const cust = o?.customer != null ? String(o.customer) : "—";
    const instructions = o?.delivery_instructions != null && String(o.delivery_instructions).trim()
      ? String(o.delivery_instructions)
      : null;
    const timeLabel = o?.time != null ? String(o.time) : "—";

    const selectedDriver = perOrderDriver[oid || ""] ?? (candidates[0] || "");
    const showReady = oid && canShowMarkReady(o?.order_status);
    const showAssign = oid && canShowAssignDriver(o);
    const showRef = showRefund && oid && canShowRefund(o?.order_status);

    return (
      <article className="panel kitchen-order-card" key={orderKey(o, idx)}>
        <div className="kitchen-order-card__head">
          <div>
            <p className="kitchen-order-card__id">Order #{oid || "—"}</p>
            <p className="kitchen-order-card__status">
              <span className="kitchen-badge">{st || "—"}</span>
              <span className="muted"> · Payment: {pay}</span>
            </p>
          </div>
          <div className="kitchen-order-card__cost">{cost}</div>
        </div>
        <p className="kitchen-order-card__line">
          <span className="muted">Customer:</span> {cust}
        </p>
        <p className="kitchen-order-card__line">
          <span className="muted">Items:</span> {itemsLine}
        </p>
        {instructions && (
          <p className="kitchen-order-card__line">
            <span className="muted">Notes:</span> {instructions}
          </p>
        )}
        <p className="kitchen-order-card__line small-print muted">
          Driver: {driver} · Time: {timeLabel}
        </p>
        <div className="kitchen-order-card__actions">
          {oid && (
            <button
              type="button"
              className="kitchen-btn-secondary"
              disabled={!!working || loading}
              onClick={() => setDetailOrder((prev) => (prev === o ? null : o))}
            >
              {detailOrder === o ? "Hide details" : "View details"}
            </button>
          )}
          {showReady && (
            <>
              <button
                type="button"
                className="kitchen-btn-secondary"
                disabled={working === oid || loading}
                onClick={() => handleRestaurantDelay(o)}
              >
                Report delay
              </button>
              <button
                type="button"
                disabled={working === oid || loading}
                onClick={() => handleMarkReady(o)}
              >
                {working === oid ? "…" : "Mark ready"}
              </button>
            </>
          )}
          {showAssign && (
            <>
              <label className="kitchen-assign-label">
                <span className="visually-hidden">Driver for order {oid}</span>
                <select
                  value={selectedDriver}
                  onChange={(e) => setPerOrderDriver((prev) => ({ ...prev, [oid]: e.target.value }))}
                  disabled={!!working || loading || candidates.length === 0}
                  aria-label={`Assign driver for order ${oid}`}
                >
                  {candidates.length === 0 ? (
                    <option value="">Add a driver name below</option>
                  ) : (
                    candidates.map((c) => (
                      <option key={c} value={c}>
                        {c}
                      </option>
                    ))
                  )}
                </select>
              </label>
              <button
                type="button"
                disabled={working === oid || loading || !selectedDriver}
                onClick={() => handleAssign(o, selectedDriver)}
              >
                Assign driver
              </button>
              <button
                type="button"
                className="kitchen-btn-secondary"
                disabled={working === oid || loading || candidates.length === 0}
                onClick={() => handleAutoAssign(o)}
              >
                Auto-assign
              </button>
            </>
          )}
          {showRef && (
            <button
              type="button"
              className="kitchen-btn-warn"
              disabled={working === oid || loading}
              onClick={() => handleRefund(o)}
            >
              Refund
            </button>
          )}
        </div>
        {detailOrder === o && oid && (
          <div className="kitchen-order-detail">
            <FriendlyDataSummary data={o} title={`Order ${oid}`} onDismiss={() => setDetailOrder(null)} />
          </div>
        )}
      </article>
    );
  }

  return (
    <article className="panel orders-role-section kitchen-board" data-testid="kitchen-order-board">
      <h2 className="section-heading">Kitchen queue</h2>
      <p className="muted small-print">
        Load orders for your venue, then mark ready or assign a driver from the list—no need to type order numbers.
      </p>
      {usingLinkedVenue ? (
        <div className="kitchen-linked-venue row">
          <p className="muted small-print kitchen-linked-venue__text">
            Orders load for <strong>{linkedRestaurant?.label || `venue ${linkedIdStr}`}</strong>. Refresh the list after
            updates.
          </p>
          <div className="kitchen-linked-venue__actions">
            <button type="button" disabled={loading} onClick={refreshOrders}>
              {loading ? "Loading…" : "Refresh orders"}
            </button>
            <button type="button" className="kitchen-btn-secondary" onClick={beginSwitchRestaurant}>
              Change venue
            </button>
          </div>
        </div>
      ) : (
        <div className="row kitchen-board-toolbar">
          <input
            placeholder="Venue number"
            value={restaurantId}
            onChange={(e) => setRestaurantId(e.target.value)}
            disabled={loading}
            aria-label="Venue number"
          />
          <button type="button" disabled={loading || !String(restaurantId).trim()} onClick={refreshOrders}>
            {loading ? "Loading…" : "Load orders"}
          </button>
        </div>
      )}

      <div className="kitchen-driver-pool panel kitchen-subpanel">
        <h3 className="kitchen-subheading">Drivers on your team</h3>
        <p className="muted small-print">
          Save the usernames you work with so you can assign them in one tap. Names from orders in this list are added
          automatically.
        </p>
        <div className="row">
          <input
            placeholder="Driver username"
            value={manualDriverInput}
            onChange={(e) => setManualDriverInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && (e.preventDefault(), addSavedDriver())}
            aria-label="Add driver username"
          />
          <button type="button" onClick={addSavedDriver} disabled={!manualDriverInput.trim()}>
            Save name
          </button>
        </div>
        {savedDrivers.length > 0 && (
          <p className="small-print muted">Saved: {savedDrivers.join(", ")}</p>
        )}
      </div>

      {error && (
        <p className="error app-inline-alert" role="alert">
          {error}
        </p>
      )}

      {loading && <p className="muted">Loading orders…</p>}

      {!loading && orders.length === 0 && effectiveRidForEmpty && !error && (
        <p className="muted">No orders returned for this venue.</p>
      )}

      {orders.length > 0 && (
        <div className="kitchen-order-sections">
          {needsKitchen.length > 0 && (
            <section className="kitchen-section">
              <h3 className="kitchen-section-title">In the kitchen</h3>
              <div className="kitchen-order-list">{needsKitchen.map((o, i) => renderOrderCard(o, i))}</div>
            </section>
          )}
          {other.length > 0 && (
            <section className="kitchen-section">
              <h3 className="kitchen-section-title">Out or completed</h3>
              <div className="kitchen-order-list">{other.map((o, i) => renderOrderCard(o, i))}</div>
            </section>
          )}
        </div>
      )}

      {showAdvancedLink && (
        <Link className="button-link" to="/operations">
          Advanced filters &amp; team tools
        </Link>
      )}
    </article>
  );
}
