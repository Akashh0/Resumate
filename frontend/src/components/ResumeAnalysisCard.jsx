import React from 'react';
import './ResumeAnalysisCard.css';
import { CheckCircle, AlertCircle, CircleAlert, BadgeCheck } from 'lucide-react';

export default function ResumeAnalysisCard({
  info = {},
  feedback = [],
  score = 100,
  alignment = "",
  issues = []
}) {
  const {
    name = 'Not Found',
    email = [],
    phone = [],
    skills = [],
    education = 'Not Found',
  } = info;

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981';      // green
    if (score >= 60) return '#facc15';      // yellow
    return '#ef4444';                       // red
  };

  return (
    <div className="analysis-container">
      {/* Resume Score */}
      <div className="score-box">
        <h2 className="score-title">Resume Score</h2>
        <div
          className="score-circle"
          style={{ borderColor: getScoreColor(score) }}
        >
          {score}%
        </div>
      </div>

      {/* Extracted Info */}
      <div className="info-section">
        <h3 className="section-title">📄 Extracted Information</h3>
        <ul>
          <li><strong>Name:</strong> {name}</li>
          <li><strong>Email:</strong> {email[0] || 'Not Found'}</li>
          <li><strong>Phone:</strong> {phone[0] || 'Not Found'}</li>
          <li><strong>Skills:</strong> {skills.length ? skills.join(', ') : 'None'}</li>
          <li><strong>Education:</strong> {education}</li>
        </ul>
      </div>

      {/* Career Alignment */}
      <div className="alignment-box">
        <h3 className="section-title">🎯 Role Alignment</h3>
        <p>{alignment}</p>
      </div>

      {/* Issues Section */}
      <div className="issues-section">
        <h3 className="section-title">⚠️ Issues & Suggestions</h3>
        {issues.length > 0 ? (
          <ul>
            {issues.map((issue, idx) => (
              <li key={idx} className={`issue ${issue.type}`}>
                {issue.type === 'critical' ? <CircleAlert size={18} /> :
                 issue.type === 'moderate' ? <AlertCircle size={18} /> :
                 <CheckCircle size={18} />}
                <div>
                  <p className="issue-title">{issue.title}</p>
                  <p className="issue-desc">{issue.description}</p>
                </div>
              </li>
            ))}
          </ul>
        ) : (
          <p className="no-issues">✅ No major issues found.</p>
        )}
      </div>

      {/* Feedback Summary */}
      <div className="feedback-section">
        <h3 className="section-title">💬 Feedback Summary</h3>
        <ul>
          {feedback.length > 0 ? feedback.map((point, i) => (
            <li key={i} className="feedback-item">
              <BadgeCheck size={16} /> {point}
            </li>
          )) : <li>No feedback available.</li>}
        </ul>
      </div>
    </div>
  );
}
