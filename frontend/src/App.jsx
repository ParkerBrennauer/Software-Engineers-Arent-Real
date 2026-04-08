import React from "react";
import { Link, Route, Routes } from "react-router-dom";
import { useAuth } from "./state/AuthContext";
import RequireAuth from "./components/RequireAuth";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import RestaurantsPage from "./pages/RestaurantsPage";
import OrdersPage from "./pages/OrdersPage";
import ReviewsPage from "./pages/ReviewsPage";
import OperationsPage from "./pages/OperationsPage";
import ProfilePage from "./pages/ProfilePage";

function HomePage() {
  return (
    <section className="card hero">
      <h1>FoodHub Control Center</h1>
      <p>
        Unified frontend mapped directly to the available FastAPI backend routes for
        customers, restaurant teams, and drivers.
      </p>
      <div className="grid cards">
        <article className="panel">
          <h3>Customer</h3>
          <p>Browse restaurants, build cart, place and track orders, leave reviews.</p>
        </article>
        <article className="panel">
          <h3>Driver</h3>
          <p>View assigned orders, pickup actions, delay reporting, tip payout.</p>
        </article>
        <article className="panel">
          <h3>Owner / Staff</h3>
          <p>View restaurant orders, filter by date/status, assign staff and manage discounts.</p>
        </article>
      </div>
    </section>
  );
}

function Nav() {
  const { user, logout } = useAuth();
  return (
    <header className="topbar">
      <div className="brand">SEAR Delivery</div>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/restaurants">Restaurants</Link>
        <Link to="/orders">Orders</Link>
        <Link to="/reviews">Reviews</Link>
        <Link to="/operations">Operations</Link>
        <Link to="/profile">Profile</Link>
      </nav>
      <div className="auth-chip">
        {user ? (
          <>
            <span>{user.username} ({user.role})</span>
            <button onClick={logout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </header>
  );
}

export default function App() {
  return (
    <main className="app-shell">
      <Nav />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/restaurants" element={<RestaurantsPage />} />
        <Route path="/orders" element={<RequireAuth><OrdersPage /></RequireAuth>} />
        <Route path="/reviews" element={<ReviewsPage />} />
        <Route path="/operations" element={<RequireAuth><OperationsPage /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
      </Routes>
    </main>
  );
}

