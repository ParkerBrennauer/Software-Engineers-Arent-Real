import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { registerCustomer } from '../lib/api';

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: '',
    email: '',
    username: '',
    password: '',
    paymentType: 'credit card',
    paymentDetails: '',
  });
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();

  const updateField = (key, value) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await registerCustomer(form);
      navigate('/login', {
        replace: true,
        state: { successMessage: 'Registration complete. Please log in.' },
      });
    } catch (err) {
      setError(err.message || 'Registration failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="card">
      <h2>Create account</h2>
      <p>Register as a customer so you can sign in and place orders.</p>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          Full name
          <input
            value={form.name}
            onChange={(event) => updateField('name', event.target.value)}
            required
          />
        </label>
        <label>
          Email
          <input
            type="email"
            value={form.email}
            onChange={(event) => updateField('email', event.target.value)}
            required
          />
        </label>
        <label>
          Username
          <input
            value={form.username}
            onChange={(event) => updateField('username', event.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={form.password}
            onChange={(event) => updateField('password', event.target.value)}
            required
          />
        </label>
        <label>
          Payment type
          <select
            value={form.paymentType}
            onChange={(event) => updateField('paymentType', event.target.value)}
          >
            <option value="credit card">Credit card</option>
            <option value="debit card">Debit card</option>
          </select>
        </label>
        <label>
          Card number (15 or 16 digits)
          <input
            inputMode="numeric"
            value={form.paymentDetails}
            onChange={(event) => updateField('paymentDetails', event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Registering...' : 'Register'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      <p>
        Already registered? <Link to="/login">Go to login</Link>.
      </p>
    </section>
  );
}
