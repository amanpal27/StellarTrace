import React, { useRef, useEffect, useState } from 'react';

export default function GalaxyCanvas() {
  const canvasRef = useRef(null);
  const [sneCount, setSneCount] = useState({ CC: 0, Ia: 0 });
  const [morphology, setMorphology] = useState('Spiral');

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    
    // Set size
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 450;
    
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Star particles
    const stars = [];
    const particleCount = morphology === 'Spiral' ? 1200 : morphology === 'Lenticular' ? 900 : 1500;
    
    // Supernovae list
    let supernovae = [];
    
    // Generate particles based on morphology
    if (morphology === 'Spiral') {
      // Spiral galaxy with two logarithmic arms
      for (let i = 0; i < particleCount; i++) {
        const arm = i % 2 === 0 ? 0 : Math.PI;
        const theta = Math.random() * Math.PI * 3.5;
        const a = 8;
        const b = 0.22;
        const baseR = a * Math.exp(b * theta);
        
        // Add random scatter
        const r = baseR + (Math.random() - 0.5) * (baseR * 0.4 + 10);
        const x = r * Math.cos(theta + arm);
        const y = r * Math.sin(theta + arm);
        
        // Mass and temperature
        const mass = Math.random() * 20;
        const temp = 3000 + Math.random() * 25000;
        
        stars.push({
          x, y,
          r,
          theta: theta + arm,
          mass,
          temp,
          color: temp > 15000 ? '#3498db' : temp > 8000 ? '#f8fafc' : temp > 5000 ? '#f1c40f' : '#e74c3c'
        });
      }
    } else if (morphology === 'Lenticular') {
      // Lenticular: tight central bulge, flat diffuse disk, minimal arm structure
      for (let i = 0; i < particleCount; i++) {
        const isBulge = Math.random() < 0.55;
        const r = isBulge ? Math.random() * 45 : 45 + Math.random() * 120;
        const theta = Math.random() * Math.PI * 2;
        const zScatter = isBulge ? (Math.random() - 0.5) * 35 : (Math.random() - 0.5) * 8;
        
        stars.push({
          x: r * Math.cos(theta),
          y: r * Math.sin(theta),
          r,
          theta,
          mass: Math.random() * 3,
          temp: 3000 + Math.random() * 7000,
          color: Math.random() < 0.6 ? '#f1c40f' : '#e74c3c'
        });
      }
    } else {
      // Elliptical: spheroidal distribution with random isotropic orbits
      for (let i = 0; i < particleCount; i++) {
        // Plummer sphere profile
        const scaleRadius = 65;
        const u = Math.random();
        const r = scaleRadius / Math.sqrt(Math.pow(u, -2/3) - 1);
        
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        
        stars.push({
          x: r * Math.sin(phi) * Math.cos(theta),
          y: r * Math.sin(phi) * Math.sin(theta),
          r,
          theta,
          phi,
          mass: Math.random() * 2,
          temp: 3000 + Math.random() * 5000,
          color: '#e67e22',
          speed: 0.15 + Math.random() * 0.3
        });
      }
    }
    
    // Mouse interaction
    let mouse = { x: null, y: null, active: false };
    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouse.x = e.clientX - rect.left - centerX;
      mouse.y = e.clientY - rect.top - centerY;
      mouse.active = true;
    };
    const handleMouseLeave = () => { mouse.active = false; };
    const handleCanvasClick = (e) => {
      const rect = canvas.getBoundingClientRect();
      const clickX = e.clientX - rect.left - centerX;
      const clickY = e.clientY - rect.top - centerY;
      
      // Spawn a supernova at the click point
      const dist = Math.sqrt(clickX*clickX + clickY*clickY);
      // Determine supernova type based on local parameters or random mass
      const type = Math.random() < 0.45 ? 'CC' : 'Ia';
      
      supernovae.push({
        x: clickX,
        y: clickY,
        radius: 0.1,
        maxRadius: type === 'CC' ? 45 : 30,
        alpha: 1.0,
        color: type === 'CC' ? 'rgba(26, 188, 156, 0.95)' : 'rgba(230, 126, 34, 0.95)',
        type
      });
      
      // Update counters
      setSneCount(prev => ({
        ...prev,
        [type]: prev[type] + 1
      }));
    };
    
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseleave', handleMouseLeave);
    canvas.addEventListener('click', handleCanvasClick);
    
    // Animation Loop
    const draw = () => {
      // Clear
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, width, height);
      
      // Draw grid lines (subtle cosmic mesh)
      ctx.strokeStyle = 'rgba(52, 152, 219, 0.04)';
      ctx.lineWidth = 1;
      for (let i = 0; i < width; i += 40) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, height); ctx.stroke();
      }
      for (let j = 0; j < height; j += 40) {
        ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(width, j); ctx.stroke();
      }
      
      // Draw Black Hole Event Horizon in Center
      ctx.beginPath();
      ctx.arc(centerX, centerY, 6, 0, Math.PI * 2);
      ctx.fillStyle = '#000000';
      ctx.shadowBlur = 15;
      ctx.shadowColor = '#ffffff';
      ctx.fill();
      ctx.shadowBlur = 0; // reset
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
      ctx.stroke();
      
      // Draw stars
      stars.forEach(star => {
        // Rotate stars based on rotation curve v(r) = v0 * r / sqrt(r^2 + rc^2)
        const rVal = star.r + 0.1;
        const v_rot = 0.8 / (Math.sqrt(rVal) + 1.2);
        
        star.theta += v_rot;
        
        // Orbit calculations
        let drawX = star.x;
        let drawY = star.y;
        
        if (morphology === 'Spiral' || morphology === 'Lenticular') {
          drawX = star.r * Math.cos(star.theta);
          drawY = star.r * Math.sin(star.theta);
        } else {
          // Elliptical isotropic random orbits
          const orbitalSpeed = star.speed * 0.02;
          star.theta += orbitalSpeed;
          drawX = star.r * Math.sin(star.phi) * Math.cos(star.theta);
          drawY = star.r * Math.cos(star.phi);
        }
        
        // Gravitational hover pull
        if (mouse.active) {
          const dx = mouse.x - drawX;
          const dy = mouse.y - drawY;
          const distMouse = Math.sqrt(dx*dx + dy*dy);
          if (distMouse < 90) {
            const pull = (90 - distMouse) * 0.08;
            drawX += (dx / distMouse) * pull;
            drawY += (dy / distMouse) * pull;
          }
        }
        
        // Render star
        ctx.beginPath();
        ctx.arc(drawX + centerX, drawY + centerY, star.mass > 12 ? 1.5 : 0.8, 0, Math.PI * 2);
        ctx.fillStyle = star.color;
        ctx.fill();
      });
      
      // Draw active supernovae shockwaves
      supernovae = supernovae.filter(sn => {
        sn.radius += (sn.maxRadius - sn.radius) * 0.08;
        sn.alpha -= 0.025;
        
        ctx.beginPath();
        ctx.arc(sn.x + centerX, sn.y + centerY, sn.radius, 0, Math.PI * 2);
        ctx.strokeStyle = sn.color.replace('0.95', sn.alpha);
        ctx.lineWidth = 2.5;
        ctx.stroke();
        
        // Secondary glowing flash
        ctx.beginPath();
        ctx.arc(sn.x + centerX, sn.y + centerY, sn.radius * 0.4, 0, Math.PI * 2);
        ctx.fillStyle = sn.color.replace('0.95', sn.alpha * 0.3);
        ctx.fill();
        
        return sn.alpha > 0;
      });
      
      animationFrameId = requestAnimationFrame(draw);
    };
    
    draw();
    
    return () => {
      cancelAnimationFrame(animationFrameId);
      canvas.removeEventListener('mousemove', handleMouseMove);
      canvas.removeEventListener('mouseleave', handleMouseLeave);
      canvas.removeEventListener('click', handleCanvasClick);
    };
  }, [morphology]);

  return (
    <div className="glass-panel" style={{ padding: '24px', position: 'relative' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <div>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 600 }}>3D Interactive Galaxy Physics Probe</h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Gravitational accretion disk particle simulation</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          {['Spiral', 'Lenticular', 'Elliptical'].map(type => (
            <button
              key={type}
              className={`tab-btn ${morphology === type ? 'active' : ''}`}
              onClick={() => setMorphology(type)}
            >
              {type}
            </button>
          ))}
        </div>
      </div>
      
      <div style={{ position: 'relative', borderRadius: '8px', overflow: 'hidden' }}>
        <canvas ref={canvasRef} style={{ display: 'block', cursor: 'crosshair', background: '#090d16' }} />
        
        {/* Supernova HUD Overlay */}
        <div style={{
          position: 'absolute', bottom: '16px', left: '16px',
          background: 'rgba(15, 23, 42, 0.85)', padding: '12px 16px',
          borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.1)',
          display: 'flex', gap: '20px', fontSize: '0.85rem'
        }}>
          <div>
            <span style={{ color: 'rgba(26, 188, 156, 0.95)', marginRight: '6px' }}>●</span>
            Core-Collapse SNe (Type II): <strong style={{ color: '#fff' }}>{sneCount.CC}</strong>
          </div>
          <div>
            <span style={{ color: 'rgba(230, 126, 34, 0.95)', marginRight: '6px' }}>●</span>
            Thermonuclear SNe (Type Ia): <strong style={{ color: '#fff' }}>{sneCount.Ia}</strong>
          </div>
        </div>
        
        <div style={{
          position: 'absolute', top: '16px', right: '16px',
          background: 'rgba(15, 23, 42, 0.85)', padding: '6px 12px',
          borderRadius: '6px', fontSize: '0.75rem', color: '#94a3b8',
          pointerEvents: 'none'
        }}>
          Hover to pull stars | Click to explode SN
        </div>
      </div>
    </div>
  );
}
