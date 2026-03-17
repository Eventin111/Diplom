import React, { createContext, useState, useEffect } from 'react';
import { appConfig } from '../config/appConfig';
import { initializeAuthSession } from '../core/application/usecases/initializeAuthSession';
import { loginUser } from '../core/application/usecases/loginUser';
import { logoutUser } from '../core/application/usecases/logoutUser';
import { registerUser } from '../core/application/usecases/registerUser';
import { createMockAuthRepository } from '../core/infrastructure/repositories/mockAuthRepository';

const AuthContext = createContext();
const authRepository = createMockAuthRepository();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const authKeys = appConfig.authStorageKeys;

  useEffect(() => {
    const initAuth = async () => {
      try {
        const session = await initializeAuthSession(authRepository);

        if (session.user) {
          setUser(session.user);
          setIsAuthenticated(true);
        }
      } catch (err) {
        console.error('Auth init error:', err);
        clearAuth();
      } finally {
        setTimeout(() => {
          setLoading(false);
        }, appConfig.authInitDelayMs);
      }
    };

    void initAuth();
  }, []);

  const clearAuth = () => {
    authRepository.logout();
    setUser(null);
    setIsAuthenticated(false);
  };

  const login = async (email, password) => {
    const session = await loginUser(authRepository, { email, password });
    setUser(session.user);
    setIsAuthenticated(true);
    return session.user;
  };

  const logout = async () => {
    await logoutUser(authRepository);
    setUser(null);
    setIsAuthenticated(false);
    window.location.href = '/login';
  };

  const register = async (email, password, username) => {
    const session = await registerUser(authRepository, { email, password, username });
    setUser(session.user);
    setIsAuthenticated(true);
    return session.user;
  };

  const updateUserProfile = (partialUser) => {
    if (!user) {
      return null;
    }

    const nextUser = { ...user, ...partialUser };
    setUser(nextUser);

    localStorage.setItem(authKeys.user, JSON.stringify(nextUser));

    const rawRegisteredUsers = localStorage.getItem(authKeys.registeredUsers);
    if (rawRegisteredUsers) {
      try {
        const parsed = JSON.parse(rawRegisteredUsers);
        if (Array.isArray(parsed)) {
          const updatedUsers = parsed.map((item) => {
            if (String(item.email || '').toLowerCase() === String(nextUser.email || '').toLowerCase()) {
              return { ...item, ...nextUser };
            }
            return item;
          });
          localStorage.setItem(authKeys.registeredUsers, JSON.stringify(updatedUsers));
        }
      } catch (error) {
        // ignore malformed storage
      }
    }

    return nextUser;
  };

  return (
    <AuthContext.Provider value={{ 
      isAuthenticated, 
      user, 
      loading, 
      login, 
      logout, 
      register,
      clearAuth,
      updateUserProfile
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export { AuthContext };
