import React, { useState } from 'react';
import GalaxyCanvas from './components/GalaxyCanvas';
import McmcSim from './components/McmcSim';
import Classifier from './components/Classifier';
import DtdSim from './components/DtdSim';

export default function App() {
  const [activeWidget, setActiveWidget] = useState('galaxy');

  const mentors = [
    { name: 'Aman Pal', role: 'Lead Pipeline Architect', desc: 'Designed the volume-complete generator and convolved PyTorch solvers.' },
    { name: 'Preet Varu', role: 'Bayesian Modeler', desc: 'Implemented Metropolis-Hastings MCMC parameter estimation and diagnostics.' },
    { name: 'Aric Tirkey', role: 'Deep Learning Lead', desc: 'Built the multiclass MLP classifier and PINN loss boundary constraints.' },
    { name: 'Ujjwal Prakash', role: 'Visualization Lead', desc: 'Developed the Streamlit event pipeline and WebGL Three.js integration.' }
  ];

  const mentees = [
    'Adit Bansal', 'Ankita Chatterjee', 'Aryan Trivedi', 'Chethana Kotla', 'Deeksha Badhan',
    'Dhairya Garg', 'Gurmannat', 'Kanak', 'Kuldeep Turkar', 'Kushagra Rajput', 'Rajit Dhakad',
    'Shriom Gupta', 'Sree Neha Reddy Gavva', 'Yash Kumar'
  ];

  return (
    <div style={{ minHeight: '100vh', background: '#090d16', paddingBottom: '80px' }}>
      
      {/* Background Starfield Effect */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundImage: 'radial-gradient(ellipse at top, #1e293b 0%, #090d16 80%)', zIndex: -1 }} />

      {/* Header */}
      <header style={{
        padding: '20px 5%', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        borderBottom: '1px solid rgba(255,255,255,0.05)', backdropFilter: 'blur(10px)',
        position: 'sticky', top: 0, zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '1.5rem', fontWeight: 700, letterSpacing: '-0.5px' }} className="text-gradient">Stellar Trace</span>
          <span style={{ background: 'rgba(26, 188, 156, 0.1)', color: '#1abc9c', fontSize: '0.75rem', padding: '3px 8px', borderRadius: '4px', border: '1px solid rgba(26, 188, 156, 0.2)', fontWeight: 600 }}>Astronomy Club</span>
        </div>
        <nav style={{ display: 'flex', gap: '30px', fontSize: '0.9rem' }}>
          <a href="#about" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>About</a>
          <a href="#simulator" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>Interactive Dashboard</a>
          <a href="#curriculum" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>Curriculum</a>
          <a href="#team" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>The Cohort</a>
        </nav>
      </header>

      {/* Hero Section */}
      <section id="about" style={{ padding: '80px 5% 60px 5%', textAlign: 'center', maxWidth: '900px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '3.25rem', fontWeight: 700, lineHeight: 1.15, marginBottom: '20px' }} className="text-gradient">
          Physics-Informed Machine Learning for Astronomical Transients
        </h1>
        <p style={{ fontSize: '1.15rem', color: '#94a3b8', lineHeight: 1.6, marginBottom: '32px' }}>
          A collaborative summer research project offered by the <strong>Astronomy Club</strong>. We integrated multi-class neural network classifiers, Bayesian Metropolis-Hastings samplers, and PyTorch convolved solvers to trace supernova progenitors and host galaxy potentials.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
          <a href="#simulator" className="glow-btn" style={{ textDecoration: 'none' }}>Launch Dashboard</a>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="glow-btn" style={{ background: 'none', border: '1px solid rgba(255,255,255,0.2)', boxShadow: 'none', textDecoration: 'none' }}>View Repository</a>
        </div>
      </section>

      {/* Interactive Simulator Section */}
      <section id="simulator" style={{ padding: '40px 5%', maxWidth: '1200px', margin: '0 auto' }}>
        <div className="glass-panel" style={{ padding: '8px', display: 'inline-flex', gap: '4px', marginBottom: '24px', borderRadius: '12px' }}>
          <button onClick={() => setActiveWidget('galaxy')} className={`tab-btn ${activeWidget === 'galaxy' ? 'active' : ''}`}>🌌 Galaxy Orbit Simulator</button>
          <button onClick={() => setActiveWidget('mcmc')} className={`tab-btn ${activeWidget === 'mcmc' ? 'active' : ''}`}>🎲 MCMC Markov Walk</button>
          <button onClick={() => setActiveWidget('clf')} className={`tab-btn ${activeWidget === 'clf' ? 'active' : ''}`}>🧠 Host Classifier</button>
          <button onClick={() => setActiveWidget('dtd')} className={`tab-btn ${activeWidget === 'dtd' ? 'active' : ''}`}> Convolved DTD Solver</button>
        </div>

        {activeWidget === 'galaxy' && <GalaxyCanvas />}
        {activeWidget === 'mcmc' && <McmcSim />}
        {activeWidget === 'clf' && <Classifier />}
        {activeWidget === 'dtd' && <DtdSim />}
      </section>

      {/* Curriculum Grid */}
      <section id="curriculum" style={{ padding: '80px 5%', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, textAlign: 'center', marginBottom: '40px' }}>Project Curriculum Structure</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
          
          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>🌌</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '12px', color: '#1abc9c' }}>Module 1: Galaxy Population</h3>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.5 }}>
              Simulated a volume-complete catalog of 100,000 galaxies using Schechter Mass Functions, Star Formation Main Sequence (SFMS) curves, and color bimodality.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>📊</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '12px', color: '#3498db' }}>Module 2: Statistics & Ingestion</h3>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.5 }}>
              Applied selection cuts modeling Malmquist Bias, bypassed VizieR/SDSS firewalls, and implemented 1D and 2D Kolmogorov-Smirnov tests on the Mass-sSFR plane.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '24px' }}>
            <div style={{ fontSize: '2rem', marginBottom: '16px' }}>🧬</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '12px', color: '#e67e22' }}>Module 3: Physics-Informed ML</h3>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.5 }}>
              Built multi-class neural classifiers, solved parameter degeneracies via Bayesian MCMC sampling, and reconstructed Delay Time Distributions via PyTorch convolved solvers.
            </p>
          </div>

        </div>
      </section>

      {/* Team Section */}
      <section id="team" style={{ padding: '60px 5%', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, textAlign: 'center', marginBottom: '48px' }}>Project Cohort</h2>
        
        {/* Mentors */}
        <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#94a3b8', marginBottom: '24px', textAlign: 'center' }}>Project Mentors</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '60px' }}>
          {mentors.map(mentor => (
            <div key={mentor.name} className="glass-panel" style={{ padding: '20px', borderLeft: '3px solid var(--primary)' }}>
              <strong style={{ display: 'block', fontSize: '1.05rem', color: '#fff' }}>{mentor.name}</strong>
              <span style={{ fontSize: '0.8rem', color: '#1abc9c', fontWeight: 600, display: 'block', marginBottom: '10px' }}>{mentor.role}</span>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', lineHeight: 1.4 }}>{mentor.desc}</p>
            </div>
          ))}
        </div>

        {/* Mentees */}
        <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#94a3b8', marginBottom: '24px', textAlign: 'center' }}>Student Mentees</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: '12px', maxWidth: '900px', margin: '0 auto' }}>
          {mentees.map(mentee => (
            <div key={mentee} className="glass-panel" style={{ padding: '10px 18px', fontSize: '0.85rem', fontWeight: 500, borderRadius: '20px' }}>
              👤 {mentee}
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '30px', textAlign: 'center', fontSize: '0.85rem', color: '#64748b' }}>
        <p>© 2026 Astronomy Club Summer Project. Developed under research-mentorship guidelines.</p>
      </footer>

    </div>
  );
}
