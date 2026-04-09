import React from "react";
import { createElement } from "react";
import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import KitchenOrderBoard from "../components/KitchenOrderBoard";

vi.mock("../state/RestaurantWorkspaceContext", () => ({
  useRestaurantWorkspace: () => ({
    linkedRestaurant: null,
    status: "needs_selection",
    beginSwitchRestaurant: vi.fn(),
    openPicker: vi.fn(),
    closePicker: vi.fn(),
    selectRestaurant: vi.fn(),
    isWorkspaceRole: true,
    error: "",
    pickerOpen: false,
  }),
  RestaurantWorkspaceProvider: ({ children }) => children,
  buildRestaurantDisplayLabel: (r) => `Restaurant ${r?.restaurant_id ?? ""}`,
}));

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrap(ui) {
  return render(createElement(MemoryRouter, null, ui));
}

describe("KitchenOrderBoard", () => {
  beforeEach(() => {
    localStorage.clear();
    global.fetch = vi.fn();
  });

  it("does not use a typed order number field for kitchen actions", () => {
    wrap(createElement(KitchenOrderBoard));
    expect(screen.queryByPlaceholderText("Order number")).not.toBeInTheDocument();
  });

  it("loads restaurant orders and marks ready from the card (PUT /ready)", async () => {
    const user = userEvent.setup();
    let ordersPayload = [
      {
        id: 42,
        order_status: "confirmed",
        items: [{ item_name: "Soup" }],
        cost: 9.5,
        payment_status: "paid",
        customer: "Pat",
      },
    ];

    fetch.mockImplementation((url, opts) => {
      const u = String(url);
      if (u.includes("/restaurant_administration/restaurants/9/orders") && (!opts || opts.method === "GET")) {
        return Promise.resolve(jsonFetch(true, ordersPayload));
      }
      if (u.includes("/orders/42/ready") && opts?.method === "PUT") {
        ordersPayload = [{ ...ordersPayload[0], order_status: "ready_for_pickup" }];
        return Promise.resolve(jsonFetch(true, { ok: true }));
      }
      return Promise.resolve(jsonFetch(false, { detail: "unexpected " + u }, 500));
    });

    wrap(createElement(KitchenOrderBoard));
    await user.type(screen.getByLabelText("Venue number"), "9");
    await user.click(screen.getByRole("button", { name: /^Load orders$/i }));

    await screen.findByText(/Order #42/i);
    const markBtn = screen.getByRole("button", { name: /^Mark ready$/i });
    await user.click(markBtn);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("/orders/42/ready"),
        expect.objectContaining({ method: "PUT" })
      );
    });
  });

  it("assigns driver via saved name and dropdown, not a per-order driver text box", async () => {
    const user = userEvent.setup();
    const orderRow = {
      id: 77,
      order_status: "confirmed",
      items: [],
      cost: 3,
      payment_status: "paid",
      driver: "",
    };

    fetch.mockImplementation((url, opts) => {
      const u = String(url);
      if (u.includes("/restaurant_administration/restaurants/2/orders") && (!opts || opts.method === "GET")) {
        return Promise.resolve(jsonFetch(true, [orderRow]));
      }
      if (u.includes("/orders/77/assign-driver") && u.includes("driver=alex") && opts?.method === "PUT") {
        return Promise.resolve(jsonFetch(true, { ok: true }));
      }
      return Promise.resolve(jsonFetch(false, { detail: "unexpected " + u }, 500));
    });

    wrap(createElement(KitchenOrderBoard));
    await user.type(screen.getByLabelText("Venue number"), "2");
    await user.type(screen.getByLabelText("Add driver username"), "alex");
    await user.click(screen.getByRole("button", { name: /^Save name$/i }));
    await user.click(screen.getByRole("button", { name: /^Load orders$/i }));

    await screen.findByText(/Order #77/i);
    const assignCombo = screen.getByLabelText(/Assign driver for order 77/i);
    expect(within(assignCombo).getByRole("option", { name: "alex" })).toBeInTheDocument();

    await user.selectOptions(assignCombo, "alex");
    const assignButtons = screen.getAllByRole("button", { name: /^Assign driver$/i });
    await user.click(assignButtons[0]);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/orders\/77\/assign-driver\?driver=alex/),
        expect.objectContaining({ method: "PUT" })
      );
    });
  });

  it("disables Mark ready while that order action is in flight", async () => {
    const user = userEvent.setup();
    let resolveReady;
    const readyPromise = new Promise((res) => {
      resolveReady = res;
    });

    fetch.mockImplementation((url, opts) => {
      const u = String(url);
      if (u.includes("/restaurant_administration/restaurants/1/orders") && (!opts || opts.method === "GET")) {
        return Promise.resolve(
          jsonFetch(true, [{ id: 1, order_status: "confirmed", items: [], cost: 1, payment_status: "paid" }])
        );
      }
      if (u.includes("/orders/1/ready") && opts?.method === "PUT") {
        return readyPromise.then(() => jsonFetch(true, {}));
      }
      return Promise.resolve(jsonFetch(true, []));
    });

    wrap(createElement(KitchenOrderBoard));
    await user.type(screen.getByLabelText("Venue number"), "1");
    await user.click(screen.getByRole("button", { name: /^Load orders$/i }));
    await screen.findByText(/Order #1/i);

    const markBtn = screen.getByRole("button", { name: /^Mark ready$/i });
    await user.click(markBtn);
    expect(markBtn).toBeDisabled();

    resolveReady();
    await waitFor(() => expect(markBtn).not.toBeDisabled());
  });

  it("shows load error from API without crashing", async () => {
    const user = userEvent.setup();
    fetch.mockResolvedValue(jsonFetch(false, { detail: "Restaurant not found" }, 404));

    wrap(createElement(KitchenOrderBoard));
    await user.type(screen.getByLabelText("Venue number"), "bad");
    await user.click(screen.getByRole("button", { name: /^Load orders$/i }));

    await screen.findByRole("alert");
    expect(screen.getByText(/Restaurant not found/i)).toBeInTheDocument();
  });
});
