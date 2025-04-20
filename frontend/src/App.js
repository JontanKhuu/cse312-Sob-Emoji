import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('username');
    if (token && savedUser) {
      setIsLoggedIn(true);
      setCurrentUser(savedUser);
    }
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/login', { username, password });
      localStorage.setItem('token', res.data.token || 'token-placeholder');
      localStorage.setItem('username', username);
      setIsLoggedIn(true);
      setCurrentUser(username);
      setMessage('✅ Logged in successfully!');
      setUsername('');
      setPassword('');
      setShowLogin(false);
      setShowRegister(false);
    } catch (err) {
      setMessage('❌ Login failed: Invalid credentials');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('/api/register', { username, password });
      setMessage('✅ Registered successfully! Please login.');
      setUsername('');
      setPassword('');
      setEmail('');
      setShowRegister(false);
      setShowLogin(true);
    } catch (err) {
      const errorMsg = err.response?.data?.message || 'Unknown error';
      setMessage(`❌ Registration failed: ${errorMsg}`);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setIsLoggedIn(false);
    setCurrentUser('');
    setMessage('Logged out!');
    setShowLogin(false);
    setShowRegister(false);
  };

  const setActiveButtonStyle = (btn) => {
    const loginBtn = document.querySelector('.nav-button-login');
    const registerBtn = document.querySelector('.nav-button-register');
    if (btn === 'login') {
      loginBtn.style.background = 'rgb(110, 110, 110)';
      registerBtn.style.background = 'rgb(140, 140, 140)';
    } else {
      loginBtn.style.background = 'rgb(140, 140, 140)';
      registerBtn.style.background = 'rgb(110, 110, 110)';
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="App-title">😭 CSE 312 GAME IDEA</h1>

        {isLoggedIn ? (
          <div className="login-status">
            <p className="auth-message">✅ Logged in as <strong>{currentUser}</strong></p>
            <button className="auth-button" onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <div className="login-div">
            <div className="nav-buttons">
              <button className="nav-button nav-button-register" onClick={() => {
                setShowRegister(true);
                setShowLogin(false);
                setActiveButtonStyle('register');
              }}>Register</button>

              <button className="nav-button nav-button-login" onClick={() => {
                setShowRegister(false);
                setShowLogin(true);
                setActiveButtonStyle('login');
              }}>Login</button>
            </div>

            {showLogin && (
              <form onSubmit={handleLogin} className="auth-form">
                <input
                  className="auth-input"
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
                <input
                  className="auth-input"
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button type="submit" className="auth-button">Login</button>
              </form>
            )}

            {showRegister && (
              <form onSubmit={handleRegister} className="auth-form">
                <input
                  className="auth-input"
                  type="text"
                  placeholder="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
                <input
                  className="auth-input"
                  type="email"
                  placeholder="Email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
                <input
                  className="auth-input"
                  type="password"
                  placeholder="Password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
                <button type="submit" className="auth-button">Register</button>
              </form>
            )}
          </div>
        )}
      </header>

      <main className="App-main">
        <p className="placeholder">Video Game goes here! :)</p>
        {message && <p className="auth-message">{message}</p>}
      </main>
    </div>
  );
}

export default App;
