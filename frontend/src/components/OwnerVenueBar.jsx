import React from "react";
import { useRestaurantWorkspace } from "../state/RestaurantWorkspaceContext";
import RestaurantWorkspacePicker from "./RestaurantWorkspacePicker";

/**
 * Owner/staff: shows linked venue and entry point to switch. Hidden for other roles.
 */
export default function OwnerVenueBar() {
  const {
    isWorkspaceRole,
    linkedRestaurant,
    status,
    error,
    pickerOpen,
    openPicker,
    closePicker,
    selectRestaurant,
    beginSwitchRestaurant,
  } = useRestaurantWorkspace();

  if (!isWorkspaceRole) return null;

  const mustChoose = status === "needs_selection";
  const showBanner = mustChoose && !pickerOpen;

  return (
    <>
      <RestaurantWorkspacePicker
        open={pickerOpen}
        onClose={closePicker}
        onSelect={selectRestaurant}
        mustChoose={mustChoose}
      />
      <div className="owner-venue-bar" data-testid="owner-venue-bar" role="region" aria-label="Your venue">
        {status === "loading" && <p className="owner-venue-bar__line muted">Loading your workspace…</p>}
        {status === "resolving" && (
          <p className="owner-venue-bar__line muted" data-testid="owner-venue-resolving">
            Connecting your account to your venue…
          </p>
        )}
        {status === "ready" && linkedRestaurant && (
          <div className="owner-venue-bar__inner">
            <span className="owner-venue-bar__chip" title={linkedRestaurant.label}>
              Current venue: <strong>{linkedRestaurant.label}</strong>
            </span>
            <button type="button" className="owner-venue-bar__linkish" onClick={beginSwitchRestaurant}>
              Switch venue
            </button>
          </div>
        )}
        {showBanner && (
          <div className="owner-venue-bar__banner" role="status">
            {error ? <p className="owner-venue-bar__hint muted">{error}</p> : null}
            <p>
              <strong>Choose your venue</strong> to use kitchen tools and reports without re-entering a venue number.
            </p>
            <button type="button" onClick={openPicker}>
              Choose venue
            </button>
          </div>
        )}
      </div>
    </>
  );
}
