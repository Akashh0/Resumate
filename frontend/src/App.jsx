import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import AuthProvider from './components/context/AuthContext';
import ResumeUpload from './components/ResumeUpload';
import ResumeHero from './components/ResumeHero';
import ResumeAnalysisPage from './components/ResumeAnalysisPage'; // ✅ Use this as a page
import Footer from '../Footer';

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <NavBar />
        <Routes>
          <Route path="/" element={<ResumeHero />} />
          <Route path="/upload" element={<ResumeUpload />} />
          <Route path="/analysis" element={<ResumeAnalysisPage />} /> 
        </Routes>
        <Footer />
      </Router>
    </AuthProvider>
  );
}
