// components/Loading.jsx
import React from 'react';
import Lottie from 'lottie-react';
import Loading from '../assets/loading.json'; // Your Lottie JSON file

export default function Loading() {
  return (
    <div style={{ display: 'flex', justifyContent: 'center', marginTop: '2rem' }}>
      <Lottie animationData={animationData} loop={true} style={{ height: 200 }} />
    </div>
  );
}
