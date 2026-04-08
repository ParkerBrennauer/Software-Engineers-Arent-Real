import { useEffect, useMemo, useState } from 'react';
import {
  deleteReview,
  editReview,
  getFeedbackPrompt,
  getRestaurantReviews,
  reportReview,
  submitRating,
  submitReview,
} from '../lib/api';
import {
  DEFAULT_DEMO_CUSTOMER_ID,
  DEFAULT_DEMO_RESTAURANT_ID,
  getDemoOrdersForCustomer,
  loadPreferredCustomerId,
  savePreferredCustomerId,
} from '../lib/demoData';
import { useAuth } from '../state/AuthContext';

const REPORT_REASONS = [
  { value: 'spam', label: 'Spam' },
  { value: 'inappropriate_language', label: 'Inappropriate language' },
  { value: 'other', label: 'Other' },
];

export default function ReviewsPage() {
  const { user } = useAuth();
  const [customerId, setCustomerId] = useState(() =>
    loadPreferredCustomerId(user?.username),
  );
  const demoOrders = useMemo(
    () => getDemoOrdersForCustomer(customerId || DEFAULT_DEMO_CUSTOMER_ID),
    [customerId],
  );
  const [orderId, setOrderId] = useState(demoOrders[0]?.orderId || '');
  const [restaurantId, setRestaurantId] = useState(
    String(demoOrders[0]?.restaurantId || DEFAULT_DEMO_RESTAURANT_ID),
  );
  const [ratingStars, setRatingStars] = useState('5');
  const [reviewText, setReviewText] = useState('Great food and fast delivery!');
  const [editStars, setEditStars] = useState('4');
  const [editReviewText, setEditReviewText] = useState(
    'Still good, but delivery took a little longer than expected.',
  );
  const [reportReason, setReportReason] = useState('spam');
  const [reportDescription, setReportDescription] = useState('Demo report');
  const [reviewFilter, setReviewFilter] = useState('');
  const [feedbackPrompt, setFeedbackPrompt] = useState(null);
  const [restaurantReviews, setRestaurantReviews] = useState([]);
  const [error, setError] = useState('');
  const [resultMessage, setResultMessage] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    savePreferredCustomerId(customerId);
  }, [customerId]);

  useEffect(() => {
    if (!demoOrders.some((entry) => entry.orderId === orderId)) {
      setOrderId(demoOrders[0]?.orderId || '');
      setRestaurantId(String(demoOrders[0]?.restaurantId || DEFAULT_DEMO_RESTAURANT_ID));
    }
  }, [demoOrders, orderId]);

  const chooseDemoOrder = (nextOrderId, nextRestaurantId) => {
    setOrderId(nextOrderId);
    setRestaurantId(String(nextRestaurantId));
    setError('');
    setResultMessage('');
  };

  const runAction = async (action) => {
    setError('');
    setResultMessage('');
    setIsSubmitting(true);

    try {
      const result = await action();
      return result;
    } catch (err) {
      setError(err.message || 'Request failed.');
      return null;
    } finally {
      setIsSubmitting(false);
    }
  };

  const loadFeedbackPrompt = async () => {
    const result = await runAction(() => getFeedbackPrompt(orderId));
    if (result) {
      setFeedbackPrompt(result);
      setResultMessage(result.message);
    }
  };

  const handleRatingSubmit = async () => {
    const result = await runAction(() => submitRating(orderId, Number(ratingStars)));
    if (result) {
      setResultMessage(`Saved ${result.stars}-star rating for order ${result.order_id}.`);
    }
  };

  const handleReviewSubmit = async () => {
    const result = await runAction(() => submitReview(orderId, reviewText));
    if (result) {
      setResultMessage(`Saved review for order ${result.order_id}.`);
    }
  };

  const handleReviewEdit = async () => {
    const result = await runAction(() =>
      editReview(orderId, {
        stars: editStars,
        reviewText: editReviewText,
      }),
    );
    if (result) {
      setResultMessage(`Updated review for order ${result.order_id}.`);
    }
  };

  const handleReviewDelete = async () => {
    const result = await runAction(() => deleteReview(orderId));
    if (result) {
      setResultMessage(result.message);
    }
  };

  const handleReportSubmit = async () => {
    const result = await runAction(() =>
      reportReview(orderId, {
        reason: reportReason,
        description: reportDescription,
      }),
    );
    if (result) {
      setResultMessage(result.message);
    }
  };

  const handleLoadRestaurantReviews = async () => {
    const result = await runAction(() =>
      getRestaurantReviews(restaurantId, reviewFilter || undefined),
    );
    if (result) {
      setRestaurantReviews(result.reviews || []);
      setResultMessage(`Loaded ${result.total_reviews} restaurant reviews.`);
    }
  };

  return (
    <section className="card">
      <h2>Ratings and reviews</h2>
      <p>
        This page demos Feature 9 using completed sample orders from the seeded
        review dataset and the live rating/review endpoints.
      </p>

      <label className="search-input">
        Demo customer id
        <input
          value={customerId}
          onChange={(event) => setCustomerId(event.target.value)}
          placeholder="Paste a customer id from customers.json"
        />
      </label>

      <div className="stack-section">
        <div className="section-heading">
          <h3>Completed orders</h3>
          <span className="pill">{demoOrders.length} available</span>
        </div>
        <div className="chip-row">
          {demoOrders.map((entry) => (
            <button
              key={entry.orderId}
              type="button"
              className={`chip-button ${entry.orderId === orderId ? 'active' : ''}`}
              onClick={() => chooseDemoOrder(entry.orderId, entry.restaurantId)}
            >
              {entry.orderId}
            </button>
          ))}
        </div>
      </div>

      <div className="info-grid">
        <article className="info-card">
          <h3>Selected order</h3>
          <label>
            Completed order id
            <input
              value={orderId}
              onChange={(event) => setOrderId(event.target.value)}
            />
          </label>
          <label>
            Restaurant id
            <input
              value={restaurantId}
              onChange={(event) => setRestaurantId(event.target.value)}
            />
          </label>
          <div className="button-row">
            <button type="button" onClick={loadFeedbackPrompt} disabled={isSubmitting}>
              Load feedback prompt
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={handleLoadRestaurantReviews}
              disabled={isSubmitting}
            >
              Load restaurant reviews
            </button>
          </div>
          {feedbackPrompt && <p className="helper-text">{feedbackPrompt.message}</p>}
        </article>

        <article className="info-card">
          <h3>Submit rating</h3>
          <label>
            Stars
            <input
              type="number"
              min="1"
              max="5"
              value={ratingStars}
              onChange={(event) => setRatingStars(event.target.value)}
            />
          </label>
          <button type="button" onClick={handleRatingSubmit} disabled={isSubmitting}>
            Submit rating
          </button>
        </article>
      </div>

      <div className="info-grid">
        <article className="info-card">
          <h3>Submit review</h3>
          <label>
            Review text
            <textarea
              value={reviewText}
              onChange={(event) => setReviewText(event.target.value)}
              rows="4"
            />
          </label>
          <button type="button" onClick={handleReviewSubmit} disabled={isSubmitting}>
            Submit review
          </button>
        </article>

        <article className="info-card">
          <h3>Edit or delete review</h3>
          <label>
            New stars
            <input
              type="number"
              min="1"
              max="5"
              value={editStars}
              onChange={(event) => setEditStars(event.target.value)}
            />
          </label>
          <label>
            New review text
            <textarea
              value={editReviewText}
              onChange={(event) => setEditReviewText(event.target.value)}
              rows="4"
            />
          </label>
          <div className="button-row">
            <button type="button" onClick={handleReviewEdit} disabled={isSubmitting}>
              Edit review
            </button>
            <button
              type="button"
              className="secondary-button"
              onClick={handleReviewDelete}
              disabled={isSubmitting}
            >
              Delete review
            </button>
          </div>
        </article>
      </div>

      <div className="info-grid">
        <article className="info-card">
          <h3>Report review</h3>
          <label>
            Reason
            <select
              value={reportReason}
              onChange={(event) => setReportReason(event.target.value)}
            >
              {REPORT_REASONS.map((reason) => (
                <option key={reason.value} value={reason.value}>
                  {reason.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Description
            <textarea
              value={reportDescription}
              onChange={(event) => setReportDescription(event.target.value)}
              rows="3"
            />
          </label>
          <button type="button" onClick={handleReportSubmit} disabled={isSubmitting}>
            Submit report
          </button>
        </article>

        <article className="info-card">
          <h3>Restaurant review feed</h3>
          <label>
            Stars filter
            <input
              type="number"
              min="1"
              max="5"
              value={reviewFilter}
              onChange={(event) => setReviewFilter(event.target.value)}
              placeholder="Leave blank for all"
            />
          </label>
          <div className="review-feed">
            {restaurantReviews.length === 0 && (
              <p className="helper-text">
                Load reviews to see the current restaurant feedback list.
              </p>
            )}
            {restaurantReviews.map((review) => (
              <article key={review.order_id} className="review-card">
                <p>
                  <strong>Order:</strong> {review.order_id}
                </p>
                <p>
                  <strong>Stars:</strong> {review.submitted_stars ?? 'N/A'}
                </p>
                <p>
                  <strong>Review:</strong> {review.review_text || 'No review text'}
                </p>
              </article>
            ))}
          </div>
        </article>
      </div>

      {error && <p className="error">{error}</p>}
      {resultMessage && <p className="success">{resultMessage}</p>}
    </section>
  );
}
