import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [missions, setMissions] = useState([
    { id: 'M-TEST-001', name: 'Validar Sistema L6', status: 'EM_PROGRESSO', priority: 'MEDIA' },
    { id: 'M-OPT-001', name: 'Otimizar SearchTools', status: 'EM_PLANEJAMENTO', priority: 'ALTA' }
  ])

  const [bottlenecks, setBottlenecks] = useState([
    { op: 'SimpleDiff', ms: 1200, status: 'CRITICAL' },
    { op: 'SearchLines', ms: 850, status: 'WARNING' }
  ])

  return (
    <div className="dashboard-container">
      <aside className="sidebar">
        <div className="logo">RONALDINHO 10</div>
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <button className="nav-item active">สนาม (The Pitch)</button>
          <button className="nav-item">ห้องแต่งตัว (Locker Room)</button>
          <button className="nav-item">ห้องข่าว (Press Room)</button>
        </nav>
        <div style={{ marginTop: 'auto', padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '1rem' }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Agent Status</div>
          <div style={{ color: 'var(--accent-green)', fontWeight: 'bold' }}>● Autonomous (L6)</div>
        </div>
      </aside>

      <header className="header">
        <h1>Dashboard Controle</h1>
        <div className="user-profile">
          <span>Ronaldinho Daemon v1.0</span>
        </div>
      </header>

      <main className="main-content">
        <section className="card">
          <h2>Missões Ativas (The Pitch)</h2>
          <div style={{ marginTop: '1.5rem' }}>
            {missions.map(m => (
              <div key={m.id} className="mission-item">
                <div>
                  <div style={{ fontWeight: 'bold' }}>{m.name}</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>{m.id}</div>
                </div>
                <span className={`badge ${m.status === 'EM_PROGRESSO' ? 'badge-active' : 'badge-pending'}`}>
                  {m.status}
                </span>
              </div>
            ))}
          </div>
        </section>

        <section className="card">
          <h2>Performance & Otimização</h2>
          <div style={{ marginTop: '1.5rem' }}>
            {bottlenecks.map(b => (
              <div key={b.op} className="mission-item">
                <div>
                  <div style={{ fontWeight: 'bold' }}>{b.op}</div>
                  <div style={{ color: b.status === 'CRITICAL' ? '#ff4444' : '#ffbb33' }}>{b.ms}ms</div>
                </div>
                <button className="badge-pending badge" style={{ border: 'none', cursor: 'pointer' }}>Refatorar</button>
              </div>
            ))}
          </div>
        </section>

        <section className="card" style={{ gridColumn: 'span 2' }}>
          <h2>Live Log (Press Room)</h2>
          <div style={{ 
            marginTop: '1.5rem', 
            background: 'black', 
            padding: '1rem', 
            borderRadius: '1rem',
            fontFamily: 'monospace',
            fontSize: '0.85rem',
            height: '200px',
            overflowY: 'auto'
          }}>
            <div style={{ color: '#aaa' }}>[02:40:00] Worker: Verificando MISSION_STORE...</div>
            <div style={{ color: '#00ff88' }}>[02:40:02] SecurityGuard: Log sanitizado com sucesso.</div>
            <div style={{ color: '#9d00ff' }}>[02:40:05] Optimizer: Gargalo detectado em SimpleDiff.</div>
            <div style={{ color: '#aaa' }}>[02:40:10] Gemini: Analisando código-fonte...</div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
