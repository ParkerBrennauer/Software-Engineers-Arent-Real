import { describe, expect, it, vi, beforeEach } from "vitest";
import { resolveSessionRole } from "../state/AuthContext";
import { resolveVenueViaAdminOrdersProbe } from "../utils/ownerVenueResolution";

vi.mock("../api/client", () => ({
  api: {
    restaurantAdministration: {
      orders: vi.fn(),
    },
  },
}));

import { api } from "../api/client";

describe("resolveSessionRole", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("uses registration hint when present", () => {
    localStorage.setItem("frontend-auth-role-hint-v1", JSON.stringify({ pat: "owner" }));
    expect(resolveSessionRole("pat", "customer")).toBe("owner");
  });

  it("falls back to stored role when no hint", () => {
    expect(resolveSessionRole("pat", "staff")).toBe("staff");
  });

  it("infers from username when no hint or stored role", () => {
    expect(resolveSessionRole("cafe_owner", undefined)).toBe("owner");
  });

  it("preserves frontend-only admin role from cached session", () => {
    expect(resolveSessionRole("site_admin", "admin")).toBe("admin");
  });
});

describe("resolveVenueViaAdminOrdersProbe", () => {
  beforeEach(() => {
    vi.mocked(api.restaurantAdministration.orders).mockReset();
  });

  it("returns the first restaurant row the backend allows", async () => {
    vi.mocked(api.restaurantAdministration.orders).mockImplementation(async (id) => {
      if (String(id) === "3") return [];
      throw new Error("User does not have permission to view this restaurant's orders");
    });
    const rows = [
      { restaurant_id: 1, cuisine: "A" },
      { restaurant_id: 3, cuisine: "B" },
    ];
    const found = await resolveVenueViaAdminOrdersProbe(rows);
    expect(found?.restaurant_id).toBe(3);
  });

  it("returns null when every id is denied", async () => {
    vi.mocked(api.restaurantAdministration.orders).mockRejectedValue(
      new Error("User does not have permission to view this restaurant's orders")
    );
    const found = await resolveVenueViaAdminOrdersProbe([{ restaurant_id: 9, cuisine: "Z" }]);
    expect(found).toBeNull();
  });

  it("returns null on fatal errors", async () => {
    vi.mocked(api.restaurantAdministration.orders).mockRejectedValue(new Error("Server error"));
    const found = await resolveVenueViaAdminOrdersProbe([{ restaurant_id: 9, cuisine: "Z" }]);
    expect(found).toBeNull();
  });
});
