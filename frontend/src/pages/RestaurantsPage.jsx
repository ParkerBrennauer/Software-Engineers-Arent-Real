import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  addFavoriteRestaurant,
  getFavoriteRestaurants,
  getRestaurants,
  removeFavoriteRestaurant,
} from '../lib/api';
import {
  loadPreferredCustomerId,
  savePreferredCustomerId,
} from '../lib/demoData';
import { useAuth } from '../state/AuthContext';

function normalizeRestaurants(payload) {
  if (Array.isArray(payload)) {
    return payload;
  }

  if (payload && typeof payload === 'object') {
    return Object.values(payload);
  }

  return [];
}

function averageRating(ratings) {
  if (!ratings || typeof ratings !== 'object') {
    return null;
  }

  let weightedTotal = 0;
  let totalCount = 0;

  Object.entries(ratings).forEach(([score, count]) => {
    const numericScore = Number(score);
    const numericCount = Number(count);

    if (Number.isFinite(numericScore) && Number.isFinite(numericCount)) {
      weightedTotal += numericScore * numericCount;
      totalCount += numericCount;
    }
  });

  if (totalCount === 0) {
    return null;
  }

  return (weightedTotal / totalCount).toFixed(2);
}

export default function RestaurantsPage() {
  const { user } = useAuth();
  const [customerId, setCustomerId] = useState(() =>
    loadPreferredCustomerId(user?.username),
  );
  const [restaurants, setRestaurants] = useState([]);
  const [favoriteIds, setFavoriteIds] = useState([]);
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [pendingRestaurantId, setPendingRestaurantId] = useState(null);

  useEffect(() => {
    savePreferredCustomerId(customerId);
  }, [customerId]);

  useEffect(() => {
    let isMounted = true;

    const loadRestaurants = async () => {
      setIsLoading(true);
      setError('');
      setMessage('');

      try {
        const [payload, favoritesPayload] = await Promise.all([
          getRestaurants(),
          getFavoriteRestaurants(customerId),
        ]);
        if (isMounted) {
          setRestaurants(normalizeRestaurants(payload));
          setFavoriteIds(favoritesPayload.favorite_restaurants || []);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Could not load restaurants.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    loadRestaurants();

    return () => {
      isMounted = false;
    };
  }, [customerId]);

  const filteredRestaurants = useMemo(() => {
    const lowered = query.trim().toLowerCase();
    if (!lowered) {
      return restaurants;
    }

    return restaurants.filter((restaurant) => {
      const cuisine = String(restaurant.cuisine || '').toLowerCase();
      const id = String(restaurant.restaurant_id || '').toLowerCase();
      return cuisine.includes(lowered) || id.includes(lowered);
    });
  }, [restaurants, query]);

  const toggleFavorite = async (restaurantId) => {
    setPendingRestaurantId(restaurantId);
    setError('');
    setMessage('');

    try {
      const response = favoriteIds.includes(restaurantId)
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
      <h2>Restaurants</h2>
      <p>Browse available restaurants from the backend API and save favorites.</p>

      <label className="search-input">
        Customer id for favorites
        <input
          value={customerId}
          onChange={(event) => setCustomerId(event.target.value)}
          placeholder="Paste a customer id from customers.json"
        />
      </label>

      <label className="search-input">
        Search by cuisine or restaurant id
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="e.g. asian or 30"
        />
      </label>

      {isLoading && <p>Loading restaurants...</p>}
      {error && <p className="error">{error}</p>}
      {message && <p className="success">{message}</p>}

      {!isLoading && !error && filteredRestaurants.length === 0 && (
        <p>No restaurants matched your search.</p>
      )}

      <div className="restaurant-grid">
        {filteredRestaurants.map((restaurant) => (
          <article key={restaurant.restaurant_id} className="restaurant-card">
            <h3>Restaurant #{restaurant.restaurant_id}</h3>
            <p>
              <strong>Cuisine:</strong> {restaurant.cuisine || 'Unknown'}
            </p>
            <p>
              <strong>Average rating:</strong>{' '}
              {averageRating(restaurant.ratings) ?? 'No ratings yet'}
            </p>
            <div className="button-row">
              <Link to={`/restaurants/${restaurant.restaurant_id}/order`}>
                View menu and order
              </Link>
              <button
                type="button"
                className="secondary-button"
                disabled={pendingRestaurantId === Number(restaurant.restaurant_id)}
                onClick={() => toggleFavorite(Number(restaurant.restaurant_id))}
              >
                {pendingRestaurantId === Number(restaurant.restaurant_id)
                  ? 'Updating...'
                  : favoriteIds.includes(Number(restaurant.restaurant_id))
                    ? 'Unfavorite'
                    : 'Favorite'}
              </button>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
