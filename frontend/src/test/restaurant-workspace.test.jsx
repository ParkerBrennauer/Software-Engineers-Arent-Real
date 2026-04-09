import React from "react";
import { createElement } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../state/AuthContext";
import { RestaurantWorkspaceProvider } from "../state/RestaurantWorkspaceContext";
import OwnerVenueBar from "../components/OwnerVenueBar";

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrap(ui) {
  return render(
    createElement(
      MemoryRouter,
      null,
      createElement(AuthProvider, null, createElement(RestaurantWorkspaceProvider, null, ui))
    )
  );
}

describe("Restaurant workspace (owner/staff)", () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = vi.fn();
  });

  it("does not show venue bar for customers", () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "pat", role: "customer", id: 1, requires2FA: false })
    );
    fetch.mockResolvedValue(jsonFetch(true, { username: "pat" }));
    wrap(createElement(OwnerVenueBar));
    expect(screen.queryByTestId("owner-venue-bar")).not.toBeInTheDocument();
  });

  it("shows linked venue for owner when storage exists", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "own1", role: "owner", id: 2, requires2FA: false })
    );
    localStorage.setItem(
      "frontend-restaurant-workspace-by-user-v1",
      JSON.stringify({
        own1: { restaurantId: 5, label: "Restaurant 5 · thai", cuisine: "thai" },
      })
    );
    fetch.mockResolvedValue(jsonFetch(true, { username: "own1" }));
    wrap(createElement(OwnerVenueBar));
    await waitFor(() => expect(screen.getByText(/Current venue:/i)).toBeInTheDocument());
    expect(screen.getByText(/Restaurant 5 · thai/i)).toBeInTheDocument();
  });

  it("lets owner pick a venue from the list and persists it", async () => {
    const user = userEvent.setup();
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "own2", role: "owner", id: 3, requires2FA: false })
    );
    fetch.mockImplementation((url) => {
      const u = String(url);
      if (u.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "own2" }));
      }
      if (u.includes("/restaurant_administration/restaurants/") && u.includes("/orders")) {
        return Promise.resolve(
          jsonFetch(false, { detail: "User does not have permission to view this restaurant's orders" }, 403)
        );
      }
      if (u.includes("/restaurants") && !u.includes("/restaurants/")) {
        return Promise.resolve(jsonFetch(true, [{ restaurant_id: 8, cuisine: "pizza", avg_ratings: 4.5 }]));
      }
      return Promise.resolve(jsonFetch(true, {}));
    });
    wrap(createElement(OwnerVenueBar));
    await screen.findByRole("dialog");
    expect(screen.getByText(/Which venue do you manage/i)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: /Restaurant 8 · pizza/i }));
    await waitFor(() => expect(screen.getByText(/Current venue:/i)).toBeInTheDocument());
    const stored = JSON.parse(localStorage.getItem("frontend-restaurant-workspace-by-user-v1"));
    expect(stored.own2.restaurantId).toBe(8);
  });

  it("auto-links owner when administration orders allows their venue", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "own3", role: "owner", id: 4, requires2FA: false })
    );
    fetch.mockImplementation((url) => {
      const u = String(url);
      if (u.includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "own3" }));
      }
      if (u.includes("/restaurant_administration/restaurants/12/orders")) {
        return Promise.resolve(jsonFetch(true, []));
      }
      if (u.includes("/restaurant_administration/restaurants/") && u.includes("/orders")) {
        return Promise.resolve(
          jsonFetch(false, { detail: "User does not have permission to view this restaurant's orders" }, 403)
        );
      }
      if (u.includes("/restaurants") && !u.includes("/restaurants/")) {
        return Promise.resolve(jsonFetch(true, [{ restaurant_id: 12, cuisine: "Thai", avg_ratings: 4.2 }]));
      }
      return Promise.resolve(jsonFetch(true, {}));
    });
    wrap(createElement(OwnerVenueBar));
    await waitFor(() => expect(screen.getByText(/Current venue:/i)).toBeInTheDocument());
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    const stored = JSON.parse(localStorage.getItem("frontend-restaurant-workspace-by-user-v1"));
    expect(stored.own3.restaurantId).toBe(12);
  });
});
