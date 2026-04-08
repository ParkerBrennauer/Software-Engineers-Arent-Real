import React, { useState } from "react";
import { useCart } from "../state/CartContext";

export default function CartPanel() {
  const {
    items,
    subtotal,
    tax,
    deliveryFee,
    total,
    grandTotal,
    savingsAmount,
    appliedCode,
    discountError,
    applyingDiscount,
    updateQty,
    removeItem,
    clear,
    applyDiscountCode,
    removeDiscount,
  } = useCart();
  const [codeInput, setCodeInput] = useState("");

  return (
    <aside className="panel cart-panel">
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
          <button type="button" onClick={() => removeItem(item.key)}>Remove</button>
        </div>
      ))}

      {items.length > 0 && (
        <div className="promo-block">
          <h4 className="promo-heading">Promo code</h4>
          <p className="muted small-print">
            The backend multiplies your order total by the code&apos;s stored rate (for example, 0.85 means you pay 85%
            of the total). Codes are not validated against the restaurant on apply.
          </p>
          <div className="row promo-row">
            <input
              placeholder="Enter code"
              value={codeInput}
              onChange={(e) => setCodeInput(e.target.value)}
              disabled={applyingDiscount}
              aria-label="Promo code"
            />
            <button
              type="button"
              disabled={applyingDiscount || !codeInput.trim()}
              onClick={async () => {
                await applyDiscountCode(codeInput);
              }}
            >
              {applyingDiscount ? "Applying…" : "Apply"}
            </button>
            {appliedCode && (
              <button type="button" disabled={applyingDiscount} onClick={() => { removeDiscount(); setCodeInput(""); }}>
                Remove
              </button>
            )}
          </div>
          {appliedCode && (
            <p className="success small-print">
              Applied: <strong>{appliedCode}</strong>
              {savingsAmount > 0 && (
                <span className="savings-chip">−${savingsAmount.toFixed(2)}</span>
              )}
            </p>
          )}
          {discountError && <p className="error small-print">{discountError}</p>}
        </div>
      )}

      <div className="price-breakdown">
        <p>Subtotal: ${subtotal.toFixed(2)}</p>
        <p>Tax: ${tax.toFixed(2)}</p>
        <p>Delivery: ${deliveryFee.toFixed(2)}</p>
        {appliedCode && savingsAmount > 0 && (
          <p className="success">
            Discount (estimate): −${savingsAmount.toFixed(2)}
          </p>
        )}
        <p>
          <strong>Total: ${grandTotal.toFixed(2)}</strong>
          {appliedCode && total !== grandTotal && (
            <span className="muted strike-wrap">
              {" "}
              <span className="strike">${total.toFixed(2)}</span>
            </span>
          )}
        </p>
      </div>
      <button type="button" onClick={clear}>Clear cart</button>
    </aside>
  );
}
