import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import { io } from 'socket.io-client';

function App() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUser, setCurrentUser] = useState('');
  const [inGame, setInGame] = useState(false);
  const [socket, setSocket] = useState(null);
  const [players, setPlayers] = useState([]);
  const [foods, setFoods] = useState([]);
  const [gameOver, setGameOver] = useState(false);
  const [winner, setWinner] = useState('');

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
      localStorage.setItem('token', res.data.token);
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
      await axios.post('/api/register', { username, password });
      setMessage('✅ Registered successfully! Please login.');
      setUsername('');
      setPassword('');
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
    if (socket) {
      socket.disconnect();
    }
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
  const handleAvatarUpload = async (event) => {
    const file = event.target.files[0];
    console.log("Selected file:", file);
    if (!file) return;
    
    const formData = new FormData();
    formData.append('avatar', file);
    formData.append('username', currentUser);
  
    try {
      const res = await axios.post('/api/upload-avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage('✅ Avatar uploaded successfully!');
    } catch (err) {
      setMessage('❌ Failed to upload avatar');
    }
  };
  
  const endGame = () => {
    if (socket) {
      socket.emit('force_end_game'); // Force backend to end
    }
  };

  const handleJoinGame = () => {
    const newSocket = io();
    setSocket(newSocket);
    setInGame(true);

    newSocket.emit('join_game', { username: currentUser });

    newSocket.on('game_update', (data) => {
      setPlayers(data.players);
      setFoods(data.foods);
    });

    newSocket.on('game_over', (data) => {
      setWinner(data.winner ? `${data.winner} (Score: ${data.score})` : "No one");
      setGameOver(true);
      setInGame(false);
      newSocket.disconnect();
    });

    newSocket.on('connect', () => {
      console.log('✅ Connected to game WebSocket');
    });

    newSocket.on('disconnect', () => {
      console.log('⚡ Disconnected');
    });

    newSocket.emit('start_game');

    setTimeout(() => {
      endGame();
    }, 60000); // 120 seconds = 2 minutes
  };

  const returnToHome = () => {
    setInGame(false);
    setGameOver(false);
    setPlayers([]);
    setFoods([]);
    setWinner('');
    setSocket(null);
  };

  useEffect(() => {
    if (!socket) return;

    const handleKeyDown = (e) => {
      let direction = null;
      if (e.key === 'w') direction = 'up';
      if (e.key === 'a') direction = 'left';
      if (e.key === 's') direction = 'down';
      if (e.key === 'd') direction = 'right';

      if (direction) {
        socket.emit('move', { username: currentUser, direction });
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [socket, currentUser]);

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
                <input className="auth-input" type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                <input className="auth-input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                <button type="submit" className="auth-button">Login</button>
              </form>
            )}

            {showRegister && (
              <form onSubmit={handleRegister} className="auth-form">
                <input className="auth-input" type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
                <input className="auth-input" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
                <button type="submit" className="auth-button">Register</button>
              </form>
            )}
          </div>
        )}
      </header>

      <main className="App-main">
        {message && <p className="auth-message">{message}</p>}

        {isLoggedIn && !inGame && !gameOver && (
          <button className="auth-button" onClick={handleJoinGame}>
            Join Game
          </button>
        )}
       
       <input
  id="avatar-upload"
  type="file"
  accept="image/png, image/jpeg"
  onChange={handleAvatarUpload}
  style={{ display: 'none' }}
 />
<button
  className="auth-button"
  onClick={() => document.getElementById('avatar-upload').click()}
>
  Change Avatar
</button>
        {gameOver && (
          <div className="game-over">
            <h2>🏆 The winner is {winner}!</h2>
            <button className="auth-button" onClick={returnToHome}>
              Return to Home
            </button>
          </div>
        )}

        {inGame && !gameOver && (
          <>
            <div className="board">
              <h2>COLLECT THE MOST AMMOUNT OF FOOD IN 60 SECONDS TO WIN</h2>
              {Array.from({ length: 20 }).map((_, y) => (
                <div key={y} className="row">
                  {Array.from({ length: 20 }).map((_, x) => {
                    const playerHere = players.find(p => p.x === x && p.y === y);
                    const foodHere = foods.find(f => f.x === x && f.y === y);

                    return (
                      <div key={x} className="cell">
                        {foodHere && <div className="food"></div>}
                        {playerHere && (
                        <div className="player">
                        <img
                          src={playerHere.avatar ? `/avatars/${playerHere.avatar}` : `/avatars/default.png`}
                          alt="avatar"
                          className="avatar-img"
                          style={{ width: 30, height: 30, borderRadius: '50%' }}
                        />
                        {playerHere.username}
                        <div className="score">{playerHere.score}</div>
                      </div>
                       )}

                      </div>
                    );
                  })}
                </div>
              ))}
            </div>

            <div className="players-list">
              <h2>Players in Game:</h2>
              <ul>
                {players.map((p, idx) => (
                  <li key={idx}>
                    {p.username} (Score: {p.score})
                  </li>
                ))}
              </ul>
            </div>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
