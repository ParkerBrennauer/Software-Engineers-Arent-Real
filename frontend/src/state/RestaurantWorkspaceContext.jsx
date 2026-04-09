import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";
import { api } from "../api/client";
import { normalizeApiArray } from "../utils/normalizeApiArray";
import { resolveVenueViaAdminOrdersProbe } from "../utils/ownerVenueResolution";
import {
  clearLinkedRestaurant,
  readLinkedRestaurant,
  writeLinkedRestaurant,
} from "../utils/restaurantWorkspaceStorage";

const RestaurantWorkspaceContext = createContext(null);

/** @param {unknown} r */
export function buildRestaurantDisplayLabel(r) {
  const id = r?.restaurant_id;
  if (id == null) return "";
  const c = r?.cuisine != null && String(r.cuisine).trim() ? String(r.cuisine).trim() : "";
  return c ? `Restaurant ${id} · ${c}` : `Restaurant ${id}`;
}

export function RestaurantWorkspaceProvider({ children }) {
  const { user, bootstrapping } = useAuth();
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState("");
  const [linked, setLinked] = useState(null);
  const [pickerOpen, setPickerOpen] = useState(false);

  const isWorkspaceRole = Boolean(
    user && !user.requires2FA && (user.role === "owner" || user.role === "staff")
  );

  const resetWorkspace = useCallback(() => {
    setLinked(null);
    setStatus("idle");
    setError("");
    setPickerOpen(false);
  }, []);

  useEffect(() => {
    if (bootstrapping) return;
    if (!user?.username || user.requires2FA) {
      resetWorkspace();
      return;
    }
    if (!isWorkspaceRole) {
      resetWorkspace();
      return;
    }

    let cancelled = false;

    const cached = readLinkedRestaurant(user.username);
    if (cached) {
      setError("");
      setLinked({
        id: cached.restaurantId,
        label: cached.label,
        cuisine: cached.cuisine,
      });
      setStatus("ready");
      setPickerOpen(false);
      return undefined;
    }

    setLinked(null);
    setError("");
    setStatus("resolving");
    setPickerOpen(false);

    (async () => {
      try {
        const data = await api.restaurants.getAll();
        if (cancelled) return;
        const list = normalizeApiArray(data).filter((r) => r?.restaurant_id != null);
        const found = await resolveVenueViaAdminOrdersProbe(list);
        if (cancelled) return;
        if (found?.restaurant_id != null) {
          const id = Number(found.restaurant_id);
          if (Number.isInteger(id) && id > 0) {
            const label = buildRestaurantDisplayLabel(found);
            const cuisine = found?.cuisine != null ? String(found.cuisine) : "";
            writeLinkedRestaurant(user.username, { restaurantId: id, label, cuisine });
            setLinked({ id, label, cuisine });
            setStatus("ready");
            setPickerOpen(false);
            setError("");
            return;
          }
        }
        setStatus("needs_selection");
        setPickerOpen(true);
      } catch {
        if (cancelled) return;
        setStatus("needs_selection");
        setPickerOpen(true);
        setError("We could not detect your venue automatically. Please choose it once below.");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [user?.username, user?.role, user?.requires2FA, bootstrapping, isWorkspaceRole, resetWorkspace]);

  const selectRestaurant = useCallback(async (restaurant) => {
    if (!user?.username || !restaurant?.restaurant_id) return;
    const id = Number(restaurant.restaurant_id);
    if (!Number.isInteger(id) || id <= 0) return;
    const label = buildRestaurantDisplayLabel(restaurant);
    const cuisine = restaurant?.cuisine != null ? String(restaurant.cuisine) : "";

    try {
      await api.restaurantAdministration.switchVenue(id);
      writeLinkedRestaurant(user.username, { restaurantId: id, label, cuisine });
      setLinked({ id, label, cuisine });
      setStatus("ready");
      setPickerOpen(false);
      setError("");
    } catch (err) {
      console.error("Failed to switch venue: ", err);
      setError(err?.message || "Failed to switch venue.");
    }
  }, [user?.username]);

  const openPicker = useCallback(() => {
    setPickerOpen(true);
  }, []);

  const closePicker = useCallback(() => {
    setPickerOpen(false);
  }, []);

  const beginSwitchRestaurant = useCallback(() => {
    if (!user?.username) return;
    clearLinkedRestaurant(user.username);
    setLinked(null);
    setStatus("needs_selection");
    setPickerOpen(true);
    setError("");
  }, [user?.username]);

  const resolvedStatus = bootstrapping ? "loading" : status;

  const value = useMemo(
    () => ({
      isWorkspaceRole,
      linkedRestaurant: linked,
      /** idle | loading | resolving | ready | needs_selection */
      status: resolvedStatus,
      error,
      pickerOpen,
      openPicker,
      closePicker,
      selectRestaurant,
      beginSwitchRestaurant,
    }),
    [
      isWorkspaceRole,
      linked,
      resolvedStatus,
      error,
      pickerOpen,
      openPicker,
      closePicker,
      selectRestaurant,
      beginSwitchRestaurant,
    ]
  );

  return (
    <RestaurantWorkspaceContext.Provider value={value}>{children}</RestaurantWorkspaceContext.Provider>
  );
}

export function useRestaurantWorkspace() {
  const ctx = useContext(RestaurantWorkspaceContext);
  if (!ctx) throw new Error("useRestaurantWorkspace must be used within RestaurantWorkspaceProvider");
  return ctx;
}
