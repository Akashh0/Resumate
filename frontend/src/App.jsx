import React from 'react';
import NavBar from './components/NavBar';
import AuthProvider from './components/context/AuthContext';
import ResumeUpload from './components/ResumeUpload';
import Title from './Title';
import ResumeHero from './components/ResumeHero';

export default function App() {
  return (
    <>
    <AuthProvider>
      <NavBar />
      <ResumeHero />
    </AuthProvider>
    </>  
);
}
