import { API_BASE_URL } from '../config/apiConfig';

async function handleApiResponse(response) {
  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message =
      payload?.message ||
      payload?.detail ||
      'Something went wrong while contacting the server.';
    throw new Error(message);
  }

  return payload;
}

// TODO: Confirm final route path and response shape with backend team.
export async function fetchOrderHistory(userId) {
  const response = await fetch(
    `${API_BASE_URL}/order_history?user_id=${encodeURIComponent(userId)}`,
  );
  return handleApiResponse(response);
}

// TODO: Confirm final route path and response shape with backend team.
export async function fetchFavourites(userId) {
  const response = await fetch(
    `${API_BASE_URL}/get_favourites?user_id=${encodeURIComponent(userId)}`,
  );
  return handleApiResponse(response);
}

// TODO: Confirm payload keys expected by update_favourite backend.
export async function updateFavourite({ userId, itemId, isFavourite }) {
  const response = await fetch(`${API_BASE_URL}/update_favourite`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      item_id: itemId,
      is_favourite: isFavourite,
    }),
  });
  return handleApiResponse(response);
}

