// ResumeAnalysisPage.jsx
import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import ResumeAnalysisCard from './ResumeAnalysisCard';
import './ResumeAnalysisPage.css'; // Optional: for full-page styling

export default function ResumeAnalysisPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const { info, feedback } = location.state || {};

  if (!info || !feedback) {
    return (
      <div className="analysis-wrapper">
        <h2>No data found for analysis.</h2>
        <button onClick={() => navigate('/')}>← Back to Upload</button>
      </div>
    );
  }

  return (
    <div className="analysis-wrapper">
      <ResumeAnalysisCard info={info} feedback={feedback} />
      <button className="back-button" onClick={() => navigate('/')}>
        ← Back
      </button>
    </div>
  );
}
