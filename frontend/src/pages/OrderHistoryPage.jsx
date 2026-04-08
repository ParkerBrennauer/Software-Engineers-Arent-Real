import { useEffect, useState } from 'react';
import OrderHistoryList from '../components/orders/OrderHistoryList';
import EmptyState from '../components/ui/EmptyState';
import ErrorState from '../components/ui/ErrorState';
import LoadingState from '../components/ui/LoadingState';
import { fetchOrderHistory } from '../services/featureApi';

const DEMO_USER_ID = 1; // TODO: Replace with real authenticated user id.

export default function OrderHistoryPage() {
  const [orders, setOrders] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  async function loadOrders() {
    setIsLoading(true);
    setError('');

    try {
      const result = await fetchOrderHistory(DEMO_USER_ID);
      const orderItems = result?.orders ?? result?.data ?? [];
      setOrders(Array.isArray(orderItems) ? orderItems : []);
    } catch (err) {
      setError(err.message || 'Unable to load order history right now.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadOrders();
  }, []);

  return (
    <section>
      <div className="title-row">
        <h2>Order History</h2>
        <button className="secondary-button" type="button" onClick={loadOrders}>
          Refresh
        </button>
      </div>

      {isLoading ? <LoadingState message="Loading past orders..." /> : null}
      {!isLoading && error ? <ErrorState message={error} onRetry={loadOrders} /> : null}
      {!isLoading && !error && orders.length === 0 ? (
        <EmptyState message="No past orders yet. Your completed orders will appear here." />
      ) : null}
      {!isLoading && !error && orders.length > 0 ? <OrderHistoryList orders={orders} /> : null}
    </section>
  );
}

