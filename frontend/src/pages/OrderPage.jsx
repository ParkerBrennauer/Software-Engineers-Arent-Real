import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { createOrder, getRestaurantMenu } from '../lib/api';
import { useAuth } from '../state/AuthContext';

function deriveRestaurantName(restaurantId) {
  return `Restaurant_${restaurantId}`;
}

function deriveOrderItems(selectedItems) {
  return selectedItems.map((item) => ({
    item_name: item.item_name,
    price: Number(item.cost || 0),
  }));
}

export default function OrderPage() {
  const { restaurantId } = useParams();
  const numericRestaurantId = Number(restaurantId);

  const [menuItems, setMenuItems] = useState([]);
  const [selectedItemKeys, setSelectedItemKeys] = useState([]);
  const [distance, setDistance] = useState('3');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    const loadMenu = async () => {
      setIsLoading(true);
      setError('');

      try {
        const payload = await getRestaurantMenu(numericRestaurantId);
        if (isMounted) {
          const normalized = Array.isArray(payload)
            ? payload
            : payload && typeof payload === 'object'
              ? Object.values(payload)
              : [];
          setMenuItems(normalized);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Could not load restaurant menu.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    if (Number.isFinite(numericRestaurantId)) {
      loadMenu();
    } else {
      setError('Invalid restaurant id.');
      setIsLoading(false);
    }

    return () => {
      isMounted = false;
    };
  }, [numericRestaurantId]);

  const selectedItems = useMemo(
    () =>
      menuItems.filter((item) =>
        selectedItemKeys.includes(`${item.item_name}_${item.restaurant_id}`),
      ),
    [menuItems, selectedItemKeys],
  );

  const estimatedSubtotal = useMemo(
    () =>
      selectedItems.reduce((total, item) => total + Number(item.cost || 0), 0),
    [selectedItems],
  );

  const toggleItem = (item) => {
    const key = `${item.item_name}_${item.restaurant_id}`;
    setSelectedItemKeys((current) =>
      current.includes(key)
        ? current.filter((entry) => entry !== key)
        : [...current, key],
    );
  };

  const submitOrder = async (event) => {
    event.preventDefault();
    setError('');

    if (selectedItems.length === 0) {
      setError('Please select at least one menu item.');
      return;
    }

    setIsSubmitting(true);

    try {
      const primaryCuisine = selectedItems[0]?.cuisine || 'Unknown';
      const payload = {
        items: deriveOrderItems(selectedItems),
        cost: estimatedSubtotal,
        restaurant: deriveRestaurantName(numericRestaurantId),
        customer: user?.username || '',
        time: 0,
        cuisine: primaryCuisine,
        distance: Number(distance),
      };

      const created = await createOrder(payload);
      navigate(`/orders/${created.id}`);
    } catch (err) {
      setError(err.message || 'Order creation failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="card">
      <h2>Order from restaurant #{restaurantId}</h2>
      <p>
        <Link to="/restaurants">Back to restaurant list</Link>
      </p>

      {isLoading && <p>Loading menu...</p>}
      {error && <p className="error">{error}</p>}

      {!isLoading && !error && (
        <form onSubmit={submitOrder} className="form-grid">
          <div className="menu-list">
            <h3>Menu</h3>
            {menuItems.length === 0 && <p>No menu items found.</p>}
            {menuItems.map((item) => {
              const key = `${item.item_name}_${item.restaurant_id}`;
              const isChecked = selectedItemKeys.includes(key);
              return (
                <label key={key} className="menu-row">
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => toggleItem(item)}
                  />
                  <span>
                    {item.item_name} - ${Number(item.cost || 0).toFixed(2)}
                  </span>
                </label>
              );
            })}
          </div>

          <label>
            Estimated distance (km)
            <input
              type="number"
              min="0"
              step="0.1"
              value={distance}
              onChange={(event) => setDistance(event.target.value)}
              required
            />
          </label>

          <p>
            <strong>Subtotal:</strong> ${estimatedSubtotal.toFixed(2)}
          </p>

          <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Placing order...' : 'Place order'}
          </button>
        </form>
      )}
    </section>
  );
}
