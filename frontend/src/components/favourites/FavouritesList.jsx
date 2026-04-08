import FavouriteButton from './FavouriteButton';

export default function FavouritesList({ favourites, onToggleFavourite }) {
  return (
    <div className="cards-grid">
      {favourites.map((item) => {
        // TODO: Match these fields to your real backend shape.
        const id = item.id ?? item.item_id;
        const title = item.name ?? item.title ?? `Item #${id}`;
        const subtitle = item.restaurant_name ?? item.category ?? 'Favourite item';
        const description = item.description ?? 'No description provided.';
        const isFavourite = item.isFavourite ?? item.is_favourite ?? true;

        return (
          <article key={id} className="card">
            <h3>{title}</h3>
            <p className="card-subtitle">{subtitle}</p>
            <p>{description}</p>
            <FavouriteButton
              isFavourite={isFavourite}
              onToggle={(nextState) => onToggleFavourite(id, nextState)}
            />
          </article>
        );
      })}
    </div>
  );
}

