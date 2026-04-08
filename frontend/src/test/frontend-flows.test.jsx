import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../state/AuthContext";
import LoginPage from "../pages/LoginPage";
import RestaurantsPage from "../pages/RestaurantsPage";
import OrdersPage from "../pages/OrdersPage";

function wrap(ui) {
  return render(
    <MemoryRouter>
      <AuthProvider>{ui}</AuthProvider>
    </MemoryRouter>
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
    wrap(<RestaurantsPage />);
    expect(screen.getByText(/Loading restaurants/i)).toBeInTheDocument();
    await screen.findByText(/Restaurant 7/i);
  });

  it("handles empty restaurant state", async () => {
    fetch.mockResolvedValueOnce({ ok: true, json: async () => [] });
    wrap(<RestaurantsPage />);
    await screen.findByText(/No restaurants returned/i);
  });

  it("handles restaurant API failure", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ detail: "Boom" }),
    });
    wrap(<RestaurantsPage />);
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
    wrap(<LoginPage />);
    fireEvent.change(screen.getByPlaceholderText("Username"), { target: { value: "demo" } });
    fireEvent.change(screen.getByPlaceholderText("Password"), { target: { value: "secret" } });
    fireEvent.click(screen.getByText("Sign in"));
    expect(screen.getByRole("button", { name: /Signing in/i })).toBeDisabled();
    releaseLogin();
    await waitFor(() => expect(fetch).toHaveBeenCalled());
  });

  it("shows unauthorized error from order endpoint", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Not authenticated" }),
    });
    wrap(<OrdersPage />);
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
    wrap(<OrdersPage />);
    fireEvent.change(screen.getByPlaceholderText("Order ID"), { target: { value: "999999" } });
    fireEvent.click(screen.getByText("Cancel"));
    await screen.findByText("Order not found");
  });
});

