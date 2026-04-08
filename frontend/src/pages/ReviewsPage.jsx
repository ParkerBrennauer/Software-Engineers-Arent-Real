import { useState } from "react";
import { api } from "../api/client";

export default function ReviewsPage() {
  const [orderId, setOrderId] = useState("");
  const [restaurantId, setRestaurantId] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  async function run(call) {
    setError("");
    try {
      setData(await call());
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>Ratings and reviews</h2>
      <div className="row">
        <input placeholder="Order ID" value={orderId} onChange={(e) => setOrderId(e.target.value)} />
        <button onClick={() => run(() => api.reviews.rate(orderId, 5))}>Rate 5</button>
        <button onClick={() => run(() => api.reviews.review(orderId, "Excellent meal."))}>Write review</button>
        <button onClick={() => run(() => api.reviews.editReview(orderId, { review_text: "Updated text" }))}>Edit review</button>
        <button onClick={() => run(() => api.reviews.deleteReview(orderId))}>Delete review</button>
      </div>
      <div className="row">
        <input placeholder="Restaurant ID" value={restaurantId} onChange={(e) => setRestaurantId(e.target.value)} />
        <button onClick={() => run(() => api.reviews.restaurantReviews(restaurantId))}>Get restaurant reviews</button>
        <button onClick={() => run(() => api.reviews.feedbackPrompt(orderId))}>Feedback prompt</button>
        <button onClick={() => run(() => api.reviews.reportReview(orderId, { reason: "spam", description: "Test report" }))}>Report review</button>
      </div>
      {error && <p className="error">{error}</p>}
      {data && <pre className="json">{JSON.stringify(data, null, 2)}</pre>}
    </section>
  );
}

