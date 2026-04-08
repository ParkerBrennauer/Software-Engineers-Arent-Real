/**
 * Discount API helpers.
 *
 * Base URL: set VITE_API_BASE_URL in .env (e.g. http://localhost:8000)
 * or rely on Vite proxy so requests go to /api → backend (see vite.config.js).
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export class DiscountApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = 'DiscountApiError';
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
    throw new DiscountApiError(detailMessage, response.status, payload);
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

/**
 * Create a discount (restaurant owner only; requires active session on backend).
 * Body matches DiscountCreate: discount_rate, discount_code, restaurant_id
 */
export async function createDiscount({ discountRate, discountCode, restaurantId }) {
  return request('/discounts/', {
    method: 'POST',
    body: JSON.stringify({
      discount_rate: Number(discountRate),
      discount_code: String(discountCode).trim(),
      restaurant_id: Number(restaurantId),
    }),
  });
}

/**
 * Apply a code to an order total (public/customer).
 */
export async function applyDiscount({ orderTotal, discountCode }) {
  return request('/discounts/apply', {
    method: 'POST',
    body: JSON.stringify({
      order_total: Number(orderTotal),
      discount_code: String(discountCode).trim(),
    }),
  });
}

/**
 * Delete a discount by code (owner only).
 */
export async function deleteDiscountByCode(discountCode) {
  const code = encodeURIComponent(String(discountCode).trim());
  return request(`/discounts/${code}`, {
    method: 'DELETE',
  });
}
