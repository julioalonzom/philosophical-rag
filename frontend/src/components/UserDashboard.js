// frontend/src/components/UserDashboard.js
import React from 'react';
import { useUser } from '../contexts/UserContext';

const UserDashboard = () => {
  const { user } = useUser();

  const handleUpgrade = async () => {
    const response = await fetch('/api/create-checkout-session', { method: 'POST' });
    const session = await response.json();
    const stripe = await loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);
    stripe.redirectToCheckout({ sessionId: session.id });
  };

  return (
    <div>
      <h2>Welcome, {user.username}!</h2>
      <p>Account Tier: {user.accountTier}</p>
      <p>Queries This Month: {user.queriesThisMonth}</p>
      {user.accountTier === 'free' && (
        <button onClick={handleUpgrade}>Upgrade to Premium</button>
      )}
    </div>
  );
};

export default UserDashboard;