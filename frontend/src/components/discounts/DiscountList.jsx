import { useState } from 'react';
import { deleteDiscountByCode } from '../../api/discountApi';

export default function DiscountList({ discounts, onRemoved }) {
  const [pendingCode, setPendingCode] = useState(null);
  const [error, setError] = useState(null);

  const handleDelete = async (code) => {
    setError(null);
    setPendingCode(code);
    try {
      await deleteDiscountByCode(code);
      onRemoved?.(code);
    } catch (err) {
      setError(err.message || 'Delete failed.');
    } finally {
      setPendingCode(null);
    }
  };

  if (!discounts.length) {
    return (
      <section className="discount-card">
        <h3>Your discounts</h3>
        <p className="discount-muted">No discounts yet. Create one above.</p>
      </section>
    );
  }

  return (
    <section className="discount-card">
      <h3>Your discounts</h3>
      <p className="discount-hint">
        Codes created in this session are listed here. After a page refresh, add
        them again or wire a backend list endpoint if you need persistence in the
        UI.
      </p>
      <div className="discount-table-wrap">
        <table className="discount-table">
          <thead>
            <tr>
              <th>Code</th>
              <th>Restaurant ID</th>
              <th>Rate</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {discounts.map((row) => (
              <tr key={row.discount_code}>
                <td>
                  <code>{row.discount_code}</code>
                </td>
                <td>{row.restaurant_id}</td>
                <td>{row.discount_rate}</td>
                <td>
                  <button
                    type="button"
                    className="discount-btn-danger"
                    onClick={() => handleDelete(row.discount_code)}
                    disabled={pendingCode === row.discount_code}
                  >
                    {pendingCode === row.discount_code ? 'Removing…' : 'Delete'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {error && <p className="discount-error">{error}</p>}
    </section>
  );
}
