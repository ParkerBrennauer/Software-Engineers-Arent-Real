import React from "react";
import { Link, Route, Routes } from "react-router-dom";
import { useAuth } from "./state/AuthContext";
import RequireAuth from "./components/RequireAuth";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import RestaurantsPage from "./pages/RestaurantsPage";
import RestaurantDetailPage from "./pages/RestaurantDetailPage";
import OrdersPage from "./pages/OrdersPage";
import ReviewsPage from "./pages/ReviewsPage";
import OperationsPage from "./pages/OperationsPage";
import ProfilePage from "./pages/ProfilePage";
import DiscountsPage from "./pages/DiscountsPage";
import FavouritesPage from "./pages/FavouritesPage";
import CartIconNav from "./components/CartIconNav";
import OwnerVenueBar from "./components/OwnerVenueBar";

function HomePage() {
  return (
    <section className="card hero">
      <h1 className="hero-title">Order food you love</h1>
      <p className="hero-lede">
        Discover local restaurants, customize your meal, and track delivery—all in one place.
      </p>
      <div className="grid cards hero-cards">
        <article className="panel hero-card">
          <h2 className="hero-card__title">Hungry?</h2>
          <p>Browse menus, save favorites, and check out when you&apos;re ready.</p>
        </article>
        <article className="panel hero-card">
          <h2 className="hero-card__title">On the road?</h2>
          <p>Drivers can pick up, navigate, and stay on top of every run.</p>
        </article>
        <article className="panel hero-card">
          <h2 className="hero-card__title">Running a kitchen?</h2>
          <p>Owners and staff get the tools to keep service smooth behind the scenes.</p>
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
        <Link to="/favourites">Favourites</Link>
        <Link to="/reviews">Reviews</Link>
        <Link to="/operations">Business</Link>
        <Link to="/discounts">Promos</Link>
        <Link to="/profile">Profile</Link>
      </nav>
      <div className="auth-chip">
        <CartIconNav />
        {user ? (
          <>
            <span className="nav-user-name">{user.username}</span>
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
      <OwnerVenueBar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/restaurants" element={<RestaurantsPage />} />
        <Route path="/restaurants/:restaurantId" element={<RestaurantDetailPage />} />
        <Route path="/orders" element={<RequireAuth><OrdersPage /></RequireAuth>} />
        <Route path="/favourites" element={<RequireAuth><FavouritesPage /></RequireAuth>} />
        <Route path="/reviews" element={<ReviewsPage />} />
        <Route path="/operations" element={<RequireAuth><OperationsPage /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route path="/discounts" element={<DiscountsPage />} />
      </Routes>
    </main>
  );
}
