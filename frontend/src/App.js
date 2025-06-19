import React, { useState } from 'react';

const API_URL = 'http://localhost:5000';

function App() {
  const [view, setView] = useState('login');
  const [user, setUser] = useState(null);
  const [form, setForm] = useState({});
  const [entries, setEntries] = useState([]);
  const [streak, setStreak] = useState(null);
  const [error, setError] = useState('');

  // Handle form input changes
  const handleChange = e => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  // Signup
  const handleSignup = async e => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch(`${API_URL}/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Signup failed');
      setView('login');
      setForm({});
    } catch (err) {
      setError(err.message);
    }
  };

  // Login
  const handleLogin = async e => {
    e.preventDefault();
    setError('');
    try {
      const res = await fetch(`${API_URL}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Login failed');
      setUser(data.user);
      setView('dashboard');
      setForm({});
      fetchEntries(data.user.email);
      fetchStreak(data.user.email);
    } catch (err) {
      setError(err.message);
    }
  };

  // Add entry
  const handleAddEntry = async e => {
    e.preventDefault();
    setError('');
    try {
      const entryData = { ...form, email: user.email };
      const res = await fetch(`${API_URL}/entries`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entryData),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Failed to add entry');
      setForm({});
      fetchEntries(user.email);
      fetchStreak(user.email);
    } catch (err) {
      setError(err.message);
    }
  };

  // Fetch entries
  const fetchEntries = async email => {
    const res = await fetch(`${API_URL}/entries?email=${encodeURIComponent(email)}`);
    const data = await res.json();
    setEntries(data.entries || []);
  };

  // Fetch streak
  const fetchStreak = async email => {
    const res = await fetch(`${API_URL}/streak?email=${encodeURIComponent(email)}`);
    const data = await res.json();
    setStreak(data.streak);
  };

  // Logout
  const handleLogout = () => {
    setUser(null);
    setView('login');
    setEntries([]);
    setStreak(null);
    setForm({});
    setError('');
  };

  // Render
  return (
    <div style={{ maxWidth: 500, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>Mood Tracker</h1>
      {error && <div style={{ color: 'red', marginBottom: 10 }}>{error}</div>}
      {view === 'login' && (
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <h2>Login</h2>
          <input name="email" type="email" placeholder="Email" onChange={handleChange} required />
          <input name="password" type="password" placeholder="Password" onChange={handleChange} required />
          <button type="submit">Log In</button>
          <div style={{ marginTop: 8 }}>
            Don't have an account?{' '}
            <button type="button" onClick={() => { setView('signup'); setError(''); }}>Sign Up</button>
          </div>
        </form>
      )}
      {view === 'signup' && (
        <form onSubmit={handleSignup} style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          <h2>Sign Up</h2>
          <input name="email" type="email" placeholder="Email" onChange={handleChange} required />
          <input name="password" type="password" placeholder="Password" onChange={handleChange} required />
          <input name="age" type="number" placeholder="Age" onChange={handleChange} required />
          <select name="gender" onChange={handleChange} required>
            <option value="">Gender</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="rather not say">Rather not say</option>
          </select>
          <input name="coping_mechanisms" placeholder="What helps you calm down?" onChange={handleChange} required />
          <button type="submit">Sign Up</button>
          <div style={{ marginTop: 8 }}>
            Already have an account?{' '}
            <button type="button" onClick={() => { setView('login'); setError(''); }}>Log In</button>
          </div>
        </form>
      )}
      {view === 'dashboard' && user && (
        <div>
          <div style={{ marginBottom: 10 }}>
            <b>Welcome, {user.email}!</b>
            <button style={{ float: 'right' }} onClick={handleLogout}>Log Out</button>
          </div>
          <div style={{ marginBottom: 10 }}>
            <b>Current Streak:</b> {streak} days
          </div>
          <form onSubmit={handleAddEntry} style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20 }}>
            <h3>Add Mood Entry</h3>
            <input name="highlight" placeholder="Highlight of your day" onChange={handleChange} required />
            <input name="lowlight" placeholder="Lowlight of your day" onChange={handleChange} required />
            <input name="happiness" type="number" min="1" max="10" placeholder="Happiness (1-10)" onChange={handleChange} required />
            <input name="major_event" placeholder="Major event?" onChange={handleChange} required />
            <button type="submit">Add Entry</button>
          </form>
          <div>
            <h3>Your Entries</h3>
            {entries.length === 0 && <div>No entries yet.</div>}
            {entries.map((entry, i) => (
              <div key={i} style={{ border: '1px solid #ccc', borderRadius: 6, padding: 10, marginBottom: 8 }}>
                <div><b>Date:</b> {new Date(entry.timestamp).toLocaleString()}</div>
                <div><b>Highlight:</b> {entry.highlight}</div>
                <div><b>Lowlight:</b> {entry.lowlight}</div>
                <div><b>Happiness:</b> {entry.happiness}</div>
                <div><b>Major Event:</b> {entry.major_event}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
