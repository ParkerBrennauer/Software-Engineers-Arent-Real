import React from "react";
import { Link } from "react-router-dom";
import { getOrderPlacementDetails } from "../utils/orderPlacementDetails";

/** Order confirmation banner shown after a successful checkout. */
export default function OrderPlacementSuccess({ orderPayload, onDismiss, trackSectionId = "track-order-section" }) {
  const { orderIdDisplay, costDisplay, itemLines } = getOrderPlacementDetails(orderPayload);
  const listItems = itemLines.length > 0 ? itemLines : ["Items unavailable"];

  return (
    <section
      className="panel order-placement-success"
      role="status"
      aria-live="polite"
      aria-labelledby="order-placement-success-heading"
    >
      <div className="order-placement-success__header">
        <span className="order-placement-success__icon" aria-hidden="true">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </svg>
        </span>
        <h3 id="order-placement-success-heading" className="order-placement-success__title">
          Thank you! Your order has been created.
        </h3>
      </div>

      <div className="order-placement-success__body">
        <p className="order-placement-success__label">Items:</p>
        <ul className="order-placement-success__list list-compact">
          {listItems.map((line, idx) => (
            <li key={`${idx}-${line}`}>{line}</li>
          ))}
        </ul>
        <p className="order-placement-success__meta">
          <span className="order-placement-success__strong">Total cost:</span> {costDisplay}
        </p>
        <p className="order-placement-success__meta">
          <span className="order-placement-success__strong">Order number:</span> {orderIdDisplay}
        </p>
      </div>

      <div className="order-placement-success__actions row">
        <a className="button-link" href={`#${trackSectionId}`}>
          View order
        </a>
        <Link className="button-link" to="/restaurants">
          Continue browsing
        </Link>
        {typeof onDismiss === "function" && (
          <button type="button" className="order-placement-success__dismiss" onClick={onDismiss}>
            Dismiss
          </button>
        )}
      </div>
    </section>
  );
}
