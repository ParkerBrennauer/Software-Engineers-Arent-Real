import React from "react";
import { Link } from "react-router-dom";
import { useCartOptional } from "../state/CartContext";
import { getCartTotalQuantity } from "../utils/cartItemCount";

/**
 * Header cart control: bag icon + live total quantity badge (hidden when empty).
 * Navigates to /orders where the cart panel lives for checkout.
 */
export default function CartIconNav({ to = "/orders", className = "" }) {
  const cart = useCartOptional();
  const items = Array.isArray(cart?.items) ? cart.items : [];
  const count = getCartTotalQuantity(items);
  const label =
    count === 0 ? "Shopping cart, empty. Go to orders to review or place an order." : `Shopping cart, ${count} items`;

  const badge = count > 99 ? "99+" : String(count);

  return (
    <Link
      to={to}
      className={`cart-icon-nav ${className}`.trim()}
      aria-label={label}
      title={count === 0 ? "Cart (empty)" : `Cart (${count} items)`}
    >
      <span className="cart-icon-nav__svg" aria-hidden="true">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.85" strokeLinecap="round" strokeLinejoin="round">
          <path d="M6 6h15l-1.5 9h-12z" />
          <path d="M6 6 5 3H2" />
          <circle cx="9.5" cy="20" r="1.75" />
          <circle cx="17.5" cy="20" r="1.75" />
        </svg>
      </span>
      {count > 0 && (
        <span className="cart-icon-nav__badge" aria-hidden="true">
          {badge}
        </span>
      )}
    </Link>
  );
}
