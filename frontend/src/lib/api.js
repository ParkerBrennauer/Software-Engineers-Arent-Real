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

export async function applyDiscountCode({ orderTotal, discountCode }) {
  return request('/discounts/apply', {
    method: 'POST',
    body: JSON.stringify({
      order_total: orderTotal,
      discount_code: discountCode,
    }),
  });
}

export async function getOrderStatus(orderId) {
  return request(`/orders/${orderId}`);
}
