import React, { useRef, useEffect, useState } from 'react';

export default function DtdSim() {
  const canvasRef = useRef(null);
  const [gamma, setGamma] = useState(1.15);
  const [tauSf, setTauSf] = useState(2.5);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const w = canvas.width = canvas.parentElement.clientWidth;
    const h = canvas.height = 180;
    
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, w, h);
    
    // Draw Grid Lines
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctx.lineWidth = 1;
    for (let x = w/10; x < w; x += w/10) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = h/5; y < h; y += h/5) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }
    
    // Define grids (t from 0 to 13.7 Gyr)
    const tMax = 13.7;
    const steps = 100;
    const dt = tMax / steps;
    
    // 1. Calculate SFH: SFR(t) = SFR_0 * (t / tau) * exp(-t / tau)
    const sfh = [];
    for (let i = 0; i <= steps; i++) {
      const t = i * dt;
      const s = (t / tauSf) * Math.exp(-t / tauSf);
      sfh.push(s);
    }
    
    // 2. Numerical Convolution: R_Ia(t) = Integral_{tau_min}^t SFR(t - tau) * tau^(-gamma) d_tau
    const rates = [];
    const t_min = 0.1; // minimum delay 100 Myr
    
    for (let i = 0; i <= steps; i++) {
      const tVal = i * dt;
      let r_ia = 0;
      
      // Integrate over delay time tau
      for (let j = 1; j <= i; j++) {
        const tau = j * dt;
        if (tau >= t_min) {
          const sfhVal = sfh[i - j]; // SFR(t - tau)
          const dtdVal = Math.pow(tau, -gamma); // tau^(-gamma)
          r_ia += sfhVal * dtdVal * dt;
        }
      }
      rates.push(r_ia);
    }
    
    // Normalize curves for plotting
    const maxSfh = Math.max(...sfh, 1e-5);
    const maxRate = Math.max(...rates, 1e-5);
    
    // 3. Plot SFH (Teal curve)
    ctx.strokeStyle = '#1abc9c';
    ctx.lineWidth = 2;
    ctx.beginPath();
    sfh.forEach((val, idx) => {
      const x = (idx / steps) * w;
      const y = h - 15 - (val / maxSfh) * (h - 35);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    ctx.fillStyle = 'rgba(26, 188, 156, 0.05)';
    ctx.lineTo(w, h - 15);
    ctx.lineTo(0, h - 15);
    ctx.fill();
    
    // 4. Plot Rate Ia (Orange curve)
    ctx.strokeStyle = '#e67e22';
    ctx.lineWidth = 3;
    ctx.beginPath();
    rates.forEach((val, idx) => {
      const x = (idx / steps) * w;
      const y = h - 15 - (val / maxRate) * (h - 35);
      if (idx === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
  }, [gamma, tauSf]);

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '4px' }}>PyTorch DTD Convolved Solver</h3>
      <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px' }}>Simulating convolved Type Ia supernova rates over cosmic history</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* Plot */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>
            <span>Solid Curves: <span style={{ color: '#1abc9c' }}>Star Formation History (SFH)</span> vs <span style={{ color: '#e67e22', fontWeight: 'bold' }}>Type Ia rate</span></span>
            <span>Scale Normalized</span>
          </div>
          <div style={{ borderRadius: '8px', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <canvas ref={canvasRef} style={{ display: 'block' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginTop: '4px' }}>
            <span>t = 0 Gyr (Big Bang)</span>
            <span>Time Grid (t)</span>
            <span>t = 13.7 Gyr (Today)</span>
          </div>
        </div>
        
        {/* Sliders */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '20px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
              <span>Power-Law DTD Exponent (γ)</span>
              <strong style={{ color: '#e67e22', fontFamily: 'JetBrains Mono' }}>{gamma.toFixed(2)}</strong>
            </div>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.05"
              value={gamma}
              onChange={(e) => setGamma(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#e67e22' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: '#94a3b8', marginTop: '4px' }}>
              <span>γ = 0.50 (flat DTD)</span>
              <span>γ = 1.0 (merger model)</span>
              <span>γ = 2.0 (steep DTD)</span>
            </div>
          </div>
          
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
              <span>SFH Timescale (τ_SF in Gyr)</span>
              <strong style={{ color: '#1abc9c', fontFamily: 'JetBrains Mono' }}>{tauSf.toFixed(1)} Gyr</strong>
            </div>
            <input
              type="range"
              min="1.0"
              max="5.0"
              step="0.1"
              value={tauSf}
              onChange={(e) => setTauSf(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#1abc9c' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: '#94a3b8', marginTop: '4px' }}>
              <span>τ = 1.0 Gyr (early starburst)</span>
              <span>τ = 5.0 Gyr (extended active)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
