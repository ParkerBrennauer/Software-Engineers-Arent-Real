import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api/client";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [restaurant, setRestaurant] = useState(null);
  const [appliedCode, setAppliedCode] = useState(null);
  const [discountedTotal, setDiscountedTotal] = useState(null);
  const [discountError, setDiscountError] = useState("");
  const [applyingDiscount, setApplyingDiscount] = useState(false);
  const skipReapplyRef = useRef(false);

  function addItem(item) {
    if (!item?.restaurant_id) {
      return { ok: false, message: "Invalid menu item." };
    }
    if (restaurant && Number(restaurant.restaurant_id) !== Number(item.restaurant_id)) {
      return { ok: false, message: "Cart can only contain items from one restaurant at a time." };
    }
    setRestaurant((prev) => prev || { restaurant_id: item.restaurant_id, cuisine: item.cuisine });
    setItems((prev) => {
      const key = `${item.item_name}_${item.restaurant_id}`;
      const existing = prev.find((p) => p.key === key);
      if (!existing) return [...prev, { ...item, key, quantity: 1, price: item.cost ?? item.price ?? 0 }];
      return prev.map((p) => (p.key === key ? { ...p, quantity: p.quantity + 1 } : p));
    });
    return { ok: true };
  }

  function updateQty(key, quantity) {
    const q = Math.max(0, Number(quantity || 0));
    setItems((prev) => {
      const updated = prev.map((i) => (i.key === key ? { ...i, quantity: q } : i)).filter((i) => i.quantity > 0);
      if (updated.length === 0) setRestaurant(null);
      return updated;
    });
  }

  function removeItem(key) {
    setItems((prev) => {
      const updated = prev.filter((i) => i.key !== key);
      if (updated.length === 0) setRestaurant(null);
      return updated;
    });
  }

  function clearDiscountState() {
    setAppliedCode(null);
    setDiscountedTotal(null);
    setDiscountError("");
  }

  function clear() {
    setItems([]);
    setRestaurant(null);
    clearDiscountState();
  }

  function removeDiscount() {
    clearDiscountState();
  }

  const subtotal = useMemo(
    () => items.reduce((sum, i) => sum + (i.price || 0) * i.quantity, 0),
    [items]
  );
  const tax = useMemo(() => subtotal * 0.13, [subtotal]);
  const deliveryFee = items.length ? 2 : 0;
  const total = subtotal + tax + deliveryFee;

  const grandTotal = useMemo(() => {
    if (appliedCode && discountedTotal != null && Number.isFinite(Number(discountedTotal))) {
      return Number(discountedTotal);
    }
    return total;
  }, [appliedCode, discountedTotal, total]);

  const savingsAmount = useMemo(() => {
    if (!appliedCode || discountedTotal == null || !Number.isFinite(Number(discountedTotal))) return 0;
    const raw = total - Number(discountedTotal);
    return raw > 0 ? raw : 0;
  }, [appliedCode, discountedTotal, total]);

  async function applyDiscountCode(code) {
    const trimmed = String(code || "").trim();
    setDiscountError("");
    if (!trimmed) {
      setDiscountError("Enter a promo code.");
      return;
    }
    if (!items.length) {
      setDiscountError("Add items to your cart before applying a code.");
      return;
    }
    setApplyingDiscount(true);
    skipReapplyRef.current = true;
    try {
      const body = await api.discounts.apply({
        order_total: Number(total.toFixed(2)),
        discount_code: trimmed,
      });
      const dt = body?.discounted_total;
      if (dt == null || !Number.isFinite(Number(dt))) {
        setDiscountError("Invalid response from discount service.");
        setAppliedCode(null);
        setDiscountedTotal(null);
        return;
      }
      setAppliedCode(trimmed);
      setDiscountedTotal(Number(dt));
      setDiscountError("");
    } catch (err) {
      setDiscountError(err?.message || "Could not apply discount.");
      setAppliedCode(null);
      setDiscountedTotal(null);
    } finally {
      setApplyingDiscount(false);
    }
  }

  useEffect(() => {
    if (!items.length && appliedCode) {
      setAppliedCode(null);
      setDiscountedTotal(null);
      setDiscountError("");
    }
  }, [items.length, appliedCode]);

  useEffect(() => {
    if (!appliedCode || !items.length) return;
    if (skipReapplyRef.current) {
      skipReapplyRef.current = false;
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const body = await api.discounts.apply({
          order_total: Number(total.toFixed(2)),
          discount_code: appliedCode,
        });
        const dt = body?.discounted_total;
        if (cancelled) return;
        if (dt == null || !Number.isFinite(Number(dt))) {
          setDiscountError("Discount could not be recalculated.");
          setAppliedCode(null);
          setDiscountedTotal(null);
          return;
        }
        setDiscountedTotal(Number(dt));
        setDiscountError("");
      } catch (err) {
        if (cancelled) return;
        setDiscountError(err?.message || "Discount is no longer valid for this cart.");
        setAppliedCode(null);
        setDiscountedTotal(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [total, appliedCode, items.length]);

  const value = {
    items,
    restaurant,
    subtotal,
    tax,
    deliveryFee,
    total,
    grandTotal,
    savingsAmount,
    appliedCode,
    discountedTotal,
    discountError,
    applyingDiscount,
    addItem,
    updateQty,
    removeItem,
    clear,
    applyDiscountCode,
    removeDiscount,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}

/** Safe when used outside CartProvider (returns null). */
export function useCartOptional() {
  return useContext(CartContext);
}
