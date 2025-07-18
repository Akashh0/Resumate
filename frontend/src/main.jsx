import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import AuthContext from './components/context/AuthContext.jsx'
import './api/axiosSetup.js'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <AuthContext>
      <App />
    </AuthContext>
  </React.StrictMode>
);
