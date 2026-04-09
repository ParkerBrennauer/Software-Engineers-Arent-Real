import React, { useEffect, useMemo, useState } from "react";
import { api } from "../api/client";
import FriendlyDataSummary from "../components/FriendlyDataSummary";
import { useAuth } from "../state/AuthContext";

function parseRestaurantId(order) {
  const rawRestaurant = typeof order?.restaurant === "string" ? order.restaurant : "";
  const match = rawRestaurant.match(/(\d+)/);
  return match ? match[1] : "";
}

function orderStatusLabel(order) {
  if (!order?.order_status) return "unknown";
  return String(order.order_status).replace(/_/g, " ");
}

export default function ReviewsPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [selectedOrderId, setSelectedOrderId] = useState("");
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [restaurantId, setRestaurantId] = useState("");
  const [stars, setStars] = useState("5");
  const [reviewText, setReviewText] = useState("");
  const [reportReason, setReportReason] = useState("spam");
  const [reportDescription, setReportDescription] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  const isCustomerSignedIn = user?.role === "customer" && !user?.requires2FA;

  useEffect(() => {
    let active = true;

    async function loadOrders() {
      if (!isCustomerSignedIn) {
        setOrders([]);
        setSelectedOrderId("");
        setRestaurantId("");
        return;
      }

      setOrdersLoading(true);
      setError("");
      try {
        const history = await api.customer.orderHistory();
        if (!active) return;
        setOrders(Array.isArray(history) ? history : []);
      } catch (err) {
        if (!active) return;
        setOrders([]);
        setError(err.message || "Could not load your orders.");
      } finally {
        if (active) setOrdersLoading(false);
      }
    }

    loadOrders();
    return () => {
      active = false;
    };
  }, [isCustomerSignedIn]);

  const selectedOrder = useMemo(
    () => orders.find((order) => String(order?.id ?? "") === selectedOrderId) ?? null,
    [orders, selectedOrderId]
  );

  const ratedOrders = useMemo(
    () =>
      orders.filter(
        (order) => order?.submitted_stars != null || (typeof order?.review_text === "string" && order.review_text.trim())
      ),
    [orders]
  );

  async function run(call) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      setData(await call());
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function selectOrder(order) {
    const nextOrderId = String(order?.id ?? "");
    setSelectedOrderId(nextOrderId);
    const derivedRestaurantId = parseRestaurantId(order);
    if (derivedRestaurantId) setRestaurantId(derivedRestaurantId);
  }

  function hasSelectedOrder() {
    return Boolean(selectedOrderId && selectedOrder);
  }

  function updateSelectedOrderFeedback(updates) {
    setOrders((currentOrders) =>
      currentOrders.map((order) =>
        String(order?.id ?? "") === selectedOrderId ? { ...order, ...updates } : order
      )
    );
  }

  async function handleSubmitRating() {
    await run(async () => {
      const response = await api.reviews.rate(selectedOrderId, Number(stars));
      updateSelectedOrderFeedback({ submitted_stars: Number(stars) });
      setMessage(`Rating submitted for order #${selectedOrderId}.`);
      return response;
    });
  }

  async function handlePostReview() {
    await run(async () => {
      const response = await api.reviews.review(selectedOrderId, reviewText.trim());
      updateSelectedOrderFeedback({ review_text: reviewText.trim() });
      setMessage(`Review posted for order #${selectedOrderId}.`);
      return response;
    });
  }

  async function handleUpdateReview() {
    await run(async () => {
      const response = await api.reviews.editReview(selectedOrderId, { review_text: reviewText.trim() });
      updateSelectedOrderFeedback({ review_text: reviewText.trim() });
      setMessage(`Review updated for order #${selectedOrderId}.`);
      return response;
    });
  }

  async function handleDeleteReview() {
    await run(async () => {
      const response = await api.reviews.deleteReview(selectedOrderId);
      updateSelectedOrderFeedback({ submitted_stars: null, review_text: null });
      setMessage(`Review deleted for order #${selectedOrderId}.`);
      return response;
    });
  }

  return (
    <section className="card reviews-page">
      <header className="page-header-block">
        <h1 className="page-title">Reviews</h1>
        <p className="page-lede muted">
          Rate your orders, write reviews, and browse feedback for restaurants you care about.
        </p>
      </header>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Choose one of your orders</h2>
        <p className="muted small-print">
          Select an order from your account first, then rate it and review it below.
        </p>

        {!isCustomerSignedIn && (
          <p className="muted small-print">Sign in as a customer to load your orders here.</p>
        )}

        {ordersLoading && <p className="muted">Loading your orders…</p>}

        {!ordersLoading && !error && isCustomerSignedIn && orders.length === 0 && (
          <p className="muted">No orders found for your account yet.</p>
        )}

        {!ordersLoading && orders.length > 0 && (
          <div className="favourites-restaurant-list">
            {orders.map((order, index) => {
              const orderKey = String(order?.id ?? `order-${index}`);
              const isSelected = orderKey === selectedOrderId;
              return (
                <article className="panel favourites-restaurant-card" key={orderKey}>
                  <div className="favourites-restaurant-card__header">
                    <div>
                      <h3 className="favourites-restaurant-card__title">Order #{orderKey}</h3>
                      <p className="muted small-print">
                        Restaurant: {order?.restaurant || "Unknown"} | Status: {orderStatusLabel(order)}
                      </p>
                    </div>
                    <button
                      type="button"
                      className={`restaurant-favorite-button${isSelected ? " restaurant-favorite-button--active" : ""}`}
                      onClick={() => selectOrder(order)}
                    >
                      {isSelected ? "Selected" : "Select order"}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </article>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Rate an order</h2>
        <p className="muted small-print">
          {selectedOrder
            ? `Selected order #${selectedOrderId}`
            : "Choose an order above to submit a rating."}
        </p>
        <div className="row">
          <input
            placeholder="Stars (1–5)"
            value={stars}
            inputMode="numeric"
            onChange={(e) => setStars(e.target.value.replace(/\D/g, "").slice(0, 1))}
            aria-label="Star rating"
          />
          <button
            type="button"
            disabled={busy || !hasSelectedOrder() || Number(stars) < 1 || Number(stars) > 5}
            onClick={handleSubmitRating}
          >
            Submit rating
          </button>
        </div>
      </article>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Write or edit a review</h2>
        <div className="row">
          <textarea
            className="input-textarea"
            placeholder="Share your experience…"
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            rows={4}
          />
        </div>
        <div className="row action-toolbar">
          <button
            type="button"
            disabled={busy || !hasSelectedOrder() || !reviewText.trim()}
            onClick={handlePostReview}
          >
            Post review
          </button>
          <button
            type="button"
            disabled={busy || !hasSelectedOrder() || !reviewText.trim()}
            onClick={handleUpdateReview}
          >
            Update review
          </button>
          <button
            type="button"
            disabled={busy || !hasSelectedOrder()}
            onClick={handleDeleteReview}
          >
            Delete review
          </button>
        </div>
      </article>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Restaurant reviews</h2>
        <div className="row">
          <input
            placeholder="Restaurant ID"
            value={restaurantId}
            onChange={(e) => setRestaurantId(e.target.value)}
          />
          <button
            type="button"
            disabled={busy || !restaurantId.trim()}
            onClick={() => run(() => api.reviews.restaurantReviews(restaurantId))}
          >
            Load reviews
          </button>
          <button
            type="button"
            disabled={busy || !hasSelectedOrder()}
            onClick={() => run(() => api.reviews.feedbackPrompt(selectedOrderId))}
          >
            Suggested reply
          </button>
        </div>
      </article>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Report a review</h2>
        <p className="muted small-print">Flag content that breaks community guidelines.</p>
        <div className="row">
          <select value={reportReason} onChange={(e) => setReportReason(e.target.value)} aria-label="Reason">
            <option value="spam">Spam</option>
            <option value="inappropriate_language">Inappropriate language</option>
            <option value="other">Other</option>
          </select>
          <input
            placeholder="Brief details"
            value={reportDescription}
            onChange={(e) => setReportDescription(e.target.value)}
          />
          <button
            type="button"
            disabled={busy || !hasSelectedOrder()}
            onClick={() =>
              run(() =>
                api.reviews.reportReview(selectedOrderId, {
                  reason: reportReason,
                  description: reportDescription || null,
                })
              )
            }
          >
            Submit report
          </button>
        </div>
      </article>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Your rated orders</h2>
        {ratedOrders.length === 0 ? (
          <p className="muted small-print">You have not rated any orders yet.</p>
        ) : (
          <div className="favourites-restaurant-list">
            {ratedOrders.map((order) => (
              <article className="panel favourites-restaurant-card" key={`rated-${order.id}`}>
                <div className="favourites-restaurant-card__header">
                  <div>
                    <h3 className="favourites-restaurant-card__title">Order #{order.id}</h3>
                    <p className="muted small-print">
                      {order.restaurant || "Unknown restaurant"} | Stars: {order.submitted_stars ?? "—"}
                    </p>
                    {order.review_text && (
                      <p className="muted small-print">Review: {order.review_text}</p>
                    )}
                  </div>
                  <button
                    type="button"
                    className="restaurant-favorite-button"
                    onClick={() => selectOrder(order)}
                  >
                    Open order
                  </button>
                </div>
              </article>
            ))}
          </div>
        )}
      </article>

      {error && (
        <p className="error app-inline-alert" role="alert">
          {error}
        </p>
      )}
      {message && (
        <p className="success app-inline-alert" role="status">
          {message}
        </p>
      )}
      {data && <FriendlyDataSummary data={data} title="Last response" onDismiss={() => setData(null)} />}
    </section>
  );
}
