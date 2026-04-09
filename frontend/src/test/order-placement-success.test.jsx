import React, { createElement, useEffect, useRef, useState } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { api } from "../api/client";
import { AuthProvider } from "../state/AuthContext";
import { RestaurantWorkspaceProvider } from "../state/RestaurantWorkspaceContext";
import { CartProvider, useCart } from "../state/CartContext";
import OrdersPage from "../pages/OrdersPage";
import OrderPlacementSuccess from "../components/OrderPlacementSuccess";
import { getOrderPlacementDetails } from "../utils/orderPlacementDetails";

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrap(ui) {
  return render(
    createElement(
      MemoryRouter,
      null,
      createElement(
        AuthProvider,
        null,
        createElement(RestaurantWorkspaceProvider, null, createElement(CartProvider, null, ui))
      )
    )
  );
}

function OrdersWithCartPrimed() {
  const { addItem } = useCart();
  const [ready, setReady] = useState(false);
  const primed = useRef(false);
  useEffect(() => {
    if (primed.current) return;
    primed.current = true;
    addItem({ item_name: "Taccos", restaurant_id: 1, cost: 1.5 });
    addItem({ item_name: "Cookie", restaurant_id: 1, cost: 2.17 });
    setReady(true);
  }, [addItem]);
  if (!ready) return null;
  return createElement(OrdersPage);
}

describe("getOrderPlacementDetails", () => {
  it("extracts id, cost, and item names", () => {
    const d = getOrderPlacementDetails({
      id: 10004,
      cost: 3.67,
      items: [{ item_name: "Taccos" }, { item_name: "Cookie" }],
    });
    expect(d.orderIdDisplay).toBe("10004");
    expect(d.costDisplay).toMatch(/3\.67/);
    expect(d.itemLines).toEqual(["Taccos", "Cookie"]);
  });

  it("uses order_id and name fallback on item objects", () => {
    const d = getOrderPlacementDetails({
      order_id: 9,
      cost: 10,
      items: [{ name: "A" }, { title: "B" }],
    });
    expect(d.orderIdDisplay).toBe("9");
    expect(d.itemLines).toEqual(["A", "B"]);
  });

  it("handles missing or invalid data gracefully", () => {
    expect(getOrderPlacementDetails(null).orderIdDisplay).toBe("Unavailable");
    expect(getOrderPlacementDetails({}).costDisplay).toBe("Unavailable");
    expect(getOrderPlacementDetails({ id: 1, items: [] }).itemLines).toEqual([]);
  });
});

describe("OrderPlacementSuccess", () => {
  it("lists items and shows cost and order number", () => {
    render(
      createElement(
        MemoryRouter,
        null,
        createElement(OrderPlacementSuccess, {
          orderPayload: { id: 10004, cost: 3.67, items: [{ item_name: "Taccos" }, { item_name: "Cookie" }] },
        })
      )
    );
    expect(screen.getByText(/Thank you! Your order has been created/i)).toBeInTheDocument();
    expect(screen.getByText("Taccos")).toBeInTheDocument();
    expect(screen.getByText("Cookie")).toBeInTheDocument();
    expect(screen.getByText(/Total cost:/i).closest("p")).toHaveTextContent(/3\.67/);
    expect(screen.getByText(/Order number:/i).closest("p")).toHaveTextContent(/10004/);
    expect(document.querySelector("pre.json")).toBeNull();
  });

  it("shows Items unavailable when no item lines", () => {
    render(
      createElement(
        MemoryRouter,
        null,
        createElement(OrderPlacementSuccess, { orderPayload: { id: 1, cost: 2, items: [] } })
      )
    );
    expect(screen.getByText("Items unavailable")).toBeInTheDocument();
  });
});

describe("OrdersPage checkout confirmation", () => {
  beforeEach(() => {
    localStorage.setItem("frontend-auth-user", JSON.stringify({ username: "cust", role: "customer", id: 1 }));
    global.fetch = vi.fn((url) => {
      if (String(url).includes("/users/current-user")) {
        return Promise.resolve(jsonFetch(true, { username: "cust" }));
      }
      return Promise.resolve(jsonFetch(true, {}));
    });
    vi.spyOn(api.orders, "place").mockResolvedValue({
      id: 10004,
      cost: 3.67,
      items: [{ item_name: "Taccos", price: 1.5 }, { item_name: "Cookie", price: 2.17 }],
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("shows friendly confirmation after place order and does not render raw JSON", async () => {
    wrap(createElement(OrdersWithCartPrimed));
    await waitFor(() => expect(screen.getByRole("button", { name: /^Place order$/i })).not.toBeDisabled());

    fireEvent.click(screen.getByRole("button", { name: /^Place order$/i }));

    await screen.findByText(/Thank you! Your order has been created/i);
    expect(screen.getByText("Taccos")).toBeInTheDocument();
    expect(screen.getByText("Cookie")).toBeInTheDocument();
    expect(screen.getByText(/Order number:/i).closest("p")).toHaveTextContent(/10004/);

    expect(document.querySelector("pre.json")).toBeNull();
  });
});
