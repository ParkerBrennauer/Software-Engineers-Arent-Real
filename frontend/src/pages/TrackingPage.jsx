import { useState } from 'react';
import { getOrderStatus, getOrderTracking, refreshOrderTracking } from '../lib/api';
import { DEFAULT_DEMO_TRACKING_ORDER_ID } from '../lib/demoData';

export default function TrackingPage() {
  const [orderId, setOrderId] = useState(DEFAULT_DEMO_TRACKING_ORDER_ID);
  const [order, setOrder] = useState(null);
  const [tracking, setTracking] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadTracking = async (event) => {
    event?.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const [orderPayload, trackingPayload] = await Promise.all([
        getOrderStatus(orderId),
        getOrderTracking(orderId),
      ]);
      setOrder(orderPayload);
      setTracking(trackingPayload);
    } catch (err) {
      setError(err.message || 'Could not load tracking information.');
      setOrder(null);
      setTracking(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setError('');
    setIsRefreshing(true);

    try {
      const nextTracking = await refreshOrderTracking(orderId);
      setTracking(nextTracking);
    } catch (err) {
      setError(err.message || 'Could not refresh tracking.');
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <section className="card">
      <h2>Track an order</h2>
      <p>
        Use the Feature 5 tracking endpoints to see where an active order is and
        how far away it is.
      </p>

      <form onSubmit={loadTracking} className="form-grid">
        <label>
          Order id
          <input
            value={orderId}
            onChange={(event) => setOrderId(event.target.value)}
            placeholder="Use a numeric order id, like 1"
          />
        </label>
        <div className="button-row">
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Load tracking'}
          </button>
          <button
            type="button"
            className="secondary-button"
            onClick={() => setOrderId(DEFAULT_DEMO_TRACKING_ORDER_ID)}
          >
            Use demo order
          </button>
        </div>
      </form>
      {error && <p className="error">{error}</p>}

      {order && tracking && (
        <div className="info-grid">
          <article className="info-card">
            <h3>Order details</h3>
            <p>
              <strong>Restaurant:</strong> {order.restaurant}
            </p>
            <p>
              <strong>Customer:</strong> {order.customer}
            </p>
            <p>
              <strong>Order status:</strong> {order.order_status}
            </p>
            <p>
              <strong>Payment status:</strong> {order.payment_status}
            </p>
          </article>

          <article className="info-card">
            <div className="section-heading">
              <h3>Live tracking</h3>
              <button
                type="button"
                className="secondary-button"
                disabled={isRefreshing}
                onClick={handleRefresh}
              >
                {isRefreshing ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
            <p>
              <strong>Current location:</strong> {tracking.current_location}
            </p>
            <p>
              <strong>Distance:</strong> {tracking.distance_km} km
            </p>
            <p>
              <strong>Estimated time:</strong> {tracking.estimated_time_minutes}{' '}
              minutes
            </p>
            <p>
              <strong>Driver:</strong> {tracking.driver || 'Not assigned yet'}
            </p>
            <p>
              <strong>Message:</strong> {tracking.status_message}
            </p>
          </article>
        </div>
      )}
    </section>
  );
}
