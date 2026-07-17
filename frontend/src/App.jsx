import React, { useState } from 'react';
import GalaxyCanvas from './components/GalaxyCanvas';
import McmcSim from './components/McmcSim';
import Classifier from './components/Classifier';
import DtdSim from './components/DtdSim';

export default function App() {
  const [activeWidget, setActiveWidget] = useState('galaxy');
  const [activeMilestoneTab, setActiveMilestoneTab] = useState('m2');
  const [modalImage, setModalImage] = useState(null);

  const teamMembers = [
    { name: 'Aman Pal' },
    { name: 'Preet Varu' },
    { name: 'Aric Tirkey' },
    { name: 'Ujjwal Prakash' },
    { name: 'Adit Bansal' },
    { name: 'Ankita Chatterjee' },
    { name: 'Aryan Trivedi' },
    { name: 'Chethana Kotla' },
    { name: 'Deeksha Badhan' },
    { name: 'Dhairya Garg' },
    { name: 'Gurmannat' },
    { name: 'Kanak' },
    { name: 'Kuldeep Turkar' },
    { name: 'Kushagra Rajput' },
    { name: 'Rajit Dhakad' },
    { name: 'Shriom Gupta' },
    { name: 'Sree Neha Reddy Gavva' },
    { name: 'Yash Kumar' }
  ];

  // Science plots metadata
  const plotsData = {
    m1: [
      {
        title: 'Star Formation Main Sequence (SFMS) Fit',
        path: '/plots/task4_sfms_fit.png',
        desc: 'A quadratic regression fit to the SDSS star-forming population. The dashed lines show the ±0.3 dex scatter, representing intrinsic physical variance driven by gas accretion fluctuations and feedback.',
      },
      {
        title: 'Mock Universe Catalog Diagnostics',
        path: '/plots/task5_universe_generation_dashboard.png',
        desc: 'Diagnostic check of the 100,000 mock galaxies generated via Schechter Mass Functions. Compares true distributions against apparent detections showing Malmquist bias selection effects.',
      }
    ],
    m2: [
      {
        title: 'Galaxy Populations in the Mass-sSFR Plane',
        path: '/plots/task9_mass_ssfr_plane.png',
        desc: 'Comparing real host galaxy samples against the background mock field population. CC-SNe trace star-forming spirals (high sSFR) while Type Ia SNe occur in both active and quenched (low sSFR) galaxies.',
      },
      {
        title: 'Neural Classifier MLP Evaluation',
        path: '/plots/task11_mlp_evaluation.png',
        desc: 'Left: One-vs-Rest ROC curves displaying classification performance (AUC ~ 0.98). Right: Normalized 3x3 confusion matrix showing high separation rates between background, CC, and Ia hosts.',
      },
      {
        title: 'Permutation Feature Importance',
        path: '/plots/task12_mlp_feature_importance.png',
        desc: 'Sensitivity analysis measuring the mean decrease in Macro F1-score when shuffling features. Confirms sSFR and Stellar Mass are the primary physical properties leveraged by the network.',
      }
    ],
    m3: [
      {
        title: 'MCMC Posterior Parameter Corner Plot',
        path: '/plots/task13_mcmc_corner.png',
        desc: 'Markov Chain Monte Carlo posterior distributions for Type Ia rate coefficients A (delayed channel) and B (prompt channel). Demonstrates parameter degeneracies and physical covariance limits.',
      },
      {
        title: 'Physics-Informed Rate Goodness-of-Fit',
        path: '/plots/task13_piml_validation_dashboard.png',
        desc: 'Goodness-of-fit distributions comparing real hosts against predicted host catalogs. The physics-informed models match the observed histograms with high Kolmogorov-Smirnov p-values.',
      },
      {
        title: 'Delay Time Distribution (DTD) Solver',
        path: '/plots/task15_dtd_reconstruction.png',
        desc: 'PyTorch convolved solver reconstructing the SN Ia Delay Time Distribution. Recovers a power-law slope of γ ≈ 1.15, strongly supporting the double white-dwarf merger progenitor channel.',
      }
    ]
  };

  return (
    <div style={{ minHeight: '100vh', background: '#090d16', paddingBottom: '80px', position: 'relative' }}>
      
      {/* Background Starfield Effect */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
        backgroundImage: 'radial-gradient(ellipse at top, #1e293b 0%, #090d16 80%)',
        zIndex: -1
      }} />

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
          <a href="#about" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>About Project</a>
          <a href="#simulator" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>Physics Simulator</a>
          <a href="#diagnostics" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>Scientific Plots</a>
          <a href="#curriculum" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>Curriculum</a>
          <a href="#team" style={{ color: '#94a3b8', textDecoration: 'none', transition: 'color 0.2s' }} onMouseOver={e => e.target.style.color = '#fff'} onMouseOut={e => e.target.style.color = '#94a3b8'}>The Cohort</a>
        </nav>
      </header>

      {/* Hero Section */}
      <section id="about" style={{ padding: '85px 5% 60px 5%', textAlign: 'center', maxWidth: '950px', margin: '0 auto' }}>
        <h1 style={{ fontSize: '3.4rem', fontWeight: 800, lineHeight: 1.15, marginBottom: '22px', letterSpacing: '-1px' }} className="text-gradient">
          Physics-Informed Neural Networks for Astronomical Transients
        </h1>
        <p style={{ fontSize: '1.15rem', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '32px' }}>
          A collaborative summer research project offered by the <strong>Astronomy Club</strong>. We integrated multi-class deep MLP classifiers, Bayesian Metropolis-Hastings MCMC parameter estimation, and PyTorch convolved solvers to trace supernova progenitor environments and host galaxy potentials using real SDSS catalogs.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
          <a href="#simulator" className="glow-btn" style={{ textDecoration: 'none' }}>Launch simulator</a>
          <a href="#diagnostics" className="glow-btn" style={{ background: 'none', border: '1px solid rgba(255,255,255,0.25)', boxShadow: 'none', textDecoration: 'none' }}>View Diagnostics Plots</a>
        </div>
      </section>

      {/* Interactive Simulator Section */}
      <section id="simulator" style={{ padding: '40px 5%', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div className="glass-panel" style={{ padding: '6px', display: 'inline-flex', gap: '4px', borderRadius: '12px' }}>
            <button onClick={() => setActiveWidget('galaxy')} className={`tab-btn ${activeWidget === 'galaxy' ? 'active' : ''}`}>🌌 3D Galaxy Physics Simulator</button>
            <button onClick={() => setActiveWidget('mcmc')} className={`tab-btn ${activeWidget === 'mcmc' ? 'active' : ''}`}>🎲 MCMC Markov Walk</button>
            <button onClick={() => setActiveWidget('clf')} className={`tab-btn ${activeWidget === 'clf' ? 'active' : ''}`}>🧠 Host Classifier</button>
            <button onClick={() => setActiveWidget('dtd')} className={`tab-btn ${activeWidget === 'dtd' ? 'active' : ''}`}>📐 Convolved DTD Solver</button>
          </div>
        </div>

        {activeWidget === 'galaxy' && <GalaxyCanvas />}
        {activeWidget === 'mcmc' && <McmcSim />}
        {activeWidget === 'clf' && <Classifier />}
        {activeWidget === 'dtd' && <DtdSim />}
      </section>

      {/* Scientific Plots & Diagnostics Section */}
      <section id="diagnostics" style={{ padding: '80px 5% 40px 5%', maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '2.25rem', fontWeight: 800, marginBottom: '10px', color: '#fff' }}>Astrophysical Diagnostics & Verification</h2>
          <p style={{ color: '#94a3b8', fontSize: '1rem', maxWidth: '650px', margin: '0 auto' }}>
            Browse publication-grade research plots generated directly from our volume-complete mock catalogue simulations and ML solver models.
          </p>
        </div>

        {/* Milestone sub-tabs */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '32px' }}>
          <div className="glass-panel" style={{ padding: '6px', display: 'inline-flex', gap: '4px', borderRadius: '10px' }}>
            <button onClick={() => setActiveMilestoneTab('m1')} className={`tab-btn ${activeMilestoneTab === 'm1' ? 'active' : ''}`}>Milestone 1: Galaxy Population</button>
            <button onClick={() => setActiveMilestoneTab('m2')} className={`tab-btn ${activeMilestoneTab === 'm2' ? 'active' : ''}`}>Milestone 2: Statistics & ML</button>
            <button onClick={() => setActiveMilestoneTab('m3')} className={`tab-btn ${activeMilestoneTab === 'm3' ? 'active' : ''}`}>Milestone 3: Bayesian Rates & DTD</button>
          </div>
        </div>

        {/* Plots Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '24px' }}>
          {plotsData[activeMilestoneTab].map((plot, i) => (
            <div key={i} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '14px', cursor: 'zoom-in' }} onClick={() => setModalImage(plot)}>
              <div style={{ overflow: 'hidden', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)', background: '#080c14', display: 'flex', justifyContent: 'center', alignItems: 'center', height: '240px' }}>
                <img src={plot.path} alt={plot.title} style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain', transition: 'transform 0.3s ease' }} onMouseOver={e => e.target.style.transform = 'scale(1.03)'} onMouseOut={e => e.target.style.transform = 'scale(1.0)'} />
              </div>
              <div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>{plot.title}</h4>
                <p style={{ fontSize: '0.82rem', color: '#94a3b8', lineHeight: 1.5 }}>{plot.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Curriculum Grid */}
      <section id="curriculum" style={{ padding: '60px 5%', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 800, textAlign: 'center', marginBottom: '40px', color: '#fff' }}>Project Curriculum Structure</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
          
          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: '16px' }}>🌌</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '12px', color: '#1abc9c' }}>Module 1: Galaxy Population</h3>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.6 }}>
              Simulated a volume-complete catalog of 100,000 galaxies using Schechter Mass Functions, Star Formation Main Sequence (SFMS) curves, and color bimodality.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: '16px' }}>📊</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '12px', color: '#3498db' }}>Module 2: Statistics & Ingestion</h3>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.6 }}>
              Applied selection cuts modeling Malmquist Bias, bypassed VizieR/SDSS firewalls, and implemented 1D and 2D Kolmogorov-Smirnov tests on the Mass-sSFR plane.
            </p>
          </div>

          <div className="glass-panel" style={{ padding: '28px' }}>
            <div style={{ fontSize: '2.2rem', marginBottom: '16px' }}>🧬</div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '12px', color: '#e67e22' }}>Module 3: Physics-Informed ML</h3>
            <p style={{ fontSize: '0.9rem', color: '#94a3b8', lineHeight: 1.6 }}>
              Built multi-class neural classifiers, solved parameter degeneracies via Bayesian MCMC sampling, and reconstructed Delay Time Distributions via PyTorch convolved solvers.
            </p>
          </div>

        </div>
      </section>

      {/* Team Section */}
      <section id="team" style={{ padding: '60px 5%', maxWidth: '1200px', margin: '0 auto' }}>
        <h2 style={{ fontSize: '2.25rem', fontWeight: 800, textAlign: 'center', marginBottom: '16px', color: '#fff' }}>Project Cohort & Collaboration Team</h2>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', textAlign: 'center', maxWidth: '650px', margin: '0 auto 40px auto', lineHeight: 1.6 }}>
          Meet the team of students who collaborated on the stellar tracing pipeline, hypothesis testing, and deep learning models.
        </p>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '16px' }}>
          {teamMembers.map(member => (
            <div key={member.name} className="glass-panel" style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: '14px', borderLeft: '3px solid var(--primary)' }}>
              <div style={{ width: '36px', height: '36px', borderRadius: '18px', background: 'rgba(26, 188, 156, 0.1)', display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#1abc9c', fontWeight: 'bold', fontSize: '0.85rem', flexShrink: 0 }}>
                {member.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div style={{ overflow: 'hidden' }}>
                <strong style={{ display: 'block', fontSize: '0.95rem', color: '#fff', textOverflow: 'ellipsis', whiteSpace: 'nowrap', overflow: 'hidden' }}>{member.name}</strong>
                <span style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginTop: '2px' }}>Project Contributor</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '30px', marginTop: '40px', textAlign: 'center', fontSize: '0.85rem', color: '#64748b' }}>
        <p>© 2026 Astronomy Club Summer Project. Developed under research-mentorship guidelines.</p>
      </footer>

      {/* Zoom Image Modal Overlay */}
      {modalImage && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(5, 8, 16, 0.92)', display: 'flex', justifyContent: 'center', alignItems: 'center',
          zIndex: 1000, padding: '40px', cursor: 'zoom-out'
        }} onClick={() => setModalImage(null)}>
          <div style={{ position: 'relative', maxWidth: '1000px', maxHeight: '100%', display: 'flex', flexDirection: 'column', gap: '16px', background: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.1)', padding: '24px', borderRadius: '16px', backdropFilter: 'blur(20px)' }} onClick={e => e.stopPropagation()}>
            <img src={modalImage.path} alt={modalImage.title} style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.08)' }} />
            <div>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', marginBottom: '8px' }}>{modalImage.title}</h3>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: 1.5 }}>{modalImage.desc}</p>
            </div>
            <button onClick={() => setModalImage(null)} style={{ position: 'absolute', top: '16px', right: '16px', background: 'rgba(255,255,255,0.1)', border: 'none', color: '#fff', width: '32px', height: '32px', borderRadius: '16px', cursor: 'pointer', display: 'flex', justifyContent: 'center', alignItems: 'center', fontWeight: 'bold' }}>✕</button>
          </div>
        </div>
      )}

    </div>
  );
}
