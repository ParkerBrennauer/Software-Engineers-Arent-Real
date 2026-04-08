# Endpoint to UI Map

- `users/*` -> `src/pages/LoginPage.jsx`, `src/pages/RegisterPage.jsx`, `src/pages/ProfilePage.jsx`
- `customers/*` -> `src/pages/ProfilePage.jsx` (profile/favourites-ready service usage), extensible via `api.customer`
- `restaurants/*` -> `src/pages/RestaurantsPage.jsx`
- `items/*` -> `src/api/client.js` (ready for menu management controls)
- `orders/*` and tracking/tip -> `src/pages/OrdersPage.jsx`
- rating/review/report endpoints under `/orders/*` -> `src/pages/ReviewsPage.jsx`
- `discounts/*` -> `src/pages/OperationsPage.jsx`
- `restaurant_administration/*` -> `src/pages/OperationsPage.jsx`

## Notes
- Frontend includes centralized endpoint wiring for all available router domains in `src/api/client.js`.
- Where backend contracts are unstable, UI degrades to explicit error panels instead of silent failures.

