import React from "react";
import { useCart } from "../state/CartContext";

export default function CartPanel() {
  const { items, subtotal, tax, deliveryFee, total, updateQty, removeItem, clear } = useCart();

  return (
    <aside className="panel">
      <h3>Cart</h3>
      {items.length === 0 && <p className="muted">Your cart is empty.</p>}
      {items.map((item) => (
        <div className="row" key={item.key}>
          <span>{item.item_name}</span>
          <input
            aria-label={`qty-${item.key}`}
            type="number"
            min="0"
            value={item.quantity}
            onChange={(e) => updateQty(item.key, e.target.value)}
            style={{ width: 70 }}
          />
          <button onClick={() => removeItem(item.key)}>Remove</button>
        </div>
      ))}
      <p>Subtotal: ${subtotal.toFixed(2)}</p>
      <p>Tax: ${tax.toFixed(2)}</p>
      <p>Delivery: ${deliveryFee.toFixed(2)}</p>
      <p><strong>Total: ${total.toFixed(2)}</strong></p>
      <button onClick={clear}>Clear cart</button>
    </aside>
  );
}

