import { render, screen } from "@testing-library/react";
import { createElement } from "react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import App from "../App";
import RequireAuth from "../components/RequireAuth";
import OperationsPage from "../pages/OperationsPage";
import { AuthProvider } from "../state/AuthContext";
import { RestaurantWorkspaceProvider } from "../state/RestaurantWorkspaceContext";
import { CartProvider } from "../state/CartContext";
import { canViewOperationsContent } from "../utils/operationsAccess";

function jsonFetch(ok, data, status = 200) {
  const body = JSON.stringify(data);
  return { ok, status, text: async () => body, json: async () => JSON.parse(body) };
}

function wrapWithApp(initialEntry) {
  return render(
    createElement(
      MemoryRouter,
      { initialEntries: [initialEntry] },
      createElement(
        AuthProvider,
        null,
        createElement(RestaurantWorkspaceProvider, null, createElement(CartProvider, null, createElement(App)))
      )
    )
  );
}

function wrapOperationsRouteOnly(initialEntry) {
  return render(
    createElement(
      MemoryRouter,
      { initialEntries: [initialEntry] },
      createElement(
        AuthProvider,
        null,
        createElement(
          RestaurantWorkspaceProvider,
          null,
          createElement(
            Routes,
            null,
            createElement(
              Route,
              { path: "/operations", element: createElement(RequireAuth, null, createElement(OperationsPage)) }
            )
          )
        )
      )
    )
  );
}

const restricted = /restaurant owners and team accounts/i;

describe("canViewOperationsContent", () => {
  it("allows owner and admin (case-insensitive)", () => {
    expect(canViewOperationsContent("owner")).toBe(true);
    expect(canViewOperationsContent("OWNER")).toBe(true);
    expect(canViewOperationsContent("admin")).toBe(true);
    expect(canViewOperationsContent("Admin")).toBe(true);
  });

  it("denies customer, driver, and unknown strings; allows staff", () => {
    expect(canViewOperationsContent("customer")).toBe(false);
    expect(canViewOperationsContent("staff")).toBe(true);
    expect(canViewOperationsContent("driver")).toBe(false);
    expect(canViewOperationsContent("superuser")).toBe(false);
  });

  it("fails safe when role is missing or not a non-empty string", () => {
    expect(canViewOperationsContent(undefined)).toBe(false);
    expect(canViewOperationsContent(null)).toBe(false);
    expect(canViewOperationsContent("")).toBe(false);
    expect(canViewOperationsContent("   ")).toBe(false);
    expect(canViewOperationsContent(42)).toBe(false);
  });
});

describe("Operations access UI", () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
  });

  it("lets restaurant owners see operations controls", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "cafe_owner" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "cafe_owner", role: "owner", id: 1, requires2FA: false })
    );
    localStorage.setItem(
      "frontend-restaurant-workspace-by-user-v1",
      JSON.stringify({
        cafe_owner: { restaurantId: 1, label: "Restaurant 1", cuisine: "" },
      })
    );
    wrapOperationsRouteOnly("/operations");
    expect(await screen.findByRole("heading", { name: /Business tools/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /^All orders$/ })).toBeInTheDocument();
    expect(screen.queryByText(restricted)).not.toBeInTheDocument();
  });

  it("lets admins see operations controls", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "site_admin" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "site_admin", role: "admin", id: 9, requires2FA: false })
    );
    wrapOperationsRouteOnly("/operations");
    expect(await screen.findByRole("button", { name: /^All orders$/ })).toBeInTheDocument();
  });

  it("shows restricted message for customers and hides operations actions", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "bob" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "bob", role: "customer", id: 2, requires2FA: false })
    );
    wrapOperationsRouteOnly("/operations");
    expect(await screen.findByText(restricted)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^All orders$/ })).not.toBeInTheDocument();
    expect(screen.queryByRole("heading", { name: /Business tools/i })).not.toBeInTheDocument();
  });

  it("lets staff see operations controls when a venue is linked", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "staffer" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "staffer", role: "staff", id: 3, requires2FA: false })
    );
    localStorage.setItem(
      "frontend-restaurant-workspace-by-user-v1",
      JSON.stringify({
        staffer: { restaurantId: 2, label: "Restaurant 2", cuisine: "" },
      })
    );
    wrapOperationsRouteOnly("/operations");
    expect(await screen.findByRole("button", { name: /^All orders$/ })).toBeInTheDocument();
    expect(screen.queryByText(restricted)).not.toBeInTheDocument();
  });

  it("treats drivers as unauthorized for operations content", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "driver1" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "driver1", role: "driver", id: 31, requires2FA: false })
    );
    wrapOperationsRouteOnly("/operations");
    expect(await screen.findByText(restricted)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^All orders$/ })).not.toBeInTheDocument();
  });

  it("fails safe when role is unknown or omitted", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "legacy" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "legacy", id: 4, requires2FA: false })
    );
    wrapOperationsRouteOnly("/operations");
    expect(await screen.findByText(restricted)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^All orders$/ })).not.toBeInTheDocument();
  });

  it("keeps the Business nav link while gating /operations for a customer", async () => {
    fetch.mockResolvedValue(jsonFetch(true, { username: "bob" }));
    localStorage.setItem(
      "frontend-auth-user",
      JSON.stringify({ username: "bob", role: "customer", id: 2, requires2FA: false })
    );
    wrapWithApp("/operations");
    expect(await screen.findByRole("link", { name: "Business" })).toBeInTheDocument();
    expect(screen.getByText(restricted)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /^All orders$/ })).not.toBeInTheDocument();
  });
});
