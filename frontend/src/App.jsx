import React from 'react';
import NavBar from './components/NavBar';
import AuthProvider from './components/context/AuthContext';
import ResumeUpload from './components/ResumeUpload';
import ResumeAnalysisCard from './components/ResumeAnalysisCard';

export default function App() {
  return (
    <>
    <AuthProvider>
      <NavBar />
      <div style={{ padding: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
          <h1>Welcome to Resumate</h1>
          <p>Your AI-powered Resume companion, Feel free to use the website! Upload your Resume below to start!</p>
      </div>
    </AuthProvider>
    <ResumeUpload />
    </>  
);
}
