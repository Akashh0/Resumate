
import axios from 'axios';

axios.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      window.location.reload(); // logout on unauthorized
    }
    return Promise.reject(err);
  }
);
