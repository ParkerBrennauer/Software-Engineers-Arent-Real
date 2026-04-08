import React from "react";
import { render, screen } from "@testing-library/react";
import { createElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../state/AuthContext";
import { CartProvider } from "../state/CartContext";
import OrdersPage from "../pages/OrdersPage";

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrapOrders() {
  return render(
    createElement(
      MemoryRouter,
      null,
      createElement(AuthProvider, null, createElement(CartProvider, null, createElement(OrdersPage)))
    )
  );
}

function primeSession(user) {
  localStorage.setItem("frontend-auth-user", JSON.stringify(user));
  global.fetch = vi.fn((url) => {
    if (String(url).includes("/users/current-user")) {
      return Promise.resolve(jsonFetch(true, { username: user.username }));
    }
    return Promise.resolve(jsonFetch(true, {}));
  });
}

describe("OrdersPage role-based UI", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("shows only customer actions for customers (and cart)", () => {
    primeSession({ username: "alice", role: "customer", id: 1 });
    wrapOrders();

    expect(screen.getByRole("heading", { name: /^Place an order$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Place order$/i })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /^Cart$/i })).toBeInTheDocument();

    expect(screen.queryByRole("button", { name: /^Mark ready$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Confirm pickup$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Load my orders/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Assign driver$/i })).not.toBeInTheDocument();
  });

  it("shows only driver actions for drivers and hides the cart panel", () => {
    primeSession({ username: "driver_bob", role: "driver", id: 2 });
    wrapOrders();

    expect(screen.getByRole("heading", { name: /^Deliveries$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Confirm pickup$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Load my orders/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Report delay/i })).toBeInTheDocument();

    expect(screen.queryByRole("button", { name: /^Place order$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /^Cart$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Mark ready$/i })).not.toBeInTheDocument();
  });

  it("shows owner operational controls and restaurant queue", () => {
    primeSession({ username: "owner_carol", role: "owner", id: 3 });
    wrapOrders();

    expect(screen.getByRole("heading", { name: /Kitchen & dispatch/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Mark ready$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Assign driver$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Load orders$/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Advanced filters/i })).toBeInTheDocument();

    expect(screen.queryByRole("button", { name: /^Place order$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /^Cart$/i })).not.toBeInTheDocument();
  });

  it("shows staff kitchen and queue controls but not assign driver", () => {
    primeSession({ username: "staff_dan", role: "staff", id: 4 });
    wrapOrders();

    expect(screen.getByRole("heading", { name: /^Kitchen$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Mark ready$/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^Load orders$/i })).toBeInTheDocument();

    expect(screen.queryByRole("button", { name: /^Assign driver$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Place order$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Confirm pickup$/i })).not.toBeInTheDocument();
  });

  it("hides all role actions when role is unknown or missing (fail-safe)", () => {
    primeSession({ username: "weird", role: "admin", id: 9 });
    wrapOrders();

    expect(screen.getByText(/verify your account type/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Place order$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Confirm pickup$/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Mark ready$/i })).not.toBeInTheDocument();
  });

  it("hides actions when cached user has no role field", () => {
    primeSession({ username: "norole", id: 10 });
    wrapOrders();
    expect(screen.getByText(/verify your account type/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^Confirm pickup$/i })).not.toBeInTheDocument();
  });
});
