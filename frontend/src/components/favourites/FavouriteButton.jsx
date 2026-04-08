import { useState } from 'react';

export default function FavouriteButton({
  isFavourite,
  onToggle,
  disabled = false,
}) {
  const [isUpdating, setIsUpdating] = useState(false);

  async function handleClick() {
    if (!onToggle || disabled || isUpdating) {
      return;
    }

    setIsUpdating(true);
    try {
      await onToggle(!isFavourite);
    } finally {
      setIsUpdating(false);
    }
  }

  return (
    <button
      type="button"
      className={`favourite-button ${isFavourite ? 'active' : ''}`}
      onClick={handleClick}
      disabled={disabled || isUpdating}
    >
      {isUpdating ? 'Saving...' : isFavourite ? 'Remove Favourite' : 'Add Favourite'}
    </button>
  );
}

