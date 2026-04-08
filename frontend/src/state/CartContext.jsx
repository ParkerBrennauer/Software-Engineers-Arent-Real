import React, { createContext, useContext, useMemo, useState } from "react";

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const [restaurant, setRestaurant] = useState(null);

  function addItem(item) {
    setRestaurant((prev) => prev || { restaurant_id: item.restaurant_id, cuisine: item.cuisine });
    setItems((prev) => {
      const key = `${item.item_name}_${item.restaurant_id}`;
      const existing = prev.find((p) => p.key === key);
      if (!existing) return [...prev, { ...item, key, quantity: 1, price: item.cost ?? item.price ?? 0 }];
      return prev.map((p) => (p.key === key ? { ...p, quantity: p.quantity + 1 } : p));
    });
  }

  function updateQty(key, quantity) {
    const q = Math.max(0, Number(quantity || 0));
    setItems((prev) => prev.map((i) => (i.key === key ? { ...i, quantity: q } : i)).filter((i) => i.quantity > 0));
  }

  function removeItem(key) {
    setItems((prev) => prev.filter((i) => i.key !== key));
  }

  function clear() {
    setItems([]);
    setRestaurant(null);
  }

  const subtotal = useMemo(
    () => items.reduce((sum, i) => sum + (i.price || 0) * i.quantity, 0),
    [items]
  );
  const tax = useMemo(() => subtotal * 0.13, [subtotal]);
  const deliveryFee = items.length ? 2 : 0;
  const total = subtotal + tax + deliveryFee;

  const value = {
    items,
    restaurant,
    subtotal,
    tax,
    deliveryFee,
    total,
    addItem,
    updateQty,
    removeItem,
    clear,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used within CartProvider");
  return ctx;
}

