const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

function parseErrorDetail(body, response) {
  if (typeof body?.detail === "string") return body.detail;
  if (Array.isArray(body?.detail)) {
    return body.detail
      .map((d) => d?.msg || d?.message || JSON.stringify(d))
      .filter(Boolean)
      .join("; ");
  }
  if (typeof body?.message === "string") return body.message;
  return `Request failed: ${response.status}`;
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    });
  } catch {
    throw new Error("Network error. Please check connection and retry.");
  }
  const rawText = await response.text();
  let body = null;
  try {
    body = rawText ? JSON.parse(rawText) : null;
  } catch {
    body = rawText || null;
  }
  if (!response.ok) {
    const detail = parseErrorDetail(body, response);
    throw new Error(detail);
  }
  return body;
}

export const api = {
  users: {
    register: (payload) => request("/users/register", { method: "POST", body: JSON.stringify(payload) }),
    registerCustomer: (payload) => request("/users/register/customer", { method: "POST", body: JSON.stringify(payload) }),
    registerDriver: (payload) => request("/users/register/driver", { method: "POST", body: JSON.stringify(payload) }),
    login: (payload) => request("/users/login", { method: "POST", body: JSON.stringify(payload) }),
    logout: () => request("/users/logout", { method: "POST" }),
    currentUser: () => request("/users/current-user"),
    update: (payload) => request("/users", { method: "PATCH", body: JSON.stringify(payload) }),
    generate2FA: () => request("/users/2fa/generate", { method: "POST" }),
    verify2FA: (code) => request("/users/2fa/verify", { method: "POST", body: JSON.stringify({ code }) }),
    resetPassword: (username, payload) =>
      request(`/users/${encodeURIComponent(username)}/reset-password`, { method: "POST", body: JSON.stringify(payload) }),
    addAddress: (address) => request("/users/addresses", { method: "POST", body: JSON.stringify({ address }) }),
    getAddresses: () => request("/users/addresses"),
  },
  restaurants: {
    getAll: () => request("/restaurants"),
    search: (query) => request(`/restaurants/search/${encodeURIComponent(query)}`),
    advancedSearch: (payload) => request("/restaurants/search/advanced", { method: "POST", body: JSON.stringify(payload) }),
    menu: (restaurantId) => request(`/restaurants/${restaurantId}/menu`),
    create: (payload) => request("/restaurants", { method: "POST", body: JSON.stringify(payload) }),
    update: (restaurantId, payload) =>
      request(`/restaurants/${restaurantId}`, { method: "PATCH", body: JSON.stringify(payload) }),
  },
  items: {
    byKey: (itemKey) => request(`/items/${encodeURIComponent(itemKey)}`),
    byRestaurant: (restaurantId) => request(`/items/restaurant/${restaurantId}`),
    update: (itemKey, payload) =>
      request(`/items/${encodeURIComponent(itemKey)}`, { method: "PATCH", body: JSON.stringify(payload) }),
    create: (payload) => request("/items", { method: "POST", body: JSON.stringify(payload) }),
  },
  orders: {
    place: (payload) => request("/orders/place", { method: "POST", body: JSON.stringify(payload) }),
    addItems: (orderId, payload) => request(`/orders/${orderId}/items`, { method: "POST", body: JSON.stringify(payload) }),
    get: (orderId) => request(`/orders/${orderId}`),
    byRestaurant: (restaurant) => request(`/orders/restaurant/${encodeURIComponent(restaurant)}`),
    cancel: (orderId) => request(`/orders/${orderId}/cancel`, { method: "PUT" }),
    ready: (orderId) => request(`/orders/${orderId}/ready`, { method: "PUT" }),
    restaurantDelay: (orderId, reason) => request(`/orders/${orderId}/restaurant-delay?reason=${encodeURIComponent(reason)}`, { method: "PUT" }),
    byDriver: (driver) => request(`/orders/driver/${encodeURIComponent(driver)}`),
    pickup: (orderId) => request(`/orders/${orderId}/pickup`, { method: "PUT" }),
    driverDelay: (orderId, reason) => request(`/orders/${orderId}/driver-delay?reason=${encodeURIComponent(reason)}`, { method: "PUT" }),
    assignDriver: (orderId, driver) =>
      request(`/orders/${orderId}/assign-driver?driver=${encodeURIComponent(driver)}`, { method: "PUT" }),
    refund: (orderId) => request(`/orders/${orderId}/refund`, { method: "PUT" }),
    tracking: (orderId) => request(`/orders/${orderId}/tracking`),
    refreshTracking: (orderId) => request(`/orders/${orderId}/tracking/refresh`, { method: "POST" }),
    updateTracking: (orderId, payload) =>
      request(`/orders/${orderId}/tracking/status`, { method: "PATCH", body: JSON.stringify(payload) }),
    tip: (orderId, payload) => request(`/orders/${orderId}/tip`, { method: "POST", body: JSON.stringify(payload) }),
    payoutTip: (orderId) => request(`/orders/${orderId}/tip/payout`, { method: "POST" }),
  },
  reviews: {
    rate: (orderId, stars) => request(`/orders/${orderId}/rating`, { method: "POST", body: JSON.stringify({ stars }) }),
    review: (orderId, review_text) => request(`/orders/${orderId}/review`, { method: "POST", body: JSON.stringify({ review_text }) }),
    editReview: (orderId, payload) => request(`/orders/${orderId}/review`, { method: "PUT", body: JSON.stringify(payload) }),
    deleteReview: (orderId) => request(`/orders/${orderId}/review`, { method: "DELETE" }),
    feedbackPrompt: (orderId) => request(`/orders/${orderId}/feedback-prompt`),
    restaurantReviews: (restaurantId, stars) =>
      request(`/orders/restaurants/${restaurantId}/reviews${stars ? `?stars=${stars}` : ""}`),
    reportReview: (orderId, payload) => request(`/orders/${orderId}/report`, { method: "POST", body: JSON.stringify(payload) }),
  },
  customer: {
    getFavoriteRestaurants: () => request("/customers/favorites/restaurants"),
    addFavoriteRestaurant: (restaurantId) => request(`/customers/favorites/restaurants/${restaurantId}`, { method: "POST" }),
    removeFavoriteRestaurant: (restaurantId) => request(`/customers/favorites/restaurants/${restaurantId}`, { method: "DELETE" }),
    orderHistory: () => request("/customers/order-history", { method: "PATCH" }),
    toggleFavouriteItem: (itemKey) => request(`/customers/favourites/${encodeURIComponent(itemKey)}`, { method: "PATCH" }),
    getFavourites: () => request("/customers/favourites"),
  },
  discounts: {
    apply: (payload) => request("/discounts/apply", { method: "POST", body: JSON.stringify(payload) }),
    create: (payload) => request("/discounts/", { method: "POST", body: JSON.stringify(payload) }),
    remove: (discountCode) => request(`/discounts/${encodeURIComponent(discountCode)}`, { method: "DELETE" }),
  },
  restaurantAdministration: {
    assignStaff: (staff_username) => request("/restaurant_administration/staff", { method: "POST", body: JSON.stringify({ staff_username }) }),
    orders: (restaurantId) => request(`/restaurant_administration/restaurants/${restaurantId}/orders`),
    ordersByStatus: (restaurantId, order_status) =>
      request(`/restaurant_administration/restaurants/${restaurantId}/orders/filter/status?order_status=${encodeURIComponent(order_status)}`),
    ordersByDate: (restaurantId, start_time, end_time) =>
      request(`/restaurant_administration/restaurants/${restaurantId}/orders/filter/date?start_time=${start_time}&end_time=${end_time}`),
    ordersByStatusAndDate: (restaurantId, order_status, start_time, end_time) =>
      request(`/restaurant_administration/restaurants/${restaurantId}/orders/filter/status-and-date?order_status=${encodeURIComponent(order_status)}&start_time=${start_time}&end_time=${end_time}`),
  },
};

