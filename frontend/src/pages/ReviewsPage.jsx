import React, { useState } from "react";
import { api } from "../api/client";

export default function ReviewsPage() {
  const [orderId, setOrderId] = useState("");
  const [restaurantId, setRestaurantId] = useState("");
  const [stars, setStars] = useState("5");
  const [reviewText, setReviewText] = useState("Excellent meal.");
  const [reportReason, setReportReason] = useState("spam");
  const [reportDescription, setReportDescription] = useState("Test report");
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
    <section className="card">
      <h2>Ratings and reviews</h2>
      <div className="row">
        <input placeholder="Order ID" value={orderId} onChange={(e) => setOrderId(e.target.value)} />
        <input
          placeholder="Stars (1-5)"
          value={stars}
          inputMode="numeric"
          onChange={(e) => setStars(e.target.value.replace(/\D/g, "").slice(0, 1))}
        />
        <button disabled={busy || !validOrderId() || Number(stars) < 1 || Number(stars) > 5} onClick={() => run(() => api.reviews.rate(validOrderId(), Number(stars)))}>Rate</button>
        <button disabled={busy || !validOrderId() || !reviewText.trim()} onClick={() => run(() => api.reviews.review(validOrderId(), reviewText.trim()))}>Write review</button>
        <button disabled={busy || !validOrderId() || !reviewText.trim()} onClick={() => run(() => api.reviews.editReview(validOrderId(), { review_text: reviewText.trim() }))}>Edit review</button>
        <button disabled={busy || !validOrderId()} onClick={() => run(() => api.reviews.deleteReview(validOrderId()))}>Delete review</button>
      </div>
      <div className="row">
        <input placeholder="Review text" value={reviewText} onChange={(e) => setReviewText(e.target.value)} />
      </div>
      <div className="row">
        <input placeholder="Restaurant ID" value={restaurantId} onChange={(e) => setRestaurantId(e.target.value)} />
        <button disabled={busy || !restaurantId.trim()} onClick={() => run(() => api.reviews.restaurantReviews(restaurantId))}>Get restaurant reviews</button>
        <button disabled={busy || !validOrderId()} onClick={() => run(() => api.reviews.feedbackPrompt(validOrderId()))}>Feedback prompt</button>
        <select value={reportReason} onChange={(e) => setReportReason(e.target.value)}>
          <option value="spam">Spam</option>
          <option value="inappropriate_language">Inappropriate language</option>
          <option value="other">Other</option>
        </select>
        <input placeholder="Report description" value={reportDescription} onChange={(e) => setReportDescription(e.target.value)} />
        <button disabled={busy || !validOrderId()} onClick={() => run(() => api.reviews.reportReview(validOrderId(), { reason: reportReason, description: reportDescription || null }))}>Report review</button>
      </div>
      {error && <p className="error">{error}</p>}
      {data && <pre className="json">{JSON.stringify(data, null, 2)}</pre>}
    </section>
  );
}

