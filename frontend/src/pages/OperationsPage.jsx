import React, { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";
import { useRestaurantWorkspace } from "../state/RestaurantWorkspaceContext";
import { canViewOperationsContent } from "../utils/operationsAccess";
import FriendlyDataSummary from "../components/FriendlyDataSummary";

export default function OperationsPage() {
  const { user } = useAuth();
  const { linkedRestaurant, status: workspaceStatus, beginSwitchRestaurant } = useRestaurantWorkspace();
  const mayUseOperations = canViewOperationsContent(user?.role);
  const [restaurantId, setRestaurantId] = useState("");
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
      setError("Enter valid start and end times.");
      return null;
    }
    if (start > end) {
      setError("Start must be before end.");
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

  const ownerLinkedReady =
    mayUseOperations &&
    user?.role === "owner" &&
    workspaceStatus === "ready" &&
    linkedRestaurant?.id != null;

  useEffect(() => {
    if (!ownerLinkedReady || linkedRestaurant?.id == null) return;
    setRestaurantId(String(linkedRestaurant.id));
  }, [ownerLinkedReady, linkedRestaurant?.id]);

  if (!mayUseOperations) {
    return (
      <section className="card operations-access">
        <h1 className="page-title">Business tools</h1>
        <div className="access-restricted-notice" role="status">
          <p>This area is for restaurant owners. Sign in with an owner account to continue.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="card operations-page">
      <header className="page-header-block">
        <h1 className="page-title">Business tools</h1>
        <p className="page-lede muted">Reports and staff actions for your restaurants.</p>
      </header>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Order reports</h2>
        <p className="muted small-print">Filter orders by restaurant and time range.</p>
        {ownerLinkedReady && linkedRestaurant && (
          <p className="muted small-print operations-linked-venue">
            Using your linked venue <strong>{linkedRestaurant.label}</strong> ({linkedRestaurant.id}).
            <button type="button" className="operations-switch-venue" onClick={beginSwitchRestaurant}>
              Switch venue
            </button>
          </p>
        )}
        <div className="row">
          <input
            placeholder="Restaurant ID"
            value={restaurantId}
            onChange={(e) => setRestaurantId(e.target.value)}
            aria-label="Restaurant ID for reports"
            readOnly={ownerLinkedReady}
            disabled={ownerLinkedReady}
          />
        </div>
        <div className="row action-toolbar">
          <button disabled={busy || !restaurantId.trim()} onClick={() => run(() => api.restaurantAdministration.orders(restaurantId))}>
            All orders
          </button>
          <button
            disabled={busy || !restaurantId.trim()}
            onClick={() => run(() => api.restaurantAdministration.ordersByStatus(restaurantId, "delayed"))}
          >
            Delayed only
          </button>
          <button
            disabled={busy || !restaurantId.trim()}
            onClick={() => {
              const range = parseTimeRange();
              if (range) run(() => api.restaurantAdministration.ordersByDate(restaurantId, range.start, range.end));
            }}
          >
            By date range
          </button>
          <button
            disabled={busy || !restaurantId.trim()}
            onClick={() => {
              const range = parseTimeRange();
              if (range)
                run(() =>
                  api.restaurantAdministration.ordersByStatusAndDate(restaurantId, "delayed", range.start, range.end)
                );
            }}
          >
            Delayed in range
          </button>
        </div>
        <div className="row">
          <label className="field">
            <span>Range start</span>
            <input value={startTime} onChange={(e) => setStartTime(e.target.value)} />
          </label>
          <label className="field">
            <span>Range end</span>
            <input value={endTime} onChange={(e) => setEndTime(e.target.value)} />
          </label>
        </div>
        <p className="muted small-print">Time values use the same numeric format as your reporting setup.</p>
      </article>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Team</h2>
        <div className="row">
          <input placeholder="Staff username" value={staffUsername} onChange={(e) => setStaffUsername(e.target.value)} />
          <button disabled={busy || !staffUsername.trim()} onClick={() => run(() => api.restaurantAdministration.assignStaff(staffUsername))}>
            Add staff member
          </button>
        </div>
      </article>

      {error && <p className="error app-inline-alert">{error}</p>}
      {result && <FriendlyDataSummary data={result} title="Results" onDismiss={() => setResult(null)} />}
    </section>
  );
}
