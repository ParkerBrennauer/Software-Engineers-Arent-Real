import React, { createElement } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { CartProvider } from "../state/CartContext";
import { AuthProvider } from "../state/AuthContext";
import RestaurantsPage from "../pages/RestaurantsPage";
import RestaurantDetailPage from "../pages/RestaurantDetailPage";
import { normalizeApiArray } from "../utils/normalizeApiArray";
import { dietaryTags } from "../utils/formatItemDietary";

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrapRoutes(ui, initialEntries = ["/restaurants"]) {
  return render(
    createElement(
      MemoryRouter,
      { initialEntries },
      createElement(AuthProvider, null, createElement(CartProvider, null, ui))
    )
  );
}

describe("normalizeApiArray & dietaryTags", () => {
  it("normalizes object or array", () => {
    expect(normalizeApiArray([1, 2])).toEqual([1, 2]);
    expect(normalizeApiArray({ a: 1, b: 2 })).toEqual([1, 2]);
    expect(normalizeApiArray(null)).toEqual([]);
  });

  it("lists true dietary flags", () => {
    expect(dietaryTags({ vegan: true, vegetarian: false })).toEqual(["vegan"]);
  });
});

describe("Restaurant browsing navigation", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
  });

  it("navigates from list to dedicated restaurant page and shows menu (no inline menu section on list)", async () => {
    fetch
      .mockResolvedValueOnce(jsonFetch(true, [{ restaurant_id: 7, cuisine: "thai", avg_ratings: 4.8 }]))
      .mockResolvedValueOnce(
        jsonFetch(true, [
          {
            item_name: "Taccos",
            restaurant_id: 7,
            cost: 1.5,
            cuisine: "thai",
            dietary: { vegan: true },
          },
          { item_name: "Cookie", restaurant_id: 7, cost: 2.17, cuisine: "thai" },
        ])
      );

    wrapRoutes(
      createElement(
        Routes,
        null,
        createElement(Route, { path: "/restaurants", element: createElement(RestaurantsPage) }),
        createElement(Route, { path: "/restaurants/:restaurantId", element: createElement(RestaurantDetailPage) })
      )
    );

    await screen.findByText(/Restaurant 7/i);
    expect(screen.queryByRole("heading", { name: /^Menu$/i })).not.toBeInTheDocument();
    expect(screen.queryByText(/Menu for Restaurant/i)).not.toBeInTheDocument();

    fireEvent.click(screen.getByText("View menu"));

    await screen.findByRole("heading", { name: /^Menu$/i });
    expect(await screen.findByText("Taccos")).toBeInTheDocument();
    expect(screen.getByText("Cookie")).toBeInTheDocument();
    expect(screen.getByText(/vegan/i)).toBeInTheDocument();
    expect(fetch).toHaveBeenCalled();
  });

  it("add to cart from detail page updates cart affordance", async () => {
    fetch
      .mockResolvedValueOnce(jsonFetch(true, [{ restaurant_id: 7, cuisine: "thai", avg_ratings: 4.8 }]))
      .mockResolvedValueOnce(
        jsonFetch(true, [{ item_name: "Burger", restaurant_id: 7, cost: 9.99, cuisine: "thai" }])
      );

    wrapRoutes(
      createElement(
        Routes,
        null,
        createElement(Route, { path: "/restaurants", element: createElement(RestaurantsPage) }),
        createElement(Route, { path: "/restaurants/:restaurantId", element: createElement(RestaurantDetailPage) })
      )
    );

    await screen.findByText(/Restaurant 7/i);
    fireEvent.click(screen.getByText("View menu"));
    await screen.findByText("Burger");
    fireEvent.click(screen.getByRole("button", { name: /Add to cart/i }));
    await waitFor(() => {
      expect(screen.getByRole("heading", { name: /^Cart$/i })).toBeInTheDocument();
    });
    expect(screen.getAllByText(/Burger/i).length).toBeGreaterThan(0);
  });

  it("shows safe fallback for invalid restaurant id param", () => {
    wrapRoutes(
      createElement(
        Routes,
        null,
        createElement(Route, { path: "/restaurants/:restaurantId", element: createElement(RestaurantDetailPage) })
      ),
      ["/restaurants/not-a-number"]
    );
    expect(screen.getByText(/not valid/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Back to restaurants/i })).toHaveAttribute("href", "/restaurants");
  });

  it("renders detail with sparse menu data without crashing", async () => {
    fetch.mockResolvedValueOnce(jsonFetch(true, [{}]));

    wrapRoutes(
      createElement(
        Routes,
        null,
        createElement(Route, { path: "/restaurants/:restaurantId", element: createElement(RestaurantDetailPage) })
      ),
      [{ pathname: "/restaurants/7", state: { restaurant: { restaurant_id: 7, cuisine: "thai" } } }]
    );

    await waitFor(() => expect(screen.getByText(/Menu item/i)).toBeInTheDocument());
    expect(screen.getAllByText(/\$0\.00/).length).toBeGreaterThan(0);
  });

  it("shows the restaurant favourite section and toggles a favourite item", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "demo", role: "customer", id: 1, requires2FA: false })
    );

    fetch.mockImplementation((url, options = {}) => {
      const path = String(url);
      if (path.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "demo" }));
      }
      if (path.includes("/restaurants/7/menu")) {
        return Promise.resolve(
          jsonFetch(true, [
            { item_name: "Burger", restaurant_id: 7, cost: 9.99, cuisine: "thai" },
            { item_name: "Cookie", restaurant_id: 7, cost: 2.5, cuisine: "thai" },
          ])
        );
      }
      if (path.includes("/customers/favourites") && (!options.method || options.method === "GET")) {
        return Promise.resolve(jsonFetch(true, ["Burger_7"]));
      }
      if (path.includes("/customers/favourites/Burger_7") && options.method === "PATCH") {
        return Promise.resolve(jsonFetch(true, "removed"));
      }
      if (path.includes("/customers/favourites/Cookie_7") && options.method === "PATCH") {
        return Promise.resolve(jsonFetch(true, "added"));
      }
      return Promise.resolve(jsonFetch(true, [{ restaurant_id: 7, cuisine: "thai", avg_ratings: 4.8 }]));
    });

    wrapRoutes(
      createElement(
        Routes,
        null,
        createElement(Route, { path: "/restaurants/:restaurantId", element: createElement(RestaurantDetailPage) })
      ),
      ["/restaurants/7"]
    );

    await screen.findByRole("heading", { name: /^Favourite$/i });
    expect(await screen.findAllByText("Burger")).not.toHaveLength(0);
    expect(screen.getByRole("button", { name: /Remove favourite/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Remove favourite/i }));
    await screen.findByText(/No favourite item saved for this restaurant yet/i);

    fireEvent.click(screen.getAllByRole("button", { name: /☆ Favourite/i })[1]);
    expect(await screen.findByRole("button", { name: /Remove favourite/i })).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith("/api/customers/favourites/Cookie_7", expect.objectContaining({ method: "PATCH" }));
  });
});
