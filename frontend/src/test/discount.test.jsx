import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { createElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../state/AuthContext";
import { CartProvider } from "../state/CartContext";
import CartPanel from "../components/CartPanel";
import DiscountsPage from "../pages/DiscountsPage";
import RestaurantsPage from "../pages/RestaurantsPage";
import { useCart } from "../state/CartContext";

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrap(ui, { route = "/" } = {}) {
  return render(
    createElement(
      MemoryRouter,
      { initialEntries: [route] },
      createElement(AuthProvider, null, createElement(CartProvider, null, ui))
    )
  );
}

describe("discount feature", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
  });

  it("applies discount and shows savings in cart", async () => {
    fetch.mockImplementation((url) => {
      if (String(url).includes("/discounts/apply")) {
        return Promise.resolve(jsonFetch(true, { discounted_total: 9 }));
      }
      return Promise.resolve(jsonFetch(true, {}));
    });
    function Harness() {
      const { addItem } = useCart();
      return (
        <>
          <button type="button" onClick={() => addItem({ item_name: "Burger", restaurant_id: 1, cost: 10, cuisine: "x" })}>
            Add
          </button>
          <CartPanel />
        </>
      );
    }
    wrap(createElement(Harness));
    fireEvent.click(screen.getByText("Add"));
    fireEvent.change(screen.getByLabelText("Promo code"), { target: { value: "SAVE" } });
    fireEvent.click(screen.getByRole("button", { name: "Apply" }));
    await waitFor(() => expect(screen.getByText(/Applied:/i)).toBeInTheDocument());
    expect(screen.getByText(/Total: \$9\.00/)).toBeInTheDocument();
  });

  it("shows API error when discount code is invalid", async () => {
    fetch.mockResolvedValue(jsonFetch(false, { detail: "Discount not found" }, 404));
    function Harness() {
      const { addItem } = useCart();
      return (
        <>
          <button type="button" onClick={() => addItem({ item_name: "Burger", restaurant_id: 1, cost: 10, cuisine: "x" })}>
            Add
          </button>
          <CartPanel />
        </>
      );
    }
    wrap(createElement(Harness));
    fireEvent.click(screen.getByText("Add"));
    fireEvent.change(screen.getByLabelText("Promo code"), { target: { value: "BAD" } });
    fireEvent.click(screen.getByRole("button", { name: "Apply" }));
    await screen.findByText("Discount not found");
  });

  it("disables apply while request is in flight", async () => {
    let resolveApply;
    fetch.mockImplementation((url) => {
      if (String(url).includes("/discounts/apply")) {
        return new Promise((resolve) => {
          resolveApply = () => resolve(jsonFetch(true, { discounted_total: 5 }));
        });
      }
      return Promise.resolve(jsonFetch(true, {}));
    });
    function Harness() {
      const { addItem } = useCart();
      return (
        <>
          <button type="button" onClick={() => addItem({ item_name: "Burger", restaurant_id: 1, cost: 10, cuisine: "x" })}>
            Add
          </button>
          <CartPanel />
        </>
      );
    }
    wrap(createElement(Harness));
    fireEvent.click(screen.getByText("Add"));
    fireEvent.change(screen.getByLabelText("Promo code"), { target: { value: "SAVE" } });
    fireEvent.click(screen.getByRole("button", { name: "Apply" }));
    expect(screen.getByRole("button", { name: /Applying/i })).toBeDisabled();
    resolveApply();
    await waitFor(() => expect(screen.getByRole("button", { name: "Apply" })).not.toBeDisabled());
  });

  it("recalculates discount when cart total changes", async () => {
    let applyCalls = 0;
    fetch.mockImplementation((url) => {
      if (String(url).includes("/discounts/apply")) {
        applyCalls += 1;
        const orderTotal = applyCalls === 1 ? 13.3 : 24.6;
        return Promise.resolve(jsonFetch(true, { discounted_total: orderTotal * 0.9 }));
      }
      return Promise.resolve(jsonFetch(true, {}));
    });
    function Harness() {
      const { addItem } = useCart();
      return (
        <>
          <button type="button" onClick={() => addItem({ item_name: "Burger", restaurant_id: 1, cost: 10, cuisine: "x" })}>
            Add
          </button>
          <CartPanel />
        </>
      );
    }
    wrap(createElement(Harness));
    fireEvent.click(screen.getByText("Add"));
    fireEvent.change(screen.getByLabelText("Promo code"), { target: { value: "SAVE" } });
    fireEvent.click(screen.getByRole("button", { name: "Apply" }));
    await waitFor(() => expect(screen.getByText(/Total: \$11\.97/)).toBeInTheDocument());
    fireEvent.click(screen.getByText("Add"));
    await waitFor(() => expect(screen.getByText(/Total: \$22\.14/)).toBeInTheDocument());
  });

  it("renders owner discount management when user is owner", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "cafe_owner" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "cafe_owner", role: "owner", id: 1, requires2FA: false })
    );
    wrap(createElement(DiscountsPage));
    await waitFor(() => expect(screen.getByText(/Owner: create a discount code/i)).toBeInTheDocument());
    expect(screen.getByPlaceholderText("e.g. 1")).toBeInTheDocument();
  });

  it("submits create discount for owner", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "cafe_owner", role: "owner", id: 1, requires2FA: false })
    );
    fetch.mockImplementation((url) => {
      if (String(url).includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "cafe_owner" }));
      }
      return Promise.resolve(jsonFetch(true, { message: "valid code, enjoy saving" }));
    });
    wrap(createElement(DiscountsPage));
    fireEvent.change(screen.getByPlaceholderText("e.g. 1"), { target: { value: "3" } });
    fireEvent.change(screen.getByPlaceholderText("0.85"), { target: { value: "0.85" } });
    fireEvent.change(screen.getByPlaceholderText("SAVE10"), { target: { value: "SAVE10" } });
    fireEvent.click(screen.getByRole("button", { name: "Create discount" }));
    await waitFor(() => expect(fetch).toHaveBeenCalled());
    const call = fetch.mock.calls.find((c) => String(c[0]).includes("/discounts/"));
    expect(call).toBeTruthy();
    const opts = call[1];
    expect(opts.method).toBe("POST");
    expect(JSON.parse(opts.body)).toEqual({
      discount_rate: 0.85,
      discount_code: "SAVE10",
      restaurant_id: 3,
    });
  });

  it("blocks create with invalid restaurant id", () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "cafe_owner" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "cafe_owner", role: "owner", id: 1, requires2FA: false })
    );
    wrap(createElement(DiscountsPage));
    fireEvent.change(screen.getByPlaceholderText("e.g. 1"), { target: { value: "0" } });
    fireEvent.click(screen.getByRole("button", { name: "Create discount" }));
    expect(screen.getByText(/Restaurant ID must be a positive whole number/i)).toBeInTheDocument();
    expect(fetch.mock.calls.filter((c) => String(c[0]).includes("/discounts"))).toHaveLength(0);
  });

  it("shows non-owner message on discounts page", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "bob" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "bob", role: "customer", id: 2, requires2FA: false })
    );
    wrap(createElement(DiscountsPage));
    await screen.findByText(/Only accounts with the owner role can create or delete/i);
  });

  it("submits delete discount for owner", async () => {
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "cafe_owner", role: "owner", id: 1, requires2FA: false })
    );
    fetch.mockImplementation((url) => {
      if (String(url).includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "cafe_owner" }));
      }
      return Promise.resolve(jsonFetch(true, { message: "successfully removed code" }));
    });
    wrap(createElement(DiscountsPage));
    fireEvent.change(screen.getByPlaceholderText("Code to remove"), { target: { value: "SAVE10" } });
    fireEvent.click(screen.getByRole("checkbox", { name: /I want to remove this code/i }));
    fireEvent.click(screen.getByRole("button", { name: "Remove code" }));
    await waitFor(() => expect(fetch).toHaveBeenCalled());
    const call = fetch.mock.calls.find(
      (c) => String(c[0]).includes("/discounts/SAVE10") && c[1]?.method === "DELETE"
    );
    expect(call).toBeTruthy();
  });

  it("shows restaurants promo banner when cart has items", async () => {
    fetch.mockImplementation((url) => {
      const u = String(url);
      if (u.includes("/restaurants/1/menu")) {
        return Promise.resolve(jsonFetch(true, [{ item_name: "Burger", restaurant_id: 1, cost: 10, cuisine: "x" }]));
      }
      if (u.includes("/items/restaurant/1")) {
        return Promise.resolve(jsonFetch(true, [{ item_name: "Burger", restaurant_id: 1, cost: 10, cuisine: "x" }]));
      }
      if (u.includes("/restaurants")) {
        return Promise.resolve(jsonFetch(true, [{ restaurant_id: 1, cuisine: "x", avg_ratings: 5 }]));
      }
      return Promise.resolve(jsonFetch(true, {}));
    });
    wrap(createElement(RestaurantsPage));
    await screen.findByText(/Restaurant 1/i);
    fireEvent.click(screen.getByText("View menu"));
    await screen.findByText("Add to cart");
    fireEvent.click(screen.getByText("Add to cart"));
    expect(screen.getByRole("status")).toHaveTextContent(/Have a code/i);
  });
});
