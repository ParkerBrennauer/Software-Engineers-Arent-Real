import { useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../state/AuthContext";

export default function OperationsPage() {
  const { user } = useAuth();
  const [restaurantId, setRestaurantId] = useState("");
  const [discountCode, setDiscountCode] = useState("SAVE10");
  const [staffUsername, setStaffUsername] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function run(call) {
    setError("");
    try {
      setResult(await call());
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="card">
      <h2>Role operations</h2>
      <p className="muted">Current role: {user?.role}. Backend auth is session-global and not token-based.</p>
      <div className="row">
        <input placeholder="Restaurant ID" value={restaurantId} onChange={(e) => setRestaurantId(e.target.value)} />
        <button onClick={() => run(() => api.restaurantAdministration.orders(restaurantId))}>Owner orders</button>
        <button onClick={() => run(() => api.restaurantAdministration.ordersByStatus(restaurantId, "delayed"))}>Owner orders by status</button>
      </div>
      <div className="row">
        <input placeholder="Staff username" value={staffUsername} onChange={(e) => setStaffUsername(e.target.value)} />
        <button onClick={() => run(() => api.restaurantAdministration.assignStaff(staffUsername))}>Assign staff</button>
      </div>
      <div className="row">
        <input placeholder="Discount code" value={discountCode} onChange={(e) => setDiscountCode(e.target.value)} />
        <button onClick={() => run(() => api.discounts.apply({ order_total: 50, discount_code: discountCode }))}>Apply discount</button>
        <button onClick={() => run(() => api.discounts.create({ discount_rate: 0.9, discount_code: discountCode, restaurant_id: Number(restaurantId || 1) }))}>Create discount</button>
        <button onClick={() => run(() => api.discounts.remove(discountCode))}>Delete discount</button>
      </div>
      {error && <p className="error">{error}</p>}
      {result && <pre className="json">{JSON.stringify(result, null, 2)}</pre>}
    </section>
  );
}

