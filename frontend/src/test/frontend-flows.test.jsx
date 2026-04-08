import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../state/AuthContext";
import { CartProvider } from "../state/CartContext";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import RestaurantsPage from "../pages/RestaurantsPage";
import OrdersPage from "../pages/OrdersPage";
import ProfilePage from "../pages/ProfilePage";
import { useCart } from "../state/CartContext";

function wrap(ui) {
  return render(
    createElement(
      MemoryRouter,
      null,
      createElement(AuthProvider, null, createElement(CartProvider, null, ui))
    )
  );
}

describe("frontend endpoint flows", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
  });

  it("shows loading and renders restaurant results", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [{ restaurant_id: 7, cuisine: "thai", avg_ratings: 4.8 }],
    });
    wrap(createElement(RestaurantsPage));
    expect(screen.getByText(/Loading restaurants/i)).toBeInTheDocument();
    await screen.findByText(/Restaurant 7/i);
  });

  it("handles empty restaurant state", async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    wrap(createElement(RestaurantsPage));
    await screen.findByText(/No restaurants returned/i);
  });

  it("handles restaurant API failure", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: "Boom" }),
    });
    wrap(createElement(RestaurantsPage));
    await screen.findByText("Boom");
  });

  it("prevents duplicate login submit while loading", async () => {
    let releaseLogin;
    fetch.mockImplementation((url) => {
      if (String(url).includes("/users/login")) {
        return new Promise((resolve) => {
          releaseLogin = () => resolve({ ok: true, json: async () => ({ id: 10, requires_2fa: false }) });
        });
      }
      if (String(url).includes("/users/current-user")) {
        return Promise.resolve({ ok: true, json: async () => ({ username: "demo" }) });
      }
      return Promise.resolve({ ok: true, json: async () => ({}) });
    });
    wrap(createElement(LoginPage));
    fireEvent.change(screen.getByPlaceholderText("Username"), { target: { value: "demo" } });
    fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: "secret" } });
    fireEvent.click(screen.getByText("Sign in"));
    expect(screen.getByRole("button", { name: /Signing in/i })).toBeDisabled();
    releaseLogin();
    await waitFor(() => expect(fetch).toHaveBeenCalled());
  });

  it("requires valid 2FA code before verify submit", async () => {
    fetch.mockImplementation((url) => {
      if (String(url).includes("/users/login")) {
        return Promise.resolve({ ok: true, json: async () => ({ id: 10, requires_2fa: true }) });
      }
      if (String(url).includes("/users/current-user")) {
        return Promise.resolve({ ok: true, json: async () => ({ username: "driver_demo" }) });
      }
      if (String(url).includes("/users/2fa/generate")) {
        return Promise.resolve({ ok: true, json: async () => ({ message: "generated" }) });
      }
      return Promise.resolve({ ok: true, json: async () => ({}) });
    });
    wrap(createElement(LoginPage));
    fireEvent.change(screen.getByPlaceholderText("Username"), { target: { value: "driver_demo" } });
    fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: "secret" } });
    fireEvent.click(screen.getByText("Sign in"));
    await screen.findByText(/Two-factor verification/i);
    expect(screen.getByRole("button", { name: "Verify 2FA" })).toBeDisabled();
    fireEvent.change(screen.getByPlaceholderText("6-digit code"), { target: { value: "123456" } });
    expect(screen.getByRole("button", { name: "Verify 2FA" })).not.toBeDisabled();
  });

  it("shows unauthorized error from order endpoint", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Not authenticated" }),
    });
    wrap(createElement(OrdersPage));
    fireEvent.change(screen.getByPlaceholderText("Order ID"), { target: { value: "1" } });
    fireEvent.click(screen.getByText("Load order"));
    await screen.findByText("Not authenticated");
  });

  it("handles invalid input on review endpoint access via orders controls", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Order not found" }),
    });
    wrap(createElement(OrdersPage));
    fireEvent.change(screen.getByPlaceholderText("Order ID"), { target: { value: "999999" } });
    fireEvent.click(screen.getByText("Cancel"));
    await screen.findByText("Order not found");
  });

  it("blocks customer signup with invalid card number before API call", async () => {
    wrap(createElement(RegisterPage));
    fireEvent.change(screen.getByPlaceholderText("Email"), { target: { value: "a@a.com" } });
    fireEvent.change(screen.getByPlaceholderText("Name"), { target: { value: "A" } });
    fireEvent.change(screen.getByPlaceholderText("Username"), { target: { value: "aa" } });
    fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: "pass123" } });
    fireEvent.change(screen.getByPlaceholderText("Card number (15-16 digits)"), { target: { value: "123" } });
    fireEvent.click(screen.getByRole("button", { name: "Create account" }));
    expect(await screen.findByText("Card number must be 15 or 16 digits.")).toBeInTheDocument();
    expect(fetch).not.toHaveBeenCalled();
  });

  it("disables empty address save on profile page", async () => {
    fetch
      .mockResolvedValueOnce({ ok: true, json: async () => ({ username: "demo" }) })
      .mockResolvedValueOnce({ ok: true, json: async () => [] });
    wrap(createElement(ProfilePage));
    await waitFor(() => expect(fetch).toHaveBeenCalled());
    expect(screen.getByRole("button", { name: "Save address" })).toBeDisabled();
  });

  it("prevents adding items from different restaurants to cart", () => {
    function Harness() {
      const { addItem, items } = useCart();
      return (
        <>
          <button onClick={() => addItem({ item_name: "Burger", restaurant_id: 1, cost: 10 })}>Add one</button>
          <button onClick={() => addItem({ item_name: "Pasta", restaurant_id: 2, cost: 12 })}>Add two</button>
          <p>Count:{items.length}</p>
        </>
      );
    }
    wrap(createElement(Harness));
    fireEvent.click(screen.getByText("Add one"));
    fireEvent.click(screen.getByText("Add two"));
    expect(screen.getByText("Count:1")).toBeInTheDocument();
  });
});

