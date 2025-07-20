import React, { useState, useContext } from 'react';
import './Navbar.css';
import AuthModal from './AuthModal/AuthModal';
import { AuthContext } from './context/AuthContext';

export default function Navbar() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalType, setModalType] = useState('login');
  const [menuOpen, setMenuOpen] = useState(false); // 🌟 for mobile menu toggle

  const { user, logout } = useContext(AuthContext);

  const openModal = (type) => {
    setModalType(type);
    setIsModalOpen(true);
    setMenuOpen(false); // Close menu on modal open (optional)
  };

  const closeModal = () => setIsModalOpen(false);

  const toggleMenu = () => setMenuOpen(!menuOpen); // 🌟 toggle handler

  return (
    <>
      <nav className="navbar">

        <div className="navbar__toggle" onClick={toggleMenu}>
          <span className="bar"></span>
          <span className="bar"></span>
          <span className="bar"></span>
        </div>
        
        <div className="navbar__logo">ResuMate</div>

        {/* 🌟 Responsive Nav Links */}
        <div className={`navbar__links ${menuOpen ? 'open' : ''}`}>
          <a href="/">Home</a>
          <a href="#how-it-works">How It Works</a>
          <a href="#features">Features</a>
          <a href="#contact">Contact</a>

          <div className="navbar__auth-buttons">
            {user ? (
              <>
                <span className="welcome-user">
                  Hello, <strong>{user.username}</strong>
                </span>
                <button className="logout-btn" onClick={logout}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <button className="login-btn" onClick={() => openModal('login')}>
                  Login
                </button>
                <button className="signup-btn" onClick={() => openModal('signup')}>
                  Sign Up
                </button>
              </>
            )}
          </div>
        </div>

        {/* 🌟 Hamburger Toggle (Fixed) */}
      </nav>

      {/* Auth Modal */}
      {isModalOpen && <AuthModal onClose={closeModal} initialMode={modalType} />}
    </>
  );
}
