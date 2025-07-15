import React, { useState, useContext } from 'react';
import './AuthModal.css';
import { FaGoogle, FaGithub } from 'react-icons/fa';
import { AuthContext } from '../context/AuthContext'; // adjust path if needed
import axios from 'axios';

export default function AuthModal({ onClose }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ email: '', password: '', username: '' });
  const [error, setError] = useState(null);
  const { login } = useContext(AuthContext);

  const toggleForm = () => {
    setError(null);
    setIsLogin(!isLogin);
  };

  const handleChange = (e) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      if (isLogin) {
          const res = await axios.post('http://127.0.0.1:8000/api/login/', {
          email: formData.email,
          password: formData.password,
       });

        login({ user: res.data.user, token: res.data.token }); // ✅ FIXED
        onClose();
        } else {
              await axios.post('http://127.0.0.1:8000/api/register/', {
              email: formData.email,
              username: formData.username,
              password: formData.password,
        });

        const loginRes = await axios.post('http://127.0.0.1:8000/api/login/', {
        email: formData.email,
        password: formData.password,
        });

        login({ user: loginRes.data.user, token: loginRes.data.token }); // ✅ FIXED
        onClose();
      }
    } catch (err) {
      console.error("❌ Auth Error:", err.response?.data);
      const data = err.response?.data;
      if (data?.email) {
        setError(data.email[0]);
      } else if (data?.username) {
        setError(data.username[0]);
      } else if (data?.password) {
        setError(data.password[0]);
      } else if (data?.detail) {
        setError(data.detail);
      } else {
        setError("Something went wrong. Try again.");
      }
    }
  };

  const handleSocialLogin = (provider) => {
    alert(`Logging in with ${provider}...`);
  };

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <h2>{isLogin ? 'Login' : 'Sign Up'}</h2>

        <div className="auth-social">
          <button onClick={() => handleSocialLogin('Google')} className="social-btn google">
            <FaGoogle className="icon" />
            Continue with Google
          </button>
          <button onClick={() => handleSocialLogin('GitHub')} className="social-btn github">
            <FaGithub className="icon" />
            Continue with GitHub
          </button>
        </div>

        <div className="auth-divider">or</div>

        <form onSubmit={handleSubmit}>
          {!isLogin && (
            <input
              type="text"
              name="username"
              placeholder="Username"
              required
              value={formData.username}
              onChange={handleChange}
            />
          )}
          <input
            type="email"
            name="email"
            placeholder="Email"
            required
            value={formData.email}
            onChange={handleChange}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            required
            value={formData.password}
            onChange={handleChange}
          />
          <button type="submit">{isLogin ? 'Login' : 'Sign Up'}</button>
        </form>

        {error && <p className="auth-error">{error}</p>}

        <p>
          {isLogin ? "Don't have an account?" : "Already have an account?"}{' '}
          <span className="auth-switch" onClick={toggleForm}>
            {isLogin ? 'Sign Up' : 'Login'}
          </span>
        </p>
      </div>
    </div>
  );
}

