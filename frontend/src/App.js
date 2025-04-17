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
        <h1 className="App-title">😭CSE 312 GAME IDEA</h1>

        <div className = "login-div">
          <div className="nav-buttons">
            <button className="nav-button nav-button-register" onClick={() => {
                setShowRegister(false); setShowLogin(false); setShowRegister(true);
                // Make the button appear visibly depressed
                var x = document.getElementsByClassName("nav-button-register");
                for (var i = 0; i < x.length; i++) {
                  x[i].style.background = "rgb(110, 110, 110)";
                }
                var x = document.getElementsByClassName("nav-button-login");
                for (var i = 0; i < x.length; i++) {
                  x[i].style.background = "rgb(140, 140, 140)";
                }
            }}>Register</button>
            <button className="nav-button nav-button-login" onClick={() => { setShowRegister(false); setShowLogin(false); setShowLogin(true);
              // Make the button appear visibly depressed
              var x = document.getElementsByClassName("nav-button-login");
              for (var i = 0; i < x.length; i++) {
                x[i].style.background = "rgb(110, 110, 110)";
              }
              var x = document.getElementsByClassName("nav-button-register");
              for (var i = 0; i < x.length; i++) {
                x[i].style.background = "rgb(140, 140, 140)";
              }
            }}>Login</button>
          </div>

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
        </div>

      </header>

      <main className="App-main">
        <p className="placeholder">Video Game goes here! :)</p>

        {message && <p className="auth-message">{message}</p>}
      </main>
    </div>
  );
}

export default App;