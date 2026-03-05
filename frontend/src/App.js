import React, { useState, useEffect } from 'react';
import axios from 'axios';
import TaskList from './components/TaskList';
import TaskForm from './components/TaskForm';
import SearchBar from './components/SearchBar';
import Stats from './components/Stats';
import './App.css';

const API_URL = 'http://localhost:8000/api';

function App() {
  const [tasks, setTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filter === 'active' || filter === 'done') params.status = filter;
      if (filter === 'today') params.today = new Date().toISOString().split('T')[0];
      const res = await axios.get(`${API_URL}/tasks`, { params });
      setTasks(res.data);
    } catch (err) { console.error('Failed to fetch tasks:', err); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchTasks(); }, [filter]);

  const addTask = async (task) => {
    setError(null);
    try { await axios.post(`${API_URL}/tasks`, task); fetchTasks(); }
    catch (err) {
      if (err.response?.status === 409) {
        setError('Une tâche avec ce titre existe déjà.');
      } else {
        setError('Erreur lors de la création de la tâche.');
      }
    }
  };
  const toggleTask = async (id, isActive) => {
    try { await axios.put(`${API_URL}/tasks/${id}`, { is_active: !isActive }); fetchTasks(); }
    catch (err) { console.error('Failed to update task:', err); }
  };
  const deleteTask = async (id) => {
    try { await axios.delete(`${API_URL}/tasks/${id}`); fetchTasks(); }
    catch (err) { console.error('Failed to delete task:', err); }
  };
  const searchTasks = async (query) => {
    if (!query.trim()) { fetchTasks(); return; }
    try { const res = await axios.get(`${API_URL}/search`, { params: { q: query } }); setTasks(res.data); }
    catch (err) { console.error('Search failed:', err); }
  };

  return (
    <div className="app" data-api-path="/api/tasks">
      <header><h1>📋 Task Manager</h1><Stats apiUrl={API_URL} /></header>
      <main>
        <SearchBar onSearch={searchTasks} />
        <div className="filters">
          {['all', 'active', 'done', 'today'].map(f => (
            <button key={f} className={filter === f ? 'active' : ''} onClick={() => setFilter(f)}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
        <TaskForm onSubmit={addTask} />
        {error && <p style={{ color: '#c0392b', background: '#fdecea', padding: '10px 16px', borderRadius: 8, marginBottom: 12 }}>{error}</p>}
        {loading ? <p className="loading">Loading...</p> : <TaskList tasks={tasks} onToggle={toggleTask} onDelete={deleteTask} />}
      </main>
    </div>
  );
}
export default App;
