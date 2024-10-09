import React from 'react';
import axios from 'axios';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY);

const StripeCheckout = () => {
  const handleClick = async () => {
    const stripe = await stripePromise;
    const response = await axios.post('/api/create-checkout-session');
    const session = response.data;
    const result = await stripe.redirectToCheckout({
      sessionId: session.id,
    });
    if (result.error) {
      console.error(result.error.message);
    }
  };

  return (
    <button onClick={handleClick}>
      Upgrade to Premium
    </button>
  );
};

export default StripeCheckout;