import React, { useState } from 'react';
import './ResumeUpload.css';
import { useNavigate } from 'react-router-dom';
import { Player } from '@lottiefiles/react-lottie-player';
import loadingAnimation from '../assets/loading.json';

export default function ResumeUpload({ onFileUpload }) {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === 'dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const droppedFile = e.dataTransfer.files[0];
    validateFile(droppedFile);
  };

  const handleChange = (e) => {
    const selectedFile = e.target.files[0];
    validateFile(selectedFile);
  };

  const validateFile = (file) => {
    if (!file) return;

    const isValid =
      file.type === 'application/pdf' ||
      file.name.toLowerCase().endsWith('.docx');

    if (!isValid) {
      alert('Please upload only PDF or DOCX files!');
      return;
    }

    setFile(file);
    uploadToBackend(file);
    if (onFileUpload) onFileUpload(file);
  };

  const uploadToBackend = (file) => {
    const token = localStorage.getItem('token');
    if (!token) {
      alert("You must be logged in to upload a resume.");
      return;
    }

    const formData = new FormData();
    formData.append('resume', file);
    setLoading(true);

    fetch('http://127.0.0.1:8000/api/upload-resume/', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        setLoading(false);
        if (data.text) {
          navigate('/analysis', {
            state: {
              info: data.info || {},
              feedback: data.feedback || [],
              score: data.score || 0,
              alignment: data.alignment || '',
              issues: data.issues || [],
              suggestions: data.improvementTips || [],
              positives: data.strengths || [],
              scoreReview: data.scoreReview || '',
            },
          });
        } else {
          alert(data.error || "Something went wrong while parsing.");
        }
      })
      .catch((err) => {
        setLoading(false);
        console.error("❌ Upload Error:", err);
        alert("Upload failed. Please try again.");
      });
  };

  const removeFile = () => {
    setFile(null);
    if (onFileUpload) onFileUpload(null);
  };

  return (
    <>
      <div
        className={`upload-container ${dragActive ? 'drag-active' : ''}`}
        onDragOver={handleDrag}
        onDragLeave={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="upload-input"
          accept=".pdf,.docx"
          onChange={handleChange}
          hidden
        />
        <label htmlFor="upload-input" className="upload-label">
          {!file ? (
            <div className="upload-content">
              <p>Drag & Drop your resume here</p>
              <p className="or">or</p>
              <p>Click Anywhere to Upload your Resume!!</p>
            </div>
          ) : (
            <div className="file-display">
              <span className="file-name">📄 {file.name}</span>
              <button
                type="button"
                className="remove-btn"
                onClick={removeFile}
                aria-label="Remove file"
              >
                &times;
              </button>
            </div>
          )}
        </label>
      </div>

      {loading && (
        <div className="lottie-loader">
          <Player
            autoplay
            loop
            src={loadingAnimation}
            style={{ height: '200px', width: '200px' }}
          />
          <p>Analyzing your resume...</p>
        </div>
      )}
    </>
  );
}
