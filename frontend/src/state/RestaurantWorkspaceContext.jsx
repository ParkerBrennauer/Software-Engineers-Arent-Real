import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useAuth } from "./AuthContext";
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

    setError("");
    const cached = readLinkedRestaurant(user.username);
    if (cached) {
      setLinked({
        id: cached.restaurantId,
        label: cached.label,
        cuisine: cached.cuisine,
      });
      setStatus("ready");
      setPickerOpen(false);
      return;
    }
    setLinked(null);
    setStatus("needs_selection");
    setPickerOpen(true);
  }, [user?.username, user?.role, user?.requires2FA, bootstrapping, isWorkspaceRole, resetWorkspace]);

  const selectRestaurant = useCallback((restaurant) => {
    if (!user?.username || !restaurant?.restaurant_id) return;
    const id = Number(restaurant.restaurant_id);
    if (!Number.isInteger(id) || id <= 0) return;
    const label = buildRestaurantDisplayLabel(restaurant);
    const cuisine = restaurant?.cuisine != null ? String(restaurant.cuisine) : "";
    writeLinkedRestaurant(user.username, { restaurantId: id, label, cuisine });
    setLinked({ id, label, cuisine });
    setStatus("ready");
    setPickerOpen(false);
    setError("");
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
      /** idle | loading | ready | needs_selection */
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
