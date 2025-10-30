import { useState, useEffect } from 'react'
import './App.css'

interface ApiResponse {
  message: string;
  app: string;
  version: string;
  environment: string;
  docs: string;
}

function App() {
  const [apiData, setApiData] = useState<ApiResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('http://localhost:8000/')
      .then(response => response.json())
      .then(data => {
        setApiData(data)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div className="App">
      <header className="App-header">
        <h1>FastAPI Intranet Demo</h1>
        <p>Full-stack application with FastAPI + React + TypeScript + Vite</p>
        
        <div className="api-status">
          <h2>Backend API Status</h2>
          {loading && <p>Connecting to backend...</p>}
          {error && <p className="error">Error: {error}</p>}
          {apiData && (
            <div className="api-info">
              <p>✅ Connected to backend successfully!</p>
              <ul>
                <li><strong>App:</strong> {apiData.app}</li>
                <li><strong>Version:</strong> {apiData.version}</li>
                <li><strong>Environment:</strong> {apiData.environment}</li>
                <li><strong>Message:</strong> {apiData.message}</li>
              </ul>
              <p>
                <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
                  📚 View API Documentation
                </a>
              </p>
            </div>
          )}
        </div>
      </header>
    </div>
  )
}

export default App
