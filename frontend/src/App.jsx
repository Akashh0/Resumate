import React from 'react';
import NavBar from './components/NavBar';
import AuthProvider from './components/context/AuthContext';
import ResumeUpload from './components/ResumeUpload';
import Title from './Title';

export default function App() {
  return (
    <>
    <AuthProvider>
      <NavBar />
      <Title />
    </AuthProvider>
    <ResumeUpload />
    </>  
);
}
