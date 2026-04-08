import { useMemo, useState } from 'react';
import { useAuth } from '../state/AuthContext';
import ApplyDiscountForm from '../components/discounts/ApplyDiscountForm';
import DiscountManager from '../components/discounts/DiscountManager';
import '../styles/discounts.css';

const VIEW_KEY = 'food-delivery-discount-ui-mode';

/**
 * Shows owner tools vs customer apply form based on user.role,
 * with a fallback toggle when role is unknown (demo / local dev).
 */
export default function DiscountsPage() {
  const { user } = useAuth();
  const [demoMode, setDemoMode] = useState(() => {
    try {
      return sessionStorage.getItem(VIEW_KEY) || '';
    } catch {
      return '';
    }
  });

  const inferredOwner = user?.role === 'owner';
  const inferredCustomer = user?.role === 'customer';

  const effectiveIsOwner = useMemo(() => {
    if (demoMode === 'owner') return true;
    if (demoMode === 'customer') return false;
    if (inferredOwner) return true;
    if (inferredCustomer) return false;
    return false;
  }, [demoMode, inferredOwner, inferredCustomer]);

  const [restaurantId, setRestaurantId] = useState(() => {
    if (user?.restaurant_id != null) return String(user.restaurant_id);
    return '1';
  });

  const persistMode = (mode) => {
    setDemoMode(mode);
    try {
      sessionStorage.setItem(VIEW_KEY, mode);
    } catch {
      /* ignore */
    }
  };

  return (
    <div className="discounts-page">
      <section className="card discounts-intro">
        <h2>Discounts</h2>
        <p>
          Connect the app to your API using{' '}
          <code>VITE_API_BASE_URL</code> or the Vite <code>/api</code> proxy (see{' '}
          <code>vite.config.js</code>).
        </p>
        {user?.role == null && (
          <div className="discount-demo-banner">
            <strong>Demo:</strong> Your login response may not include{' '}
            <code>role</code>. Choose a view:
            <div className="discount-demo-actions">
              <button
                type="button"
                className={demoMode === 'owner' ? 'active' : ''}
                onClick={() => persistMode('owner')}
              >
                Owner (manage)
              </button>
              <button
                type="button"
                className={demoMode === 'customer' ? 'active' : ''}
                onClick={() => persistMode('customer')}
              >
                Customer (apply)
              </button>
              <button type="button" onClick={() => persistMode('')}>
                Use profile role only
              </button>
            </div>
          </div>
        )}
      </section>

      {effectiveIsOwner ? (
        <>
          <section className="card discount-owner-settings">
            <label>
              Restaurant ID for this session
              <input
                type="number"
                min="1"
                value={restaurantId}
                onChange={(e) => setRestaurantId(e.target.value)}
              />
            </label>
            <p className="discount-hint">
              Must match <code>restaurant_id</code> for your owner account on the
              server. Override here if your profile does not store it yet.
            </p>
          </section>
          <DiscountManager restaurantId={restaurantId} />
        </>
      ) : (
        <ApplyDiscountForm />
      )}
    </div>
  );
}
