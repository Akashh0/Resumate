// Footer.jsx
import React from 'react';
import './Footer.css';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">
          <h2>ResuMate</h2>
          <p>AI-powered resume analysis to help you stand out.</p>
        </div>

        <div className="footer-links">
          <a href="#">Home</a>
          <a href="#">Upload</a>
          <a href="#">Features</a>
          <a href="#">About</a>
          <a href="#">Contact</a>
        </div>

        <div className="footer-bottom">
          <p>© {new Date().getFullYear()} ResuMate. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}
