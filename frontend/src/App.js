import React, { useState, useEffect } from 'react';
import './App.css';

// URL del servicio de Python (el servicio de submisión)
// En producción, Render nos proporcionará una URL de variable de entorno.
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [text, setText] = useState('');
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState('IDLE'); // IDLE, PENDING, PROCESSING, COMPLETED, ERROR
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  // Hook para consultar periódicamente el estado del trabajo
  useEffect(() => {
    let intervalId;

    if (jobId && status !== 'COMPLETED' && status !== 'ERROR') {
      intervalId = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/job_status/${jobId}`);
          if (!response.ok) {
            throw new Error('No se pudo obtener el estado del trabajo.');
          }
          const data = await response.json();
          setStatus(data.status);

          if (data.status === 'COMPLETED') {
            setResults({
              sentiment: data.sentiment,
              keywords: data.keywords,
            });
            clearInterval(intervalId);
          } else if (data.status === 'ERROR') {
            clearInterval(intervalId);
            setError('Ocurrió un error en el análisis.');
          }
        } catch (err) {
          clearInterval(intervalId);
          setError(err.message);
          setStatus('ERROR');
        }
      }, 3000); // Consulta cada 3 segundos
    }

    // Limpia el intervalo cuando el componente se desmonte
    return () => clearInterval(intervalId);
  }, [jobId, status]);

  // Función para enviar el texto al servicio de Python
  const handleSubmit = async (e) => {
    e.preventDefault();
    setJobId(null);
    setStatus('PENDING');
    setResults(null);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/submit_job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Error al enviar la solicitud.');
      }

      const data = await response.json();
      setJobId(data.job_id);
      setStatus(data.status);
    } catch (err) {
      setError(err.message);
      setStatus('ERROR');
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AnalytiCore</h1>
        <p>Análisis de sentimiento y extracción de palabras clave</p>
      </header>
      <div className="container">
        <form onSubmit={handleSubmit} className="form-group">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Escribe el texto para analizar..."
            rows="10"
            required
          />
          <button type="submit" disabled={status === 'PENDING' || status === 'PROCESSING'}>
            {status === 'PENDING' || status === 'PROCESSING' ? 'Analizando...' : 'Enviar para análisis'}
          </button>
        </form>

        {status !== 'IDLE' && (
          <div className="status-box">
            <h2>Estado del Trabajo: {status}</h2>
            {jobId && <p>ID del Trabajo: <code>{jobId}</code></p>}
            {status === 'ERROR' && <p className="error">{error}</p>}
            {status === 'COMPLETED' && results && (
              <div className="results-box">
                <h3>Resultados:</h3>
                <p><strong>Sentimiento:</strong> {results.sentiment}</p>
                <p><strong>Palabras Clave:</strong> {results.keywords.join(', ')}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;