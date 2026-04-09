import React, { createElement } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { CartProvider } from "../state/CartContext";
import { AuthProvider } from "../state/AuthContext";
import { RestaurantWorkspaceProvider } from "../state/RestaurantWorkspaceContext";
import RestaurantsPage from "../pages/RestaurantsPage";
import RestaurantDetailPage from "../pages/RestaurantDetailPage";
import FavouritesPage from "../pages/FavouritesPage";
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
      createElement(
        AuthProvider,
        null,
        createElement(RestaurantWorkspaceProvider, null, createElement(CartProvider, null, ui))
      )
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

  it("lets a signed-in customer favourite and unfavourite restaurants from the browse page", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "demo", role: "customer", id: 1, requires2FA: false })
    );

    fetch.mockImplementation((url, options = {}) => {
      const path = String(url);
      if (path.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "demo" }));
      }
      if (path.includes("/customers/favorites/restaurants/7") && options.method === "POST") {
        return Promise.resolve(
          jsonFetch(true, { customer_id: "demo", restaurant_id: 7, favorite_restaurants: [7], message: "added" })
        );
      }
      if (path.includes("/customers/favorites/restaurants/7") && options.method === "DELETE") {
        return Promise.resolve(
          jsonFetch(true, { customer_id: "demo", restaurant_id: 7, favorite_restaurants: [], message: "removed" })
        );
      }
      if (path.includes("/customers/favorites/restaurants")) {
        return Promise.resolve(jsonFetch(true, { customer_id: "demo", favorite_restaurants: [] }));
      }
      if (path.includes("/restaurants")) {
        return Promise.resolve(jsonFetch(true, [{ restaurant_id: 7, cuisine: "thai", avg_ratings: 4.8 }]));
      }
      return Promise.resolve(jsonFetch(false, { detail: "Not found" }, 404));
    });

    wrapRoutes(createElement(RestaurantsPage));

    const addButton = await screen.findByLabelText(/Add Restaurant 7 to favourite restaurants/i);
    fireEvent.click(addButton);
    expect(await screen.findByLabelText(/Remove Restaurant 7 from favourite restaurants/i)).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText(/Remove Restaurant 7 from favourite restaurants/i));
    expect(await screen.findByLabelText(/Add Restaurant 7 to favourite restaurants/i)).toBeInTheDocument();
  });

  it("hides favourite buttons on the restaurant details page for non-customer users", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "owner-demo", role: "owner", id: 2, requires2FA: false })
    );

    fetch.mockImplementation((url) => {
      const path = String(url);
      if (path.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "owner-demo" }));
      }
      if (path.includes("/restaurants/7/menu")) {
        return Promise.resolve(
          jsonFetch(true, [{ item_name: "Burger", restaurant_id: 7, cost: 9.99, cuisine: "thai" }])
        );
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
    await screen.findByText("Burger");
    expect(screen.queryByRole("button", { name: /Favourite/i })).not.toBeInTheDocument();
    expect(screen.getByText(/Sign in as a customer to save a favourite item here/i)).toBeInTheDocument();
  });

  it("shows item edit and create controls only for the owner viewing their own restaurant", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "owner-demo", role: "owner", id: 2, requires2FA: false })
    );
    localStorage.setItem(
      "frontend-restaurant-workspace-by-user-v1",
      JSON.stringify({
        "owner-demo": { restaurantId: 7, label: "Restaurant 7", cuisine: "thai" },
      })
    );

    fetch.mockImplementation((url, options = {}) => {
      const path = String(url);
      if (path.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "owner-demo" }));
      }
      if (path.includes("/restaurants/7/menu")) {
        return Promise.resolve(
          jsonFetch(true, [{ item_name: "Burger", restaurant_id: 7, cost: 9.99, cuisine: "thai" }])
        );
      }
      if (path.includes("/items/Burger_7") && options.method === "PATCH") {
        return Promise.resolve(
          jsonFetch(true, { item_name: "Big Burger", restaurant_id: 7, cost: 12.5, cuisine: "thai" })
        );
      }
      if (path.endsWith("/items") && options.method === "POST") {
        return Promise.resolve(
          jsonFetch(true, { item_name: "Soup", restaurant_id: 7, cost: 6.25, cuisine: "thai" }, 201)
        );
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

    await screen.findByText("Burger");
    expect(screen.getByRole("button", { name: /Create item/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Edit item/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /Edit item/i }));
    fireEvent.change(screen.getByLabelText(/^Name$/i), { target: { value: "Big Burger" } });
    fireEvent.change(screen.getByLabelText(/^Cost$/i), { target: { value: "12.5" } });
    fireEvent.click(screen.getByRole("button", { name: /Save changes/i }));

    expect(await screen.findByText("Big Burger")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/items/Burger_7",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({
          item_name: "Big Burger",
          cost: 12.5,
          cuisine: "thai",
          dietary: {
            vegan: false,
            vegetarian: false,
            gluten_free: false,
            dairy_free: false,
            nut_free: false,
            halal: false,
            kosher: false,
          },
        }),
      })
    );

    fireEvent.click(screen.getByRole("button", { name: /Create item/i }));
    fireEvent.change(screen.getByLabelText(/^Name$/i), { target: { value: "Soup" } });
    fireEvent.change(screen.getByLabelText(/^Cost$/i), { target: { value: "6.25" } });
    fireEvent.click(screen.getByRole("button", { name: /^Save item$/i }));

    expect(await screen.findByText("Soup")).toBeInTheDocument();
    expect(fetch).toHaveBeenCalledWith(
      "/api/items",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          item_name: "Soup",
          restaurant_id: 7,
          cost: 6.25,
          cuisine: "thai",
          times_ordered: 0,
          avg_rating: 0,
          dietary: {
            vegan: false,
            vegetarian: false,
            gluten_free: false,
            dairy_free: false,
            nut_free: false,
            halal: false,
            kosher: false,
          },
        }),
      })
    );
  });

  it("hides owner item management controls when viewing a different restaurant", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "owner-demo", role: "owner", id: 2, requires2FA: false })
    );
    localStorage.setItem(
      "frontend-restaurant-workspace-by-user-v1",
      JSON.stringify({
        "owner-demo": { restaurantId: 8, label: "Restaurant 8", cuisine: "thai" },
      })
    );

    fetch.mockImplementation((url) => {
      const path = String(url);
      if (path.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "owner-demo" }));
      }
      if (path.includes("/restaurants/7/menu")) {
        return Promise.resolve(
          jsonFetch(true, [{ item_name: "Burger", restaurant_id: 7, cost: 9.99, cuisine: "thai" }])
        );
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

    await screen.findByText("Burger");
    expect(screen.queryByRole("button", { name: /Create item/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /Edit item/i })).not.toBeInTheDocument();
    expect(screen.getByText(/Item editing is only available on your linked restaurant/i)).toBeInTheDocument();
  });

  it("shows all favourite items from restaurants that have a saved favourite", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "demo", role: "customer", id: 1, requires2FA: false })
    );

    fetch.mockImplementation((url) => {
      const path = String(url);
      if (path.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "demo" }));
      }
      if (path.includes("/customers/favorites/restaurants")) {
        return Promise.resolve(jsonFetch(true, { customer_id: "demo", favorite_restaurants: [7, 9] }));
      }
      if (path.includes("/customers/favourites")) {
        return Promise.resolve(jsonFetch(true, ["Burger_7", "Cookie_7", "Soup_9", "Missing_99"]));
      }
      if (path.includes("/items/Burger_7")) {
        return Promise.resolve(jsonFetch(true, { item_name: "Burger", restaurant_id: 7, cost: 9.99, cuisine: "thai" }));
      }
      if (path.includes("/items/Cookie_7")) {
        return Promise.resolve(jsonFetch(true, { item_name: "Cookie", restaurant_id: 7, cost: 2.5, cuisine: "thai" }));
      }
      if (path.includes("/items/Soup_9")) {
        return Promise.resolve(jsonFetch(true, { item_name: "Soup", restaurant_id: 9, cost: 8.25, cuisine: "comfort" }));
      }
      if (path.includes("/items/Missing_99")) {
        return Promise.resolve(jsonFetch(false, { detail: "Not found" }, 404));
      }
      if (path.includes("/restaurants")) {
        return Promise.resolve(
          jsonFetch(true, [
            { restaurant_id: 7, name: "North Noodles", cuisine: "thai" },
            { restaurant_id: 9, name: "South Soup", cuisine: "comfort" },
            { restaurant_id: 12, name: "Empty Cafe", cuisine: "coffee" },
          ])
        );
      }
      return Promise.resolve(jsonFetch(false, { detail: "Not found" }, 404));
    });

    wrapRoutes(
      createElement(
        Routes,
        null,
        createElement(Route, { path: "/favourites", element: createElement(FavouritesPage) })
      ),
      ["/favourites"]
    );

    await screen.findByRole("heading", { name: /^Favourite restaurants$/i });
    expect(screen.getAllByText("North Noodles").length).toBeGreaterThan(0);
    expect(screen.getAllByText("South Soup").length).toBeGreaterThan(0);
    await screen.findByRole("heading", { name: /^Favourite items$/i });
    expect(screen.getByText("Burger")).toBeInTheDocument();
    expect(screen.getByText("Cookie")).toBeInTheDocument();
    expect(screen.getByText("Soup")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /Add to cart/i })).toHaveLength(3);
    expect(screen.queryByText("Missing")).not.toBeInTheDocument();
    expect(screen.queryByText("Empty Cafe")).not.toBeInTheDocument();

    fireEvent.click(screen.getAllByRole("button", { name: /Add to cart/i })[0]);
    expect(screen.getByText(/\$9\.99/)).toBeInTheDocument();
  });
});
