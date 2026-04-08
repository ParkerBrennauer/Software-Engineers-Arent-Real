import { useEffect, useMemo, useState } from 'react';
import {
  addFavoriteRestaurant,
  getFavoriteRestaurants,
  getRestaurants,
  removeFavoriteRestaurant,
} from '../lib/api';
import {
  DEFAULT_DEMO_CUSTOMER_ID,
  savePreferredCustomerId,
} from '../lib/demoData';

function normalizeRestaurants(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (payload && typeof payload === 'object') {
    return Object.values(payload);
  }

  return [];
}

export default function FavoritesPage() {
  const [customerId, setCustomerId] = useState(DEFAULT_DEMO_CUSTOMER_ID);
  const [restaurants, setRestaurants] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [pendingRestaurantId, setPendingRestaurantId] = useState(null);

  useEffect(() => {
    savePreferredCustomerId(customerId);
  }, [customerId]);

  useEffect(() => {
    let isMounted = true;

    const loadPage = async () => {
      setIsLoading(true);
      setError('');
      setMessage('');

      try {
        const [restaurantPayload, favoritesPayload] = await Promise.all([
          getRestaurants(),
          getFavoriteRestaurants(customerId),
        ]);

        if (!isMounted) {
          return;
        }

        setRestaurants(normalizeRestaurants(restaurantPayload));
        setFavoriteIds(favoritesPayload.favorite_restaurants || []);
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Could not load favorite restaurants.');
          setFavoriteIds([]);
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadPage();

    return () => {
      isMounted = false;
    };
  }, [customerId]);

  const favoriteRestaurants = useMemo(
    () =>
      restaurants.filter((restaurant) =>
        favoriteIds.includes(Number(restaurant.restaurant_id)),
      ),
    [restaurants, favoriteIds],
  );

  const toggleFavorite = async (restaurantId) => {
    setPendingRestaurantId(restaurantId);
    setError('');
    setMessage('');

    try {
      const isFavorite = favoriteIds.includes(restaurantId);
      const response = isFavorite
        ? await removeFavoriteRestaurant(customerId, restaurantId)
        : await addFavoriteRestaurant(customerId, restaurantId);

      setFavoriteIds(response.favorite_restaurants || []);
      setMessage(response.message);
    } catch (err) {
      setError(err.message || 'Could not update favorite restaurants.');
    } finally {
      setPendingRestaurantId(null);
    }
  };

  return (
    <section className="card">
      <h2>Favorite restaurants</h2>
      <p>
        Choose a customer id, then add or remove favorite restaurants using the
        existing backend favorites endpoints.
      </p>

      <label className="search-input">
        Customer id
        <input
          value={customerId}
          onChange={(event) => setCustomerId(event.target.value)}
          placeholder="Paste a customer id from customers.json"
        />
      </label>

      {isLoading && <p>Loading favorites...</p>}
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      {!isLoading && !error && (
        <>
          <section className="stack-section">
            <div className="section-heading">
              <h3>Current favorites</h3>
              <span className="pill">{favoriteRestaurants.length} saved</span>
            </div>
            {favoriteRestaurants.length === 0 && (
              <p>No favorite restaurants saved for this customer yet.</p>
            )}
            <div className="restaurant-grid">
              {favoriteRestaurants.map((restaurant) => (
                <article
                  key={`favorite_${restaurant.restaurant_id}`}
                  className="restaurant-card"
                >
                  <h3>Restaurant #{restaurant.restaurant_id}</h3>
                  <p>
                    <strong>Cuisine:</strong> {restaurant.cuisine || 'Unknown'}
                  </p>
                  <button
                    type="button"
                    className="secondary-button"
                    disabled={pendingRestaurantId === restaurant.restaurant_id}
                    onClick={() => toggleFavorite(Number(restaurant.restaurant_id))}
                  >
                    {pendingRestaurantId === restaurant.restaurant_id
                      ? 'Updating...'
                      : 'Remove favorite'}
                  </button>
                </article>
              ))}
            </div>
          </section>

          <section className="stack-section">
            <div className="section-heading">
              <h3>All restaurants</h3>
              <span className="pill">{restaurants.length} total</span>
            </div>
            <div className="restaurant-grid">
              {restaurants.map((restaurant) => {
                const restaurantId = Number(restaurant.restaurant_id);
                const isFavorite = favoriteIds.includes(restaurantId);

                return (
                  <article
                    key={`all_${restaurant.restaurant_id}`}
                    className="restaurant-card"
                  >
                    <h3>Restaurant #{restaurant.restaurant_id}</h3>
                    <p>
                      <strong>Cuisine:</strong> {restaurant.cuisine || 'Unknown'}
                    </p>
                    <button
                      type="button"
                      disabled={pendingRestaurantId === restaurantId}
                      onClick={() => toggleFavorite(restaurantId)}
                    >
                      {pendingRestaurantId === restaurantId
                        ? 'Updating...'
                        : isFavorite
                          ? 'Unfavorite'
                          : 'Add to favorites'}
                    </button>
                  </article>
                );
              })}
            </div>
          </section>
        </>
      )}
    </section>
  );
}
