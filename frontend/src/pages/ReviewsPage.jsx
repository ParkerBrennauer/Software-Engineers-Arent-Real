import React, { useState } from "react";
import { api } from "../api/client";
import FriendlyDataSummary from "../components/FriendlyDataSummary";

export default function ReviewsPage() {
  const [orderId, setOrderId] = useState("");
  const [restaurantId, setRestaurantId] = useState("");
  const [stars, setStars] = useState("5");
  const [reviewText, setReviewText] = useState("");
  const [reportReason, setReportReason] = useState("spam");
  const [reportDescription, setReportDescription] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function run(call) {
    setBusy(true);
    setError("");
    try {
      setData(await call());
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function validOrderId() {
    const id = Number(orderId);
    return Number.isInteger(id) && id > 0 ? String(id) : null;
  }

  return (
    <section className="card reviews-page">
      <header className="page-header-block">
        <h1 className="page-title">Reviews</h1>
        <p className="page-lede muted">Rate orders, write reviews, and browse feedback for restaurants you care about.</p>
      </header>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Rate an order</h2>
        <p className="muted small-print">Use your order number from checkout or confirmation email.</p>
        <div className="row">
          <input placeholder="Order number" value={orderId} onChange={(e) => setOrderId(e.target.value)} />
          <input
            placeholder="Stars (1–5)"
            value={stars}
            inputMode="numeric"
            onChange={(e) => setStars(e.target.value.replace(/\D/g, "").slice(0, 1))}
            aria-label="Star rating"
          />
          <button
            type="button"
            disabled={busy || !validOrderId() || Number(stars) < 1 || Number(stars) > 5}
            onClick={() => run(() => api.reviews.rate(validOrderId(), Number(stars)))}
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
            disabled={busy || !validOrderId() || !reviewText.trim()}
            onClick={() => run(() => api.reviews.review(validOrderId(), reviewText.trim()))}
          >
            Post review
          </button>
          <button
            type="button"
            disabled={busy || !validOrderId() || !reviewText.trim()}
            onClick={() => run(() => api.reviews.editReview(validOrderId(), { review_text: reviewText.trim() }))}
          >
            Update review
          </button>
          <button type="button" disabled={busy || !validOrderId()} onClick={() => run(() => api.reviews.deleteReview(validOrderId()))}>
            Delete review
          </button>
        </div>
      </article>

      <article className="panel orders-role-section">
        <h2 className="section-heading">Restaurant reviews</h2>
        <div className="row">
          <input placeholder="Restaurant ID" value={restaurantId} onChange={(e) => setRestaurantId(e.target.value)} />
          <button type="button" disabled={busy || !restaurantId.trim()} onClick={() => run(() => api.reviews.restaurantReviews(restaurantId))}>
            Load reviews
          </button>
          <button type="button" disabled={busy || !validOrderId()} onClick={() => run(() => api.reviews.feedbackPrompt(validOrderId()))}>
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
            disabled={busy || !validOrderId()}
            onClick={() =>
              run(() => api.reviews.reportReview(validOrderId(), { reason: reportReason, description: reportDescription || null }))
            }
          >
            Submit report
          </button>
        </div>
      </article>

      {error && (
        <p className="error app-inline-alert" role="alert">
          {error}
        </p>
      )}
      {data && <FriendlyDataSummary data={data} title="Last response" onDismiss={() => setData(null)} />}
    </section>
  );
}
