import { useEffect, useState } from 'react';
import FavouritesList from '../components/favourites/FavouritesList';
import EmptyState from '../components/ui/EmptyState';
import ErrorState from '../components/ui/ErrorState';
import LoadingState from '../components/ui/LoadingState';
import { fetchFavourites, updateFavourite } from '../services/featureApi';

const DEMO_USER_ID = 1; // TODO: Replace with real authenticated user id.

export default function FavouritesPage() {
  const [favourites, setFavourites] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionError, setActionError] = useState('');

  async function loadFavourites() {
    setIsLoading(true);
    setError('');

    try {
      const result = await fetchFavourites(DEMO_USER_ID);
      const entries = result?.favourites ?? result?.data ?? [];
      setFavourites(Array.isArray(entries) ? entries : []);
    } catch (err) {
      setError(err.message || 'Unable to load favourites right now.');
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    loadFavourites();
  }, []);

  async function handleToggleFavourite(itemId, nextIsFavourite) {
    setActionError('');

    const previous = favourites;

    // Optimistic UI: update immediately, rollback if API fails.
    setFavourites((current) =>
      current.map((item) => {
        const id = item.id ?? item.item_id;
        if (id !== itemId) {
          return item;
        }
        return {
          ...item,
          isFavourite: nextIsFavourite,
          is_favourite: nextIsFavourite,
        };
      }),
    );

    try {
      await updateFavourite({
        userId: DEMO_USER_ID,
        itemId,
        isFavourite: nextIsFavourite,
      });

      await loadFavourites();
    } catch (err) {
      setFavourites(previous);
      setActionError(err.message || 'Could not update favourite. Please try again.');
    }
  }

  return (
    <section>
      <div className="title-row">
        <h2>Favourites</h2>
        <button className="secondary-button" type="button" onClick={loadFavourites}>
          Refresh
        </button>
      </div>

      {isLoading ? <LoadingState message="Loading favourites..." /> : null}
      {!isLoading && error ? <ErrorState message={error} onRetry={loadFavourites} /> : null}
      {!isLoading && !error && favourites.length === 0 ? (
        <EmptyState message="No favourites yet. Add favourites to see them here." />
      ) : null}
      {!isLoading && !error && favourites.length > 0 ? (
        <FavouritesList
          favourites={favourites}
          onToggleFavourite={handleToggleFavourite}
        />
      ) : null}

      {actionError ? <p className="error-inline">{actionError}</p> : null}
    </section>
  );
}

