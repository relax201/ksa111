import React, { createContext, useContext, useState, useCallback } from 'react';
import axios from 'axios';
import { API_URL } from '../utils/constants';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is authenticated
  const checkAuth = useCallback(async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        setIsAuthenticated(false);
        setUser(null);
        setLoading(false);
        return;
      }
      
      const response = await axios.get(`${API_URL}/user`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data.status === 'success') {
        setUser(response.data.data);
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('token');
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check error:', error);
      localStorage.removeItem('token');
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // Login user
  const login = async (email, password) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/auth/login`, {
        email,
        password
      });
      
      if (response.data.status === 'success') {
        localStorage.setItem('token', response.data.token);
        setUser(response.data.user);
        setIsAuthenticated(true);
        return true;
      } else {
        setError(response.data.message || 'فشل تسجيل الدخول');
        return false;
      }
    } catch (error) {
      console.error('Login error:', error);
      setError(error.response?.data?.message || 'حدث خطأ أثناء تسجيل الدخول');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Register user
  const register = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/auth/register`, userData);
      
      if (response.data.status === 'success') {
        localStorage.setItem('token', response.data.token);
        setUser(response.data.user);
        setIsAuthenticated(true);
        return true;
      } else {
        setError(response.data.message || 'فشل إنشاء الحساب');
        return false;
      }
    } catch (error) {
      console.error('Register error:', error);
      setError(error.response?.data?.message || 'حدث خطأ أثناء إنشاء الحساب');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout user
  const logout = async () => {
    try {
      const token = localStorage.getItem('token');
      
      if (token) {
        await axios.post(`${API_URL}/auth/logout`, {}, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  // Update user profile
  const updateProfile = async (userData) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem('token');
      
      const response = await axios.put(`${API_URL}/user/profile`, userData, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data.status === 'success') {
        setUser(response.data.data);
        return true;
      } else {
        setError(response.data.message || 'فشل تحديث الملف الشخصي');
        return false;
      }
    } catch (error) {
      console.error('Update profile error:', error);
      setError(error.response?.data?.message || 'حدث خطأ أثناء تحديث الملف الشخصي');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Reset password request
  const resetPasswordRequest = async (email) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_URL}/auth/password/email`, {
        email
      });
      
      if (response.data.status === 'success') {
        return true;
      } else {
        setError(response.data.message || 'فشل إرسال طلب إعادة تعيين كلمة المرور');
        return false;
      }
    } catch (error) {
      console.error('Reset password request error:', error);
      setError(error.response?.data?.message || 'حدث خطأ أثناء طلب إعادة تعيين كلمة المرور');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    checkAuth,
    login,
    register,
    logout,
    updateProfile,
    resetPasswordRequest
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};