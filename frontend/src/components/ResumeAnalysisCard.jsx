import React from 'react';
import './ResumeAnalysisCard.css';
import { CheckCircle, AlertCircle } from 'lucide-react';

export default function ResumeAnalysisCard({ info = {}, feedback = [] }) {
  const {
    name = 'Not Found',
    email = [],
    phone = [],
    skills = [],
    education = 'Not Found',
  } = info;

  return (
    <div className="resume-card">
      <h2 className="title">🔍 Resume Analysis</h2>

      <div className="section">
        <h3 className="subtitle">📄 Extracted Info</h3>
        <ul>
          <li><strong>Name:</strong> {name}</li>
          <li><strong>Email:</strong> {email[0] || 'Not Found'}</li>
          <li><strong>Phone:</strong> {phone[0] || 'Not Found'}</li>
          <li><strong>Skills:</strong> {skills.length ? skills.join(', ') : 'None'}</li>
          <li><strong>Education Mentioned:</strong> {education}</li>
        </ul>
      </div>

      <div className="section">
        <h3 className="subtitle">💬 Feedback</h3>
        <ul>
          {feedback.length > 0 ? feedback.map((point, i) => (
            <li key={i} className={point.toLowerCase().includes("missing") || point.toLowerCase().includes("unclear") ? "warn" : "ok"}>
              {point.toLowerCase().includes("missing") || point.toLowerCase().includes("unclear") 
                ? <AlertCircle size={16} className="icon warn-icon" />
                : <CheckCircle size={16} className="icon ok-icon" />}
              <span>{point}</span>
            </li>
          )) : <li>No feedback available.</li>}
        </ul>
      </div>
    </div>
  );
}
