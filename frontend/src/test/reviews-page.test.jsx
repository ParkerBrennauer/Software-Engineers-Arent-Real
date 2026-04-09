import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../state/AuthContext";
import { CartProvider } from "../state/CartContext";
import ReviewsPage from "../pages/ReviewsPage";

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrapReviews() {
  return render(
    createElement(
      MemoryRouter,
      null,
      createElement(AuthProvider, null, createElement(CartProvider, null, createElement(ReviewsPage)))
    )
  );
}

describe("ReviewsPage order selection", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
  });

  it("loads the signed-in customer's orders and allows selecting one to rate", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "demo", role: "customer", id: 1, requires2FA: false })
    );

    fetch.mockImplementation((url, options = {}) => {
      const path = String(url);
      if (path.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "demo" }));
      }
      if (path.includes("/customers/order-history") && options.method === "PATCH") {
        return Promise.resolve(
          jsonFetch(true, [
            { id: 11, restaurant: "Restaurant_16", order_status: "delivered" },
            { id: 12, restaurant: "Restaurant_9", order_status: "picked_up" },
          ])
        );
      }
      if (path.includes("/orders/11/rating")) {
        return Promise.resolve(jsonFetch(true, { order_id: "11", submitted_stars: 5 }));
      }
      return Promise.resolve(jsonFetch(true, {}));
    });

    wrapReviews();

    await screen.findByText(/Order #11/i);
    expect(screen.getByText(/Order #12/i)).toBeInTheDocument();

    fireEvent.click(screen.getAllByRole("button", { name: /Select order/i })[0]);
    expect(await screen.findByText(/Selected order #11/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue("16")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Submit rating/i }));
    await waitFor(() =>
      expect(fetch).toHaveBeenCalledWith(
        "/api/orders/11/rating",
        expect.objectContaining({ method: "POST" })
      )
    );
    expect(await screen.findByText(/Rating submitted for order #11/i)).toBeInTheDocument();
    expect(await screen.findByText(/Your rated orders/i)).toBeInTheDocument();
    expect(screen.getByText(/Stars: 5/i)).toBeInTheDocument();
  });
});
