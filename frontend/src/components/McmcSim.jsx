import React, { useRef, useEffect, useState } from 'react';

export default function McmcSim() {
  const plotRef = useRef(null);
  const distRef = useRef(null);
  
  const [proposalWidth, setProposalWidth] = useState(0.2);
  const [isRunning, setIsRunning] = useState(false);
  const [chain, setChain] = useState([0.0]);
  const [acceptanceRate, setAcceptanceRate] = useState(100);
  const [steps, setSteps] = useState(0);
  
  // Double-peaked Gaussian target posterior
  const targetPosterior = (x) => {
    // P(theta | D) = 0.6 * N(-1.5, 0.4^2) + 0.4 * N(1.5, 0.5^2)
    const peak1 = 0.6 * Math.exp(-0.5 * Math.pow((x + 1.2), 2) / 0.16);
    const peak2 = 0.4 * Math.exp(-0.5 * Math.pow((x - 1.2), 2) / 0.25);
    return peak1 + peak2;
  };
  
  // Reset MCMC
  const handleReset = () => {
    setChain([0.0]);
    setSteps(0);
    setAcceptanceRate(100);
    setIsRunning(false);
  };
  
  // MCMC logic step
  useEffect(() => {
    if (!isRunning) return;
    
    let accepted = 0;
    let total = steps;
    
    // Calculate current acceptance rate based on history if possible
    // (we will calculate it incrementally in the interval)
    
    const interval = setInterval(() => {
      setChain(prevChain => {
        const current = prevChain[prevChain.length - 1];
        
        // Metropolis proposal: draw from Gaussian proposal distribution
        const u1 = Math.random();
        const u2 = Math.random();
        const randG = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2); // Box-Muller transform
        const proposal = current + randG * proposalWidth;
        
        // Enforce flat prior boundaries [-3.0, 3.0]
        if (proposal < -3.0 || proposal > 3.0) {
          total++;
          setSteps(total);
          // Keep current state
          return [...prevChain, current];
        }
        
        // Calculate scores
        const currentScore = targetPosterior(current);
        const propScore = targetPosterior(proposal);
        
        // Acceptance ratio
        const alpha = Math.min(1.0, propScore / currentScore);
        
        total++;
        let nextState = current;
        if (Math.random() < alpha) {
          nextState = proposal;
          // Count accepted steps
          accepted++;
        }
        
        // Truncate chain size if too long for display
        const nextChain = [...prevChain, nextState];
        if (nextChain.length > 250) {
          nextChain.shift();
        }
        
        setSteps(total);
        // Approximate acceptance rate incrementally based on sample transitions
        if (total % 10 === 0) {
          const transitions = nextChain.slice(-30);
          let changes = 0;
          for (let i = 1; i < transitions.length; i++) {
            if (transitions[i] !== transitions[i-1]) changes++;
          }
          const rate = Math.round((changes / Math.max(1, transitions.length - 1)) * 100);
          setAcceptanceRate(rate);
        }
        
        return nextChain;
      });
    }, 45); // ~22 steps per second
    
    return () => clearInterval(interval);
  }, [isRunning, proposalWidth, steps]);

  // Render Plots
  useEffect(() => {
    // 1. Render Trace Plot
    const plotCanvas = plotRef.current;
    if (plotCanvas) {
      const ctx = plotCanvas.getContext('2d');
      const w = plotCanvas.width = plotCanvas.parentElement.clientWidth;
      const h = plotCanvas.height = 180;
      
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, w, h);
      
      // Draw grid lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = 1;
      for (let y = 15; y < h; y += 30) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
      }
      
      // Plot chain
      if (chain.length > 1) {
        ctx.strokeStyle = proposalWidth < 0.08 ? '#1abc9c' : proposalWidth > 0.6 ? '#e67e22' : '#3498db';
        ctx.lineWidth = 1.8;
        ctx.beginPath();
        
        const stepSize = w / 250;
        chain.forEach((val, idx) => {
          const x = idx * stepSize;
          // Map val in [-3, 3] to h in [15, h-15]
          const y = h - (15 + ((val + 3) / 6) * (h - 30));
          if (idx === 0) ctx.moveTo(x, y);
          else ctx.lineTo(x, y);
        });
        ctx.stroke();
      }
    }
    
    // 2. Render Target Distribution and current position
    const distCanvas = distRef.current;
    if (distCanvas) {
      const ctx = distCanvas.getContext('2d');
      const w = distCanvas.width = distCanvas.parentElement.clientWidth;
      const h = distCanvas.height = 120;
      
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, w, h);
      
      // Draw target posterior curve
      ctx.strokeStyle = '#f8fafc';
      ctx.lineWidth = 2.2;
      ctx.beginPath();
      
      for (let xPixel = 0; xPixel < w; xPixel++) {
        // Map xPixel in [0, w] to theta in [-3, 3]
        const theta = -3.0 + (xPixel / w) * 6.0;
        const p = targetPosterior(theta);
        // Map p in [0, 0.65] to y in [10, h-10]
        const y = h - (10 + (p / 0.65) * (h - 20));
        
        if (xPixel === 0) ctx.moveTo(xPixel, y);
        else ctx.lineTo(xPixel, y);
      }
      ctx.stroke();
      
      // Draw current parameter value dot
      const currentVal = chain[chain.length - 1];
      const dotX = ((currentVal + 3) / 6) * w;
      const pCurrent = targetPosterior(currentVal);
      const dotY = h - (10 + (pCurrent / 0.65) * (h - 20));
      
      ctx.beginPath();
      ctx.arc(dotX, dotY, 6, 0, Math.PI * 2);
      ctx.fillStyle = '#1abc9c';
      ctx.shadowBlur = 10;
      ctx.shadowColor = '#1abc9c';
      ctx.fill();
      ctx.shadowBlur = 0; // reset
    }
  }, [chain, proposalWidth]);

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '4px' }}>Bayesian MCMC uncertainty Sampler</h3>
      <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '20px' }}>Metropolis-Hastings parameter walk on a bimodal posterior distribution</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '20px' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>
            <span>Trace Plot: Parameter Value vs Iteration</span>
            <span>+3.00</span>
          </div>
          <div style={{ borderRadius: '8px', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <canvas ref={plotRef} style={{ display: 'block' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginTop: '4px' }}>
            <span>Chain History (Window: 250 steps)</span>
            <span>-3.00</span>
          </div>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginBottom: '4px' }}>
              <span>Target Probability Density P(θ|D)</span>
              <span>θ Current: <strong style={{ color: '#1abc9c' }}>{chain[chain.length-1].toFixed(3)}</strong></span>
            </div>
            <div style={{ borderRadius: '8px', overflow: 'hidden', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
              <canvas ref={distRef} style={{ display: 'block' }} />
            </div>
          </div>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#94a3b8', marginTop: '8px' }}>
            <span>Acceptance Rate: <strong style={{ color: '#fff' }}>{acceptanceRate}%</strong></span>
            <span>Steps Run: <strong style={{ color: '#fff' }}>{steps}</strong></span>
          </div>
        </div>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', alignItems: 'center', gap: '24px', marginTop: '24px', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
            <span style={{ fontWeight: 600 }}>Proposal Step Size Width (σ)</span>
            <span style={{ color: '#1abc9c', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{proposalWidth}</span>
          </div>
          <input
            type="range"
            min="0.01"
            max="1.2"
            step="0.01"
            value={proposalWidth}
            onChange={(e) => setProposalWidth(parseFloat(e.target.value))}
            style={{ width: '100%', cursor: 'pointer', accentColor: '#1abc9c' }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.70rem', color: '#94a3b8' }}>
            <span>σ = 0.02 (Too Small: Drifts slowly)</span>
            <span>σ = 0.20 (Optimal mixing)</span>
            <span>σ = 1.00 (Too Large: Stuck)</span>
          </div>
        </div>
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setIsRunning(!isRunning)}
            className="glow-btn"
            style={{ minWidth: '100px' }}
          >
            {isRunning ? 'Pause' : 'Start'}
          </button>
          <button
            onClick={handleReset}
            className="glow-btn"
            style={{ background: 'none', border: '1px solid rgba(255, 255, 255, 0.2)', boxShadow: 'none', minWidth: '90px' }}
          >
            Reset
          </button>
        </div>
      </div>
    </div>
  );
}
