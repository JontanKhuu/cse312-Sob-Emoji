import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:5000/login', { email, password });
      localStorage.setItem('token', res.data.access_token);
      setMessage('✅ Logged in successfully!');
    } catch (err) {
      setMessage('❌ Login failed: Invalid credentials');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1 className="App-title">CSE 312 GAME IDEA</h1>
        <div className="nav-buttons">
          <button className="nav-button" onClick={() => { setShowRegister(false); setShowLogin(false); setShowRegister(true); }}>Register</button>
          <button className="nav-button" onClick={() => { setShowRegister(false); setShowLogin(false); setShowLogin(true); }}>Login</button>
        </div>
      </header>

      <main className="App-main">
        <p className="placeholder">Video Game goes :) here!</p>

        {showLogin && (
          <form onSubmit={handleLogin} className="auth-form">
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
            <button type="submit" className="auth-button">Login</button>
          </form>
        )}

        {showRegister && (
          <form onSubmit={(e) => e.preventDefault()} className="auth-form">
            <input className="auth-input" type="text" placeholder="Username" required />
            <input className="auth-input" type="email" placeholder="Email" required />
            <input className="auth-input" type="password" placeholder="Password" required />
            <button type="submit" className="auth-button">Register</button>
          </form>
        )}

        {message && <p className="auth-message">{message}</p>}
      </main>
    </div>
  );
}

export default App;