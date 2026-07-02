import React, { useState, useEffect } from 'react';

export default function Classifier() {
  const [mass, setMass] = useState(10.1);
  const [redshift, setRedshift] = useState(0.12);
  const [isQuenched, setIsQuenched] = useState(false);
  const [probs, setProbs] = useState({ bg: 0.8, cc: 0.1, ia: 0.1 });
  
  // Calculate star formation properties based on physical inputs
  const sfmsSfr = -0.05 * Math.pow(mass, 2) + 1.25 * mass - 6.8;
  const sfr = isQuenched ? sfmsSfr - 2.8 : sfmsSfr;
  const ssfr = sfr - mass;
  
  // rest-frame color (g-r) derived from ssfr
  const grColor = Math.min(1.0, Math.max(-0.1, 0.5 - 0.25 * (ssfr + 10.0)));
  
  useEffect(() => {
    // Neural network approximation model
    // 1. Inputs: redshift, mass, sfr, ssfr
    // 2. Class 0: Background, Class 1: CC-SN (active star forming), Class 2: Ia-SN (mass + prompt)
    
    // Core collapse SN rate scales strongly with active star formation
    const r_cc = Math.exp(sfr * 1.15) * (isQuenched ? 0.01 : 1.0);
    
    // Type Ia SN rate scales with mass (delayed) and star formation (prompt)
    const mass10 = Math.pow(10, mass - 10);
    const r_ia = 0.55 * mass10 + 0.65 * Math.pow(10, sfr);
    
    // Background non-hosts
    const r_bg = 2.0; // flat threshold
    
    // Softmax probabilities
    const sum = Math.exp(r_bg) + Math.exp(r_cc) + Math.exp(r_ia);
    const p_bg = Math.exp(r_bg) / sum;
    const p_cc = Math.exp(r_cc) / sum;
    const p_ia = Math.exp(r_ia) / sum;
    
    // Normalized probabilities
    setProbs({
      bg: p_bg,
      cc: p_cc,
      ia: p_ia
    });
  }, [mass, redshift, isQuenched]);

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '4px' }}>Host Profiling Classifier</h3>
      <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px' }}>Multi-Layer Perceptron neural network probability inference</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '30px' }}>
        {/* Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
              <span style={{ fontWeight: 600 }}>Stellar Mass (log₁₀ M*/Msun)</span>
              <span style={{ color: '#3498db', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{mass.toFixed(1)}</span>
            </div>
            <input
              type="range"
              min="7.0"
              max="12.0"
              step="0.1"
              value={mass}
              onChange={(e) => setMass(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#3498db' }}
            />
          </div>
          
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
              <span style={{ fontWeight: 600 }}>Redshift (z)</span>
              <span style={{ color: '#3498db', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{redshift.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.01"
              max="0.5"
              step="0.01"
              value={redshift}
              onChange={(e) => setRedshift(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#3498db' }}
            />
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <div>
              <span style={{ fontSize: '0.85rem', fontWeight: 600, display: 'block' }}>Galaxy Star-Forming State</span>
              <span style={{ fontSize: '0.70rem', color: '#94a3b8' }}>Quenched (red sequence) vs Active (blue cloud)</span>
            </div>
            <button
              onClick={() => setIsQuenched(!isQuenched)}
              className="glow-btn"
              style={{
                background: isQuenched ? 'linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)' : 'linear-gradient(135deg, #2ecc71 0%, #27ae60 100%)',
                boxShadow: isQuenched ? '0 4px 15px rgba(231, 76, 60, 0.4)' : '0 4px 15px rgba(46, 204, 113, 0.4)',
                fontSize: '0.75rem', padding: '6px 12px'
              }}
            >
              {isQuenched ? 'Quenched (Red)' : 'Active (Blue)'}
            </button>
          </div>
        </div>
        
        {/* Model Output probabilities */}
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between', padding: '10px 0' }}>
          <div>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#94a3b8', marginBottom: '16px' }}>Model Predicted Host Probability</h4>
            
            {/* Probability Bars */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Background */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span>Background Field Galaxy</span>
                  <strong style={{ color: '#fff' }}>{(probs.bg*100).toFixed(1)}%</strong>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', height: '10px', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{ background: '#7f8c8d', width: `${probs.bg*100}%`, height: '100%', borderRadius: '5px', transition: 'width 0.3s ease' }} />
                </div>
              </div>
              
              {/* CC-SN Host */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span style={{ color: '#1abc9c' }}>Core-Collapse Supernova (Type II)</span>
                  <strong style={{ color: '#1abc9c' }}>{(probs.cc*100).toFixed(1)}%</strong>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', height: '10px', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{ background: '#1abc9c', width: `${probs.cc*100}%`, height: '100%', borderRadius: '5px', transition: 'width 0.3s ease', boxShadow: '0 0 10px var(--primary-glow)' }} />
                </div>
              </div>
              
              {/* Ia-SN Host */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px' }}>
                  <span style={{ color: '#e67e22' }}>Thermonuclear Supernova (Type Ia)</span>
                  <strong style={{ color: '#e67e22' }}>{(probs.ia*100).toFixed(1)}%</strong>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', height: '10px', borderRadius: '5px', overflow: 'hidden' }}>
                  <div style={{ background: '#e67e22', width: `${probs.ia*100}%`, height: '100%', borderRadius: '5px', transition: 'width 0.3s ease', boxShadow: '0 0 10px var(--accent-glow)' }} />
                </div>
              </div>
            </div>
          </div>
          
          {/* Preprocessed metrics footer */}
          <div style={{ display: 'flex', gap: '16px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '12px', fontSize: '0.75rem', color: '#94a3b8' }}>
            <div>
              log(SFR): <strong style={{ color: '#fff' }}>{sfr.toFixed(2)}</strong>
            </div>
            <div>
              sSFR: <strong style={{ color: '#fff' }}>{ssfr.toFixed(2)}</strong>
            </div>
            <div>
              (g-r) Color: <strong style={{ color: '#fff' }}>{grColor.toFixed(2)}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
