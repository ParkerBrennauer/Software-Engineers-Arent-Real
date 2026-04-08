import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getOrderStatus, getOrderTracking, refreshOrderTracking } from '../lib/api';

function prettyPrintObject(value) {
  return JSON.stringify(value, null, 2);
}

export default function OrderStatusPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [tracking, setTracking] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshingTracking, setIsRefreshingTracking] = useState(false);

  useEffect(() => {
    let isMounted = true;

    const loadOrder = async () => {
      setIsLoading(true);
      setError('');
      try {
        const [orderPayload, trackingPayload] = await Promise.all([
          getOrderStatus(orderId),
          getOrderTracking(orderId),
        ]);
        if (isMounted) {
          setOrder(orderPayload);
          setTracking(trackingPayload);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Could not fetch order status.');
          setOrder(null);
          setTracking(null);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadOrder();

    return () => {
      isMounted = false;
    };
  }, [orderId]);

  const handleRefreshTracking = async () => {
    setError('');
    setIsRefreshingTracking(true);

    try {
      const payload = await refreshOrderTracking(orderId);
      setTracking(payload);
    } catch (err) {
      setError(err.message || 'Could not refresh order tracking.');
    } finally {
      setIsRefreshingTracking(false);
    }
  };

  return (
    <section className="card">
      <h2>Order #{orderId}</h2>
      <p>
        <Link to="/restaurants">Place another order</Link>
      </p>

      {isLoading && <p>Loading order status...</p>}
      {error && <p className="error">{error}</p>}

      {!isLoading && !error && order && (
        <>
          <div className="info-grid">
            <article className="info-card">
              <h3>Order summary</h3>
              <p>
                <strong>Order status:</strong> {order.order_status || 'Unknown'}
              </p>
              <p>
                <strong>Payment status:</strong> {order.payment_status || 'Unknown'}
              </p>
              <p>
                <strong>Total:</strong> ${Number(order.cost || 0).toFixed(2)}
              </p>
            </article>

            {tracking && (
              <article className="info-card">
                <div className="section-heading">
                  <h3>Tracking</h3>
                  <button
                    type="button"
                    className="secondary-button"
                    disabled={isRefreshingTracking}
                    onClick={handleRefreshTracking}
                  >
                    {isRefreshingTracking ? 'Refreshing...' : 'Refresh'}
                  </button>
                </div>
                <p>
                  <strong>Current location:</strong> {tracking.current_location}
                </p>
                <p>
                  <strong>Distance:</strong> {tracking.distance_km} km
                </p>
                <p>
                  <strong>Estimated time:</strong>{' '}
                  {tracking.estimated_time_minutes} minutes
                </p>
                <p>
                  <strong>Driver:</strong> {tracking.driver || 'Not assigned yet'}
                </p>
                <p>
                  <strong>Status message:</strong> {tracking.status_message}
                </p>
              </article>
            )}
          </div>

          <p className="helper-text">
            Want to demo ratings and reviews too? Open the Reviews page and use
            one of the seeded completed order ids.
          </p>
          <details>
            <summary>Raw order payload</summary>
            <pre>{prettyPrintObject(order)}</pre>
          </details>
        </>
      )}
    </section>
  );
}
