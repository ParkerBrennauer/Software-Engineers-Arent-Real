import { useMemo, useState } from 'react';
import CreateDiscountForm from './CreateDiscountForm';
import DiscountList from './DiscountList';

/**
 * Owner-only: manage discounts for one restaurant (restaurantId from props).
 */
export default function DiscountManager({ restaurantId }) {
  const [rows, setRows] = useState([]);

  const numericId = useMemo(() => {
    if (restaurantId === '' || restaurantId === undefined || restaurantId === null) {
      return null;
    }
    const n = Number(restaurantId);
    return Number.isNaN(n) ? null : n;
  }, [restaurantId]);

  const handleCreated = (row) => {
    setRows((prev) => {
      const next = prev.filter((r) => r.discount_code !== row.discount_code);
      return [...next, row];
    });
  };

  const handleRemoved = (code) => {
    setRows((prev) => prev.filter((r) => r.discount_code !== code));
  };

  return (
    <div className="discount-manager">
      <header className="discount-manager-header">
        <h2>Discount management</h2>
        <p className="discount-muted">
          You must be logged in on the server (same session as the API). Only
          restaurant owners can create or delete discounts.
        </p>
      </header>

      {numericId === null ? (
        <p className="discount-error">
          Set a restaurant ID to manage discounts for that restaurant.
        </p>
      ) : (
        <>
          <CreateDiscountForm
            restaurantId={numericId}
            onCreated={handleCreated}
          />
          <DiscountList discounts={rows} onRemoved={handleRemoved} />
        </>
      )}
    </div>
  );
}
