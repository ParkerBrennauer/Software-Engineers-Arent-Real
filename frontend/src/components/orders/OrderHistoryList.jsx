export default function OrderHistoryList({ orders }) {
  return (
    <div className="cards-grid">
      {orders.map((order) => {
        // TODO: Match these fields to your real backend order payload.
        const id = order.id ?? order.order_id;
        const restaurant = order.restaurant_name ?? order.restaurant ?? 'Restaurant';
        const total = order.total_amount ?? order.total ?? 0;
        const status = order.status ?? 'Unknown';
        const placedAt = order.placed_at ?? order.created_at ?? null;

        return (
          <article key={id} className="card">
            <h3>Order #{id}</h3>
            <p className="card-subtitle">{restaurant}</p>
            <div className="meta-row">
              <span>Status: {status}</span>
              <span>Total: ${Number(total).toFixed(2)}</span>
            </div>
            <p className="muted-text">
              {placedAt ? `Placed: ${new Date(placedAt).toLocaleString()}` : 'Placed date unavailable'}
            </p>
          </article>
        );
      })}
    </div>
  );
}

