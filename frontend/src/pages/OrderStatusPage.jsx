import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getOrderStatus } from '../lib/api';

function prettyPrintObject(value) {
  return JSON.stringify(value, null, 2);
}

export default function OrderStatusPage() {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadOrder = async () => {
      setIsLoading(true);
      setError('');
      try {
        const payload = await getOrderStatus(orderId);
        if (isMounted) {
          setOrder(payload);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Could not fetch order status.');
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
          <p>
            <strong>Order status:</strong> {order.order_status || 'Unknown'}
          </p>
          <p>
            <strong>Payment status:</strong> {order.payment_status || 'Unknown'}
          </p>
          <p>
            <strong>Total:</strong> ${Number(order.cost || 0).toFixed(2)}
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
