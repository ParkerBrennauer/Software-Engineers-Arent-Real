import { useState } from 'react';
import { createDiscount } from '../../api/discountApi';

/**
 * Owner form: creates a discount on the backend.
 * restaurantId: required by API; often the logged-in owner's restaurant.
 */
export default function CreateDiscountForm({
  restaurantId,
  onCreated,
  disabled = false,
}) {
  const [discountCode, setDiscountCode] = useState('');
  const [discountRate, setDiscountRate] = useState('0.9');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setLoading(true);
    try {
      const rid =
        restaurantId === '' || restaurantId === undefined
          ? null
          : Number(restaurantId);
      if (rid === null || Number.isNaN(rid)) {
        setError('Please set a valid restaurant ID.');
        return;
      }
      const res = await createDiscount({
        discountCode,
        discountRate,
        restaurantId: rid,
      });
      setMessage(res?.message || 'Discount created.');
      onCreated?.({
        discount_code: discountCode.trim(),
        discount_rate: Number(discountRate),
        restaurant_id: rid,
      });
      setDiscountCode('');
    } catch (err) {
      setError(err.message || 'Could not create discount.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="discount-card">
      <h3>Create discount</h3>
      <p className="discount-hint">
        Rate is the multiplier applied to the order total on the server (e.g.{' '}
        <code>0.9</code> → customer pays 90% of the total).
      </p>
      <form className="discount-form" onSubmit={handleSubmit}>
        <label>
          Discount code
          <input
            value={discountCode}
            onChange={(e) => setDiscountCode(e.target.value)}
            placeholder="SAVE10"
            required
            disabled={disabled || loading}
            autoComplete="off"
          />
        </label>
        <label>
          Discount rate (multiplier)
          <input
            type="number"
            step="0.01"
            min="0"
            max="1"
            value={discountRate}
            onChange={(e) => setDiscountRate(e.target.value)}
            required
            disabled={disabled || loading}
          />
        </label>
        <button type="submit" disabled={disabled || loading}>
          {loading ? 'Creating…' : 'Create discount'}
        </button>
      </form>
      {message && <p className="discount-success">{message}</p>}
      {error && <p className="discount-error">{error}</p>}
    </section>
  );
}
