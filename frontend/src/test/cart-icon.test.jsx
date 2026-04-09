import React from "react";
import { createElement } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { CartProvider, useCart } from "../state/CartContext";
import CartIconNav from "../components/CartIconNav";
import { getCartTotalQuantity } from "../utils/cartItemCount";

function wrap(ui) {
  return render(createElement(MemoryRouter, null, createElement(CartProvider, null, ui)));
}

function CartHarness() {
  const { addItem, removeItem, items } = useCart();
  return (
    <>
      <CartIconNav />
      <button type="button" onClick={() => addItem({ item_name: "Burger", restaurant_id: 1, cost: 10 })}>Add line</button>
      <button type="button" onClick={() => addItem({ item_name: "Fries", restaurant_id: 1, cost: 3 })}>Add other</button>
      {items[0] && (
        <button type="button" onClick={() => removeItem(items[0].key)}>
          Remove first
        </button>
      )}
    </>
  );
}

describe("getCartTotalQuantity", () => {
  it("sums line quantities", () => {
    expect(getCartTotalQuantity([{ quantity: 2 }, { quantity: 3 }])).toBe(5);
  });

  it("returns 0 for non-arrays and invalid quantities", () => {
    expect(getCartTotalQuantity(undefined)).toBe(0);
    expect(getCartTotalQuantity(null)).toBe(0);
    expect(getCartTotalQuantity([{ quantity: "x" }, { quantity: -1 }])).toBe(0);
  });
});

describe("CartIconNav", () => {
  it("shows empty cart in accessible name and hides numeric badge", () => {
    wrap(createElement(CartHarness));
    const link = screen.getByRole("link", { name: /shopping cart, empty/i });
    expect(link).toBeInTheDocument();
    expect(link.querySelector(".cart-icon-nav__badge")).toBeNull();
  });

  it("shows total quantity in badge and updates when items change", () => {
    wrap(createElement(CartHarness));
    const link = screen.getByRole("link", { name: /shopping cart/i });

    fireEvent.click(screen.getByText("Add line"));
    expect(link).toHaveAttribute("aria-label", expect.stringContaining("1 items"));
    expect(link.querySelector(".cart-icon-nav__badge")).toHaveTextContent("1");

    fireEvent.click(screen.getByText("Add line"));
    expect(link.querySelector(".cart-icon-nav__badge")).toHaveTextContent("2");

    fireEvent.click(screen.getByText("Add other"));
    expect(link.querySelector(".cart-icon-nav__badge")).toHaveTextContent("3");

    fireEvent.click(screen.getByText("Remove first"));
    expect(link.querySelector(".cart-icon-nav__badge")).toHaveTextContent("1");
  });

  it("does not crash without CartProvider and still renders a link", () => {
    render(
      createElement(MemoryRouter, null, createElement(CartIconNav))
    );
    const link = screen.getByRole("link", { name: /shopping cart, empty/i });
    expect(link).toBeInTheDocument();
    expect(link.querySelector(".cart-icon-nav__badge")).toBeNull();
  });

  it("navigates to /orders by default", () => {
    wrap(createElement(CartIconNav));
    expect(screen.getByRole("link", { name: /shopping cart/i })).toHaveAttribute("href", "/orders");
  });
});
