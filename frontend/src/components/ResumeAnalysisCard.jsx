import React from 'react';
import './ResumeAnalysisCard.css';
import {
  CheckCircle,
  AlertCircle,
  CircleAlert,
  BadgeCheck
} from 'lucide-react';
import { useLocation } from 'react-router-dom';

export default function ResumeAnalysisCard() {
  const { state } = useLocation();

  if (!state) return <p>No analysis data found. Please upload a resume first.</p>;

  const {
    info = {},
    score = 0,
    alignment = '',
    feedback = [],
    issues = [],
    suggestions = [],
    positives = [],
    wordCount = 0,
    skillsCount = 0,
    hasGitHub = false,
    emailCount = 0,
    phoneCount = 0,
    nameFound = false,
    educationFound = false,
    objective = '',
    experience = '',
    certifications = [],
    achievements = [],
    languages = [],
    linkedinFound = false,
    projectsMentioned = false,
  } = state;

  const {
    name = 'Not Found',
    email = [],
    phone = [],
    skills = [],
    education = 'Not Found',
    softSkills = [],
  } = info;

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#facc15'; // yellow
    return '#ef4444'; // red
  };

  return (
    <div className="analysis-container">
      {/* Score */}
      <div className="score-box">
        <h2 className="score-title">Resume Score</h2>
        <div className="score-bar-container">
          <div
            className="score-bar"
            style={{ width: `${score}%`, backgroundColor: getScoreColor(score) }}
          />
        </div>
        <p className="score-percent">{score}%</p>
        <p className="score-review">
          {score >= 80
            ? "Excellent resume! You're nearly job-ready."
            : score >= 60
              ? "Decent resume. Some polishing needed."
              : "Resume needs significant improvements to stand out."}
        </p>
      </div>

      {/* Extracted Information */}
      <div className="info-section">
        <h3 className="section-title">📄 Extracted Information</h3>
        <ul>
          <li><strong>Name:</strong> {name}</li>
          <li><strong>Email:</strong> {email[0] || 'Not Found'}</li>
          <li><strong>Phone:</strong> {phone[0] || 'Not Found'}</li>
          <li><strong>Word Count:</strong> {wordCount}</li>
          <li><strong>Education:</strong> {educationFound ? "✅ Yes" : "❌ No"}</li>
          <li><strong>Skills:</strong> {Array.isArray(skills) ? skills.join(', ') : 'None'}</li>
          <li><strong>Certifications:</strong> {
          Array.isArray(certifications)
          ? (certifications.length > 0 ? '✅ Yes' : '❌ No')
          : '❌ No'
          }</li>
          <li><strong>Experience:</strong> {
          Array.isArray(experience)
          ? (experience.length > 0 ? experience.join(', ') : 'None')
          : (experience || 'None')
          }</li>
          <li><strong>Projects Mentioned:</strong> {projectsMentioned ? "✅ Yes" : "❌ No"}</li>
          <li><strong>Achievements:</strong> {
          Array.isArray(achievements)
          ? (achievements.length > 0 ? '✅ Yes' : '❌ No')
          : (achievements && achievements !== 'Not Found' ? '✅ Yes' : '❌ No')
          }</li>
          <li><strong>GitHub:</strong> {hasGitHub ? "✅ Yes" : "❌ No"}</li>
          <li><strong>LinkedIn:</strong> {linkedinFound ? "✅ Yes" : "❌ No"}</li>
          <li><strong>Languages:</strong> {languages.join(', ') || 'Not Mentioned'}</li>
        </ul>
      </div>

      {/* Role Alignment */}
      <div className="alignment-box">
        <h3 className="section-title">🎯 Role Alignment</h3>
        <p>{alignment || 'Not available'}</p>
      </div>

      {/* Issues & Suggestions */}
      <div className="issues-section">
        <h3 className="section-title">⚠️ Issues & Suggestions</h3>
        {issues.length > 0 ? (
          <ul>
            {issues.slice(0, 3).map((issue, idx) => (
              <li key={idx} className={`issue ${issue.type}`}>
                {issue.type === 'critical' ? (
                  <CircleAlert size={18} />
                ) : issue.type === 'moderate' ? (
                  <AlertCircle size={18} />
                ) : (
                  <CheckCircle size={18} />
                )}
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
        {issues.length > 3 && <button className="show-more">Show More</button>}
      </div>

      {/* Feedback */}
      <div className="feedback-section">
        <h3 className="section-title">💬 Feedback Summary</h3>
        <ul>
          {feedback.length > 0 ? (
            feedback.map((point, i) => (
              <li key={i} className="feedback-item">
                <BadgeCheck size={16} /> {point}
              </li>
            ))
          ) : (
            <li>No feedback available.</li>
          )}
        </ul>
      </div>

      {/* Positives */}
      <div className="positives-section">
        <h3 className="section-title">✨ Strengths in Your Resume</h3>
        <ul>
          {skills.length >= 3 && <li><CheckCircle size={16} /> Good technical skill set listed.</li>}
          {emailCount > 0 && <li><CheckCircle size={16} /> Valid email found.</li>}
          {nameFound && <li><CheckCircle size={16} /> Name is clearly visible.</li>}
          {educationFound && <li><CheckCircle size={16} /> Education section present.</li>}
        </ul>
      </div>
    </div>
  );
}
