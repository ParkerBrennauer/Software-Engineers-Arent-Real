import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { getRestaurants } from '../lib/api';

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
  const [restaurants, setRestaurants] = useState([]);
  const [query, setQuery] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadRestaurants = async () => {
      setIsLoading(true);
      setError('');

      try {
        const payload = await getRestaurants();
        if (isMounted) {
          setRestaurants(normalizeRestaurants(payload));
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
  }, []);

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

  return (
    <section className="card">
      <h2>Restaurants</h2>
      <p>Browse available restaurants from the backend API.</p>

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
            <Link to={`/restaurants/${restaurant.restaurant_id}/order`}>
              View menu and order
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}
