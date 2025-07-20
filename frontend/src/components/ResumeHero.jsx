// ResumeHero.jsx
import React from 'react';
import './ResumeHero.css';
import ResumeUpload from './ResumeUpload';
import img01 from '../assets/01.jpg'
import img02 from '../assets/02.jpg'

export default function ResumeHero() {
  return (
    <div>
      <div className="hero-wrapper">
        <div className="hero-left">
          <h2 className="section-tag">SCORE MY RESUME – FREE RESUME CHECKER</h2>
          <h1 className="hero-title">Get expert feedback on your resume, instantly</h1>
          <p className="hero-desc">
            Our free <strong>AI-powered</strong> resume checker scores your resume on key criteria recruiters and hiring managers look for. 
            Get actionable steps to revamp your resume and <strong>land more interviews</strong>.
          </p>
          <p className="hero-desc">
            Upload your <strong>resume</strong> and uncover what hiring managers and recruiters are really looking for.
          </p>
          <p className="hero-desc">
            Find missing <strong>skills</strong>, improve <strong>structure</strong>, and boost your chances of landing <strong>interviews</strong> — instantly and for free.
          </p>
          <ResumeUpload />
        </div>

        <div className="hero-right">
          <img
            src="https://imgs.search.brave.com/6PO2q85-TPlAxJMwriSInD6mfsvhAg3smrDBYvs3Uiw/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly9lbmhh/bmN2LmNvbS9fbmV4/dC9zdGF0aWMvaW1h/Z2VzL2F0cy1jaGVj/a2VyLXNhZmFyaS1l/ZWY2YmNjNjRkZjM0/MWExMjJhMjNmZjY4/OTA0NThmOC5zdmc"
            alt="Resume Preview"
            className="floating-image"
          />
        </div>
      </div>

      {/* ✨ Feature Section Starts */}
      <div className="feature-section">
        <div className="feature-box">
          <div className="feature-text">
            <h2>Smart resume suggestions and examples from top resumes</h2>
            <p>
              We recognise how tough it can be to put your experiences into concise, effective lines.
              Our AI transforms your old lines into polished, professional bullet points — just like the top 1% of resumes.
            </p>
          </div>
          <div className="feature-image">
            <img src={img01} alt="Smart Resume Suggestions" />
          </div>
        </div>

        <div className="feature-box reverse">
          <div className="feature-text">
            <h2>The most advanced resume checker, powered by AI</h2>
            <p>
              Beyond basic spell checking — we analyze impact, keyword density, clarity, and check your style and brevity.
              Each line is scored with data recruiters care about.
            </p>
          </div>
          <div className="feature-image">
            <img src={img02} alt="AI Resume Checker" />
          </div>
        </div>
      </div>
    </div>
  );
}
