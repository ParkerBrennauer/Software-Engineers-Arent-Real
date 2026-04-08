import { useState } from 'react';
import { applyDiscount } from '../../api/discountApi';

export default function ApplyDiscountForm() {
  const [orderTotal, setOrderTotal] = useState('24.99');
  const [discountCode, setDiscountCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setResult(null);
    setLoading(true);
    try {
      const data = await applyDiscount({
        orderTotal,
        discountCode,
      });
      setResult(data);
    } catch (err) {
      setError(err.message || 'Could not apply code.');
    } finally {
      setLoading(false);
    }
  };

  const discounted =
    result && typeof result.discounted_total === 'number'
      ? result.discounted_total
      : result?.discounted_total;

  return (
    <section className="discount-card">
      <h3>Apply a discount</h3>
      <p className="discount-hint">
        Enter your order total and a valid code. The server returns the new total
        after the discount multiplier is applied.
      </p>
      <form className="discount-form" onSubmit={handleSubmit}>
        <label>
          Order total ($)
          <input
            type="number"
            step="0.01"
            min="0"
            value={orderTotal}
            onChange={(e) => setOrderTotal(e.target.value)}
            required
            disabled={loading}
          />
        </label>
        <label>
          Discount code
          <input
            value={discountCode}
            onChange={(e) => setDiscountCode(e.target.value)}
            placeholder="SAVE10"
            required
            disabled={loading}
            autoComplete="off"
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Applying…' : 'Apply code'}
        </button>
      </form>
      {discounted !== undefined && discounted !== null && (
        <p className="discount-success">
          Discounted total: <strong>${Number(discounted).toFixed(2)}</strong>
        </p>
      )}
      {error && <p className="discount-error">{error}</p>}
    </section>
  );
}
