import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { applyDiscountCode, createOrder, getRestaurantMenu } from '../lib/api';
import { useAuth } from '../state/AuthContext';

const TAX_RATE = 0.13;

function roundCurrency(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

function deriveRestaurantName(restaurantId) {
  return `Restaurant_${restaurantId}`;
}

function deriveOrderItems(selectedItems, { tipAmount, discountAmount, discountCode }) {
  const items = selectedItems.map((item) => ({
    item_name: item.item_name,
    price: Number(item.cost || 0),
  }));

  if (tipAmount > 0) {
    items.push({
      item_name: 'Tip',
      price: roundCurrency(tipAmount),
    });
  }

  if (discountAmount > 0) {
    items.push({
      item_name: discountCode ? `Discount (${discountCode})` : 'Discount',
      price: roundCurrency(-discountAmount),
    });
  }

  return items;
}

export default function OrderPage() {
  const { restaurantId } = useParams();
  const numericRestaurantId = Number(restaurantId);

  const [menuItems, setMenuItems] = useState([]);
  const [selectedItemKeys, setSelectedItemKeys] = useState([]);
  const [checkoutStep, setCheckoutStep] = useState('items');
  const [tipAmountInput, setTipAmountInput] = useState('0');
  const [discountCodeInput, setDiscountCodeInput] = useState('');
  const [appliedDiscountCode, setAppliedDiscountCode] = useState('');
  const [discountAmount, setDiscountAmount] = useState(0);
  const [discountMessage, setDiscountMessage] = useState('');
  const [isApplyingDiscount, setIsApplyingDiscount] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    let isMounted = true;

    const loadMenu = async () => {
      setIsLoading(true);
      setError('');

      try {
        const payload = await getRestaurantMenu(numericRestaurantId);
        if (isMounted) {
          const normalized = Array.isArray(payload)
            ? payload
            : payload && typeof payload === 'object'
              ? Object.values(payload)
              : [];
          setMenuItems(normalized);
        }
      } catch (err) {
        if (isMounted) {
          setError(err.message || 'Could not load restaurant menu.');
        }
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    if (Number.isFinite(numericRestaurantId)) {
      loadMenu();
    } else {
      setError('Invalid restaurant id.');
      setIsLoading(false);
    }

    return () => {
      isMounted = false;
    };
  }, [numericRestaurantId]);

  const selectedItems = useMemo(
    () =>
      menuItems.filter((item) =>
        selectedItemKeys.includes(`${item.item_name}_${item.restaurant_id}`),
      ),
    [menuItems, selectedItemKeys],
  );

  const estimatedSubtotal = useMemo(
    () =>
      selectedItems.reduce((total, item) => total + Number(item.cost || 0), 0),
    [selectedItems],
  );

  const tipAmount = useMemo(() => {
    const parsed = Number(tipAmountInput);
    if (!Number.isFinite(parsed) || parsed <= 0) {
      return 0;
    }
    return roundCurrency(parsed);
  }, [tipAmountInput]);

  const subtotalAfterDiscount = useMemo(
    () => Math.max(roundCurrency(estimatedSubtotal - discountAmount), 0),
    [discountAmount, estimatedSubtotal],
  );

  const adjustedSubtotal = useMemo(
    () => roundCurrency(subtotalAfterDiscount + tipAmount),
    [subtotalAfterDiscount, tipAmount],
  );

  const estimatedTotalWithTax = useMemo(
    () => roundCurrency(adjustedSubtotal * (1 + TAX_RATE)),
    [adjustedSubtotal],
  );

  const resetAppliedDiscount = () => {
    setAppliedDiscountCode('');
    setDiscountAmount(0);
    setDiscountMessage('');
  };

  const toggleItem = (item) => {
    const key = `${item.item_name}_${item.restaurant_id}`;
    setSelectedItemKeys((current) =>
      current.includes(key)
        ? current.filter((entry) => entry !== key)
        : [...current, key],
    );
    resetAppliedDiscount();
  };

  const continueToAdjustments = () => {
    setError('');

    if (selectedItems.length === 0) {
      setError('Please select at least one menu item.');
      return false;
    }

    setCheckoutStep('adjustments');
    return true;
  };

  const handleDiscountApply = async () => {
    const normalizedCode = discountCodeInput.trim();
    setError('');
    setDiscountMessage('');

    if (!normalizedCode) {
      resetAppliedDiscount();
      return;
    }

    if (estimatedSubtotal <= 0) {
      setError('Select at least one menu item before applying a discount code.');
      return;
    }

    setIsApplyingDiscount(true);
    try {
      const response = await applyDiscountCode({
        orderTotal: estimatedSubtotal,
        discountCode: normalizedCode,
      });
      const discountedTotal = Number(response?.discounted_total);
      if (!Number.isFinite(discountedTotal)) {
        throw new Error('Invalid discount response from server.');
      }

      const nextDiscountAmount = Math.max(
        roundCurrency(estimatedSubtotal - discountedTotal),
        0,
      );

      setDiscountAmount(nextDiscountAmount);
      setAppliedDiscountCode(normalizedCode);
      setDiscountMessage(
        nextDiscountAmount > 0
          ? `Code applied. You saved $${nextDiscountAmount.toFixed(2)}.`
          : 'Code applied, but no discount amount was returned.',
      );
    } catch (err) {
      resetAppliedDiscount();
      setError(err.message || 'Could not apply discount code.');
    } finally {
      setIsApplyingDiscount(false);
    }
  };

  const submitOrder = async (event) => {
    event.preventDefault();
    setError('');

    if (checkoutStep !== 'adjustments') {
      continueToAdjustments();
      return;
    }

    if (selectedItems.length === 0) {
      setError('Please select at least one menu item.');
      return;
    }

    const normalizedCode = discountCodeInput.trim();
    if (normalizedCode && appliedDiscountCode !== normalizedCode) {
      setError('Please apply your discount code before placing the order.');
      return;
    }

    setIsSubmitting(true);

    try {
      const primaryCuisine = selectedItems[0]?.cuisine || 'Unknown';
      const payload = {
        items: deriveOrderItems(selectedItems, {
          tipAmount,
          discountAmount,
          discountCode: appliedDiscountCode,
        }),
        cost: estimatedTotalWithTax,
        restaurant: deriveRestaurantName(numericRestaurantId),
        customer: user?.username || '',
        time: 0,
        cuisine: primaryCuisine,
      };

      const created = await createOrder(payload);
      navigate(`/orders/${created.id}`);
    } catch (err) {
      setError(err.message || 'Order creation failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="card">
      <h2>Order from restaurant #{restaurantId}</h2>
      <p>
        <Link to="/restaurants">Back to restaurant list</Link>
      </p>

      {isLoading && <p>Loading menu...</p>}
      {error && <p className="error">{error}</p>}

      {!isLoading && (
        <form onSubmit={submitOrder} className="form-grid">
          {checkoutStep === 'items' ? (
            <>
              <div className="menu-list">
                <h3>Menu</h3>
                {menuItems.length === 0 && <p>No menu items found.</p>}
                {menuItems.map((item) => {
                  const key = `${item.item_name}_${item.restaurant_id}`;
                  const isChecked = selectedItemKeys.includes(key);
                  return (
                    <label key={key} className="menu-row">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() => toggleItem(item)}
                      />
                      <span>
                        {item.item_name} - ${Number(item.cost || 0).toFixed(2)}
                      </span>
                    </label>
                  );
                })}
              </div>

              <p>
                <strong>Food subtotal:</strong> ${estimatedSubtotal.toFixed(2)}
              </p>

              <button
                type="button"
                onClick={continueToAdjustments}
                disabled={selectedItems.length === 0}
              >
                Continue to tip & discount
              </button>
            </>
          ) : (
            <>
              <div className="menu-list">
                <h3>Add tip and discount</h3>
                <p>
                  Tip is added on top of your food total. Discount codes are
                  applied to the food subtotal.
                </p>

                <label>
                  Tip amount ($)
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    value={tipAmountInput}
                    onChange={(event) => setTipAmountInput(event.target.value)}
                  />
                </label>

                <div className="inline-field">
                  <label>
                    Discount code
                    <input
                      type="text"
                      value={discountCodeInput}
                      onChange={(event) => {
                        const nextCode = event.target.value;
                        setDiscountCodeInput(nextCode);
                        if (
                          appliedDiscountCode &&
                          nextCode.trim() !== appliedDiscountCode
                        ) {
                          resetAppliedDiscount();
                        }
                      }}
                      placeholder="Enter code"
                    />
                  </label>
                  <button
                    type="button"
                    onClick={handleDiscountApply}
                    disabled={isApplyingDiscount || !discountCodeInput.trim()}
                  >
                    {isApplyingDiscount ? 'Applying...' : 'Apply code'}
                  </button>
                </div>

                {discountMessage && <p>{discountMessage}</p>}
              </div>

              <div className="menu-list">
                <h3>Order summary</h3>
                <p>
                  <strong>Food subtotal:</strong> ${estimatedSubtotal.toFixed(2)}
                </p>
                <p>
                  <strong>Discount:</strong> -${discountAmount.toFixed(2)}
                </p>
                <p>
                  <strong>Tip:</strong> +${tipAmount.toFixed(2)}
                </p>
                <p>
                  <strong>Adjusted subtotal:</strong> ${adjustedSubtotal.toFixed(2)}
                </p>
                <p>
                  <strong>Estimated total (incl. tax):</strong> $
                  {estimatedTotalWithTax.toFixed(2)}
                </p>
              </div>

              <div className="checkout-actions">
                <button
                  type="button"
                  onClick={() => setCheckoutStep('items')}
                  disabled={isSubmitting}
                >
                  Back to menu
                </button>
                <button type="submit" disabled={isSubmitting || isApplyingDiscount}>
                  {isSubmitting ? 'Placing order...' : 'Place order'}
                </button>
              </div>
            </>
          )}
        </form>
      )}
    </section>
  );
}
