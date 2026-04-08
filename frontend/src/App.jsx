import { NavLink, Navigate, Route, Routes } from 'react-router-dom';
import RequireAuth from './components/RequireAuth';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import RestaurantsPage from './pages/RestaurantsPage';
import OrderPage from './pages/OrderPage';
import OrderStatusPage from './pages/OrderStatusPage';
import FavoritesPage from './pages/FavoritesPage';
import TrackingPage from './pages/TrackingPage';
import ReviewsPage from './pages/ReviewsPage';
import { useAuth } from './state/AuthContext';

function AppShell() {
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <div className="app-shell">
      <header>
        <h1>Food Delivery</h1>
        <nav>
          {!isAuthenticated && (
            <>
              <NavLink to="/login">Login</NavLink>
              <NavLink to="/register">Register</NavLink>
            </>
          )}
          {isAuthenticated && (
            <>
              <NavLink to="/restaurants">Restaurants</NavLink>
              <NavLink to="/favorites">Favorites</NavLink>
              <NavLink to="/tracking">Tracking</NavLink>
              <NavLink to="/reviews">Reviews</NavLink>
              <button className="link-button" onClick={logout} type="button">
                Logout
              </button>
            </>
          )}
        </nav>
        {isAuthenticated && (
          <p className="auth-label">Logged in as user #{user?.id}</p>
        )}
      </header>
      <main>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/restaurants"
            element={
              <RequireAuth>
                <RestaurantsPage />
              </RequireAuth>
            }
          />
          <Route
            path="/restaurants/:restaurantId/order"
            element={
              <RequireAuth>
                <OrderPage />
              </RequireAuth>
            }
          />
          <Route
            path="/orders/:orderId"
            element={
              <RequireAuth>
                <OrderStatusPage />
              </RequireAuth>
            }
          />
          <Route
            path="/favorites"
            element={
              <RequireAuth>
                <FavoritesPage />
              </RequireAuth>
            }
          />
          <Route
            path="/tracking"
            element={
              <RequireAuth>
                <TrackingPage />
              </RequireAuth>
            }
          />
          <Route
            path="/reviews"
            element={
              <RequireAuth>
                <ReviewsPage />
              </RequireAuth>
            }
          />
          <Route
            path="*"
            element={
              <Navigate to={isAuthenticated ? '/restaurants' : '/login'} replace />
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return <AppShell />;
}
