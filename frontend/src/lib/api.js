const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

async function parseResponse(response) {
  const text = await response.text();
  let payload = null;

  if (text) {
    try {
      payload = JSON.parse(text);
    } catch {
      payload = text;
    }
  }

  if (!response.ok) {
    const detailMessage =
      (payload && typeof payload === 'object' && payload.detail) ||
      `Request failed with status ${response.status}`;
    throw new ApiError(detailMessage, response.status, payload);
  }

  return payload;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  });

  return parseResponse(response);
}

export async function loginUser({ username, password }) {
  return request('/users/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function registerCustomer({
  username,
  password,
  email,
  name,
  paymentType,
  paymentDetails,
}) {
  return request('/users/register/customer', {
    method: 'POST',
    body: JSON.stringify({
      username,
      password,
      email,
      name,
      payment_type: paymentType,
      payment_details: paymentDetails,
    }),
  });
}

export async function getRestaurants() {
  return request('/restaurants');
}

export async function getRestaurantMenu(restaurantId) {
  return request(`/restaurants/${restaurantId}/menu`);
}

export async function createOrder(orderPayload) {
  return request('/orders/place', {
    method: 'POST',
    body: JSON.stringify(orderPayload),
  });
}

export async function getOrderStatus(orderId) {
  return request(`/orders/${orderId}`);
}

export async function getOrderTracking(orderId) {
  return request(`/orders/${orderId}/tracking`);
}

export async function refreshOrderTracking(orderId) {
  return request(`/orders/${orderId}/tracking/refresh`, {
    method: 'POST',
  });
}

export async function getFavoriteRestaurants(customerId) {
  return request(`/customers/${customerId}/favorites/restaurants`);
}

export async function addFavoriteRestaurant(customerId, restaurantId) {
  return request(`/customers/${customerId}/favorites/restaurants/${restaurantId}`, {
    method: 'POST',
  });
}

export async function removeFavoriteRestaurant(customerId, restaurantId) {
  return request(`/customers/${customerId}/favorites/restaurants/${restaurantId}`, {
    method: 'DELETE',
  });
}

export async function getFeedbackPrompt(orderId) {
  return request(`/orders/${orderId}/feedback-prompt`);
}

export async function submitRating(orderId, stars) {
  return request(`/orders/${orderId}/rating`, {
    method: 'POST',
    body: JSON.stringify({ stars }),
  });
}

export async function submitReview(orderId, reviewText) {
  return request(`/orders/${orderId}/review`, {
    method: 'POST',
    body: JSON.stringify({ review_text: reviewText }),
  });
}

export async function editReview(orderId, { stars, reviewText }) {
  const payload = {};

  if (stars !== '' && stars !== null && stars !== undefined) {
    payload.stars = Number(stars);
  }
  if (reviewText !== '' && reviewText !== null && reviewText !== undefined) {
    payload.review_text = reviewText;
  }

  return request(`/orders/${orderId}/review`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function deleteReview(orderId) {
  return request(`/orders/${orderId}/review`, {
    method: 'DELETE',
  });
}

export async function reportReview(orderId, { reason, description }) {
  return request(`/orders/${orderId}/report`, {
    method: 'POST',
    body: JSON.stringify({
      reason,
      description: description || null,
    }),
  });
}

export async function getRestaurantReviews(restaurantId, stars) {
  const params = new URLSearchParams();
  if (stars) {
    params.set('stars', stars);
  }

  const suffix = params.toString() ? `?${params.toString()}` : '';
  return request(`/orders/restaurants/${restaurantId}/reviews${suffix}`);
}
