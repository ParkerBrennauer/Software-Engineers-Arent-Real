import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { loginUser } from '../lib/api';
import { useAuth } from '../state/AuthContext';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const navigate = useNavigate();
  const location = useLocation();
  const { setUser } = useAuth();

  const redirectPath = location.state?.from?.pathname || '/restaurants';

  const onSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const response = await loginUser({ username, password });
      setUser({
        id: response.id,
        username,
        requires2fa: Boolean(response.requires_2fa),
      });
      navigate(redirectPath, { replace: true });
    } catch (err) {
      setError(err.message || 'Login failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="card">
      <h2>Login</h2>
      <p>Sign in to browse restaurants and create orders.</p>
      <form onSubmit={onSubmit} className="form-grid">
        <label>
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            required
          />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </label>
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Logging in...' : 'Login'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      <p>
        Need an account? <Link to="/register">Register here</Link>.
      </p>
    </section>
  );
}
