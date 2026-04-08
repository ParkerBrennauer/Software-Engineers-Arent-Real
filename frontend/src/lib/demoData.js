export const DEFAULT_DEMO_CUSTOMER_ID = '9c6dbfcb-72c5-4cc4-9f76-29200f0efda7';
export const DEFAULT_DEMO_TRACKING_ORDER_ID = '1';
export const DEFAULT_DEMO_RESTAURANT_ID = '16';

const DEMO_CUSTOMER_STORAGE_KEY = 'food-delivery-demo-customer-id';

export const DEMO_COMPLETED_ORDERS = [
  {
    customerId: '9c6dbfcb-72c5-4cc4-9f76-29200f0efda7',
    orderId: '1d8e87M',
    restaurantId: 16,
  },
  {
    customerId: 'b3e207bd-103e-4154-b7cc-7e32bd898ee3',
    orderId: 'f4d84dC',
    restaurantId: 30,
  },
  {
    customerId: '4a96f5b2-04c4-428d-a1cd-3015ff43698a',
    orderId: '5a6006W',
    restaurantId: 53,
  },
];

export function loadPreferredCustomerId(fallbackUsername) {
  try {
    const storedId = window.localStorage.getItem(DEMO_CUSTOMER_STORAGE_KEY);
    return fallbackUsername || storedId || DEFAULT_DEMO_CUSTOMER_ID;
  } catch {
    return fallbackUsername || DEFAULT_DEMO_CUSTOMER_ID;
  }
}

export function savePreferredCustomerId(customerId) {
  try {
    window.localStorage.setItem(DEMO_CUSTOMER_STORAGE_KEY, customerId);
  } catch {
    // Ignore storage errors and keep the current in-memory selection.
  }
}

export function getDemoOrdersForCustomer(customerId) {
  const matches = DEMO_COMPLETED_ORDERS.filter(
    (entry) => entry.customerId === customerId,
  );
  return matches.length > 0 ? matches : DEMO_COMPLETED_ORDERS;
}
