import React, { useRef, useEffect, useState } from 'react';
import { modelData } from '../assets/model_data';

export default function GalaxyCanvas() {
  const canvasRef = useRef(null);
  const zoomRef = useRef(1.8);

  // Sliders states
  const [sliderZ, setSliderZ] = useState(0.1);
  const [sliderM, setSliderM] = useState(10.1);
  const [sliderS, setSliderS] = useState(0.5);
  const [particleDensity, setParticleDensity] = useState(3000);
  const [simSpeed, setSimSpeed] = useState(1.0);

  // Reached galaxy and predicted properties states
  const [closestGalaxy, setClosestGalaxy] = useState(null);
  const closestGalaxyRef = useRef(null);
  useEffect(() => {
    closestGalaxyRef.current = closestGalaxy;
  }, [closestGalaxy]);

  // Control modes states
  const [controlMode, setControlMode] = useState('redshift'); // 'redshift' or 'full'
  const [redshiftGalaxies, setRedshiftGalaxies] = useState([]);
  const [selectedGalId, setSelectedGalId] = useState('');

  const [morphology, setMorphology] = useState('Spiral');
  const [probabilities, setProbabilities] = useState({ bg: 1.0, cc: 0.0, ia: 0.0 });
  const [distanceMpc, setDistanceMpc] = useState(0);
  const [distanceGly, setDistanceGly] = useState(0);

  // Supernova counters
  const [sneCount, setSneCount] = useState({ CC: 0, Ia: 0 });

  // Numerical integration for Luminosity Distance in flat Lambda-CDM (H0=70, Om0=0.3, Olam=0.7)
  const calculateLuminosityDistance = (z) => {
    if (z <= 0) return 0;
    const H0 = 70.0;
    const Om0 = 0.3;
    const Olam = 0.7;
    const c = 299792.458; // km/s

    const steps = 100;
    const dz = z / steps;
    let integral = 0;
    for (let i = 0; i < steps; i++) {
      const zi = i * dz;
      const ez = Math.sqrt(Om0 * Math.pow(1 + zi, 3) + Olam);
      integral += 1.0 / ez;
    }
    integral *= dz;
    return (c / H0) * integral * (1 + z); // Mpc
  };

  // MLP Feed-forward classification pass
  const predictHostProbabilities = (z, m, s) => {
    const ssfr = s - m;
    const X = [z, m, s, ssfr];

    // Standard Scaling: (x - mean) / scale
    const X_scaled = X.map(
      (val, idx) => (val - modelData.scalerMean[idx]) / modelData.scalerScale[idx]
    );

    // Layer 1 (ReLU)
    const h1 = [];
    const weights1 = modelData.coefs[0];
    const bias1 = modelData.intercepts[0];
    for (let j = 0; j < weights1[0].length; j++) {
      let sum = bias1[j];
      for (let i = 0; i < X_scaled.length; i++) {
        sum += X_scaled[i] * weights1[i][j];
      }
      h1.push(Math.max(0, sum));
    }

    // Layer 2 (ReLU)
    const h2 = [];
    const weights2 = modelData.coefs[1];
    const bias2 = modelData.intercepts[1];
    for (let j = 0; j < weights2[0].length; j++) {
      let sum = bias2[j];
      for (let i = 0; i < h1.length; i++) {
        sum += h1[i] * weights2[i][j];
      }
      h2.push(Math.max(0, sum));
    }

    // Layer 3 (Logits)
    const logits = [];
    const weights3 = modelData.coefs[2];
    const bias3 = modelData.intercepts[2];
    for (let j = 0; j < weights3[0].length; j++) {
      let sum = bias3[j];
      for (let i = 0; i < h2.length; i++) {
        sum += h2[i] * weights3[i][j];
      }
      logits.push(sum);
    }

    // Softmax Activation (with numerical stability subtract max)
    const maxLogit = Math.max(...logits);
    const exps = logits.map((l) => Math.exp(l - maxLogit));
    const sumExps = exps.reduce((a, b) => a + b, 0);
    const probs = exps.map((e) => e / sumExps);

    return {
      bg: probs[0],
      cc: probs[1],
      ia: probs[2],
    };
  };

  // Helper to classify morphology based on distance from Star-Forming Main Sequence (SFMS)
  const getMorphologyForGal = (m, s) => {
    const sfmsSfr = -4.385 + 0.812 * m - 0.027 * m * m;
    const deltaSfr = s - sfmsSfr;
    if (deltaSfr > 0.6) return 'Merger';
    if (deltaSfr < -1.5) return 'Elliptical';
    if (deltaSfr < -0.5) return 'Lenticular';
    return 'Spiral';
  };

  // Find closest galaxy in our database (Full parameter explorer mode)
  useEffect(() => {
    if (controlMode !== 'full') return;
    
    let bestGal = null;
    let minDist = Infinity;

    // Scan the compiled real and mock database
    modelData.galaxies.forEach((gal) => {
      // Scale differences: normalize physically using StandardScaler scales!
      // We apply a high weight multiplier (25.0) to redshift to ensure the matched
      // galaxy's redshift strictly tracks the observer's slider redshift.
      const dz = ((gal.z - sliderZ) / modelData.scalerScale[0]) * 25.0;
      const dm = (gal.m - sliderM) / modelData.scalerScale[1];
      const ds = (gal.s - sliderS) / modelData.scalerScale[2];
      const dist = dz * dz + dm * dm + ds * ds;

      if (dist < minDist) {
        minDist = dist;
        bestGal = gal;
      }
    });

    if (bestGal) {
      setClosestGalaxy(bestGal);

      const m = bestGal.m;
      const s = bestGal.s;
      const z = bestGal.z;

      const determinedMorphology = getMorphologyForGal(m, s);
      setMorphology(determinedMorphology);

      const probs = predictHostProbabilities(z, m, s);
      setProbabilities(probs);

      const distMpc = calculateLuminosityDistance(z);
      setDistanceMpc(distMpc);
      setDistanceGly(distMpc * 0.00326156);
    }
  }, [sliderZ, sliderM, sliderS, controlMode]);

  // Find galaxies at selected redshift and coordinate selection (Redshift-locked mode)
  useEffect(() => {
    if (controlMode !== 'redshift') return;

    // Filter database to galaxies at this redshift within +- 0.025 tolerance
    const tolerance = 0.025;
    const matches = modelData.galaxies.filter(
      (gal) => Math.abs(gal.z - sliderZ) <= tolerance
    );

    // Sort by mass descending
    matches.sort((a, b) => b.m - a.m);
    setRedshiftGalaxies(matches);

    if (matches.length > 0) {
      // Pick current selected galaxy if still in list, else pick the first
      const exists = matches.find((g) => g.id === selectedGalId);
      const targetGal = exists || matches[0];
      
      if (targetGal.id !== selectedGalId) {
        setSelectedGalId(targetGal.id);
      }
      
      setClosestGalaxy(targetGal);
      setSliderM(targetGal.m);
      setSliderS(targetGal.s);

      const determinedMorphology = getMorphologyForGal(targetGal.m, targetGal.s);
      setMorphology(determinedMorphology);

      const probs = predictHostProbabilities(targetGal.z, targetGal.m, targetGal.s);
      setProbabilities(probs);

      const distMpc = calculateLuminosityDistance(targetGal.z);
      setDistanceMpc(distMpc);
      setDistanceGly(distMpc * 0.00326156);
    } else {
      setClosestGalaxy(null);
    }
  }, [sliderZ, controlMode, selectedGalId]);

  const handleGalSelectChange = (e) => {
    const galId = e.target.value;
    const targetGal = redshiftGalaxies.find((g) => g.id === galId);
    if (targetGal) {
      setSelectedGalId(galId);
      setClosestGalaxy(targetGal);
      setSliderM(targetGal.m);
      setSliderS(targetGal.s);
      
      const determinedMorphology = getMorphologyForGal(targetGal.m, targetGal.s);
      setMorphology(determinedMorphology);
      const probs = predictHostProbabilities(targetGal.z, targetGal.m, targetGal.s);
      setProbabilities(probs);
      const distMpc = calculateLuminosityDistance(targetGal.z);
      setDistanceMpc(distMpc);
      setDistanceGly(distMpc * 0.00326156);
    }
  };

  // Orbit simulation engine
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    // Set canvas sizes responsive
    const resizeCanvas = () => {
      canvas.width = canvas.parentElement.clientWidth;
      canvas.height = 500;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const width = canvas.width;
    const height = canvas.height;
    const cx = width / 2;
    const cy = height / 2;

    // Seeded random number generator (mulberry32) for structure determinism
    const createSeededRand = (s) => {
      return () => {
        let t = (s += 0x6d2b79f5);
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
      };
    };
    const rand = createSeededRand(4242);

    // Helper to convert hex to rgba for smooth alpha fades in radial gradients
    const hexToRgba = (hex, alpha) => {
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    };

    // -------------------------------------------------------------
    // PRE-RENDER HIGH-REALISM SPRITES (OFFSCREEN CANVASES)
    // -------------------------------------------------------------
    const starColors = {
      O: '#00e5ff',
      B: '#70a6ff',
      A: '#ffffff',
      F: '#fdfdf6',
      G: '#f1c40f',
      K: '#e67e22',
      M: '#e74c3c'
    };

    const starSprites = {};
    Object.entries(starColors).forEach(([cls, color]) => {
      const size = 32; // large sprite size for smooth antialiased glow
      const offCanvas = document.createElement('canvas');
      offCanvas.width = size;
      offCanvas.height = size;
      const offCtx = offCanvas.getContext('2d');
      const cx = size / 2;
      const cy = size / 2;

      const grad = offCtx.createRadialGradient(cx, cy, 0, cx, cy, size / 2);
      grad.addColorStop(0, '#ffffff'); // white-hot stellar core
      grad.addColorStop(0.12, '#ffffff');
      grad.addColorStop(0.35, color);  // spectral color glow
      grad.addColorStop(0.68, hexToRgba(color, 0.18));
      grad.addColorStop(1, 'rgba(0,0,0,0)'); // transparent boundary

      offCtx.fillStyle = grad;
      offCtx.fillRect(0, 0, size, size);
      starSprites[cls] = offCanvas;
    });

    // Cloudy dust lane absorption sprite (absorbs background starlight)
    const dustSprite = (() => {
      const size = 48;
      const offCanvas = document.createElement('canvas');
      offCanvas.width = size;
      offCanvas.height = size;
      const offCtx = offCanvas.getContext('2d');
      const cx = size / 2;
      const cy = size / 2;

      const grad = offCtx.createRadialGradient(cx, cy, 0, cx, cy, size / 2);
      grad.addColorStop(0, 'rgba(12, 8, 4, 0.48)');  // dark brown soot center
      grad.addColorStop(0.45, 'rgba(18, 12, 6, 0.18)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');      // soft edge

      offCtx.fillStyle = grad;
      offCtx.fillRect(0, 0, size, size);
      return offCanvas;
    })();

    // Accretion disk golden-red glowing particle sprite
    const accretionSprite = (() => {
      const size = 24;
      const offCanvas = document.createElement('canvas');
      offCanvas.width = size;
      offCanvas.height = size;
      const offCtx = offCanvas.getContext('2d');
      const cx = size / 2;
      const cy = size / 2;

      const grad = offCtx.createRadialGradient(cx, cy, 0, cx, cy, size / 2);
      grad.addColorStop(0, '#ffffff'); // white hot core
      grad.addColorStop(0.22, '#ffaa00'); // golden flare
      grad.addColorStop(0.55, '#ff3300'); // red edge
      grad.addColorStop(1, 'rgba(0,0,0,0)');

      offCtx.fillStyle = grad;
      offCtx.fillRect(0, 0, size, size);
      return offCanvas;
    })();

    // Particle arrays
    const stars = [];
    const dust = [];
    const nebulae = [];
    const accretion = [];
    let supernovae = [];

    // Local camera view settings
    let angleX = 0.6;
    let angleY = 0.5;
    let orbitMode = true;

    // Intercept mouse actions from parent container
    let isDragging = false;
    let startX = 0, startY = 0;
    let mouseX = -999, mouseY = -999;
    let hoveredStar = null;

    // Orbit speed curve based on Black Hole, Baryon mass, and Dark Matter Halo
    const getRotationVelocity = (r) => {
      const r_kpc = r / 12.0;
      // Keplerian Spike of Central Black Hole
      const v_bh = 95.0 * Math.sqrt(Math.pow(10, 8.0 - 8.0) / (r_kpc + 0.01));
      // Baryonic mass rotation curve
      const v_bar = 180.0 * Math.sqrt((sliderM / 10.0) / (r_kpc + 0.3));
      // Dark Matter Halo flat rotation curve (dm fraction = 0.6, core radius = 2.0 kpc)
      const v_dm = 230.0 * Math.sqrt(0.6 * r_kpc * r_kpc / (r_kpc * r_kpc + 4.0 + 0.1));
      return Math.sqrt(v_bh * v_bh + v_bar * v_bar + v_dm * v_dm);
    };

    // Construct galaxies structures based on morphological class
    let numStars = particleDensity;
    let numDust = 0;
    let numNebulae = 0;
    let maxStellarMass = 60.0;

    if (morphology === 'Spiral') {
      numDust = Math.floor(particleDensity * 0.12);
      numNebulae = 35;
    } else if (morphology === 'Lenticular') {
      numDust = Math.floor(particleDensity * 0.03);
      numNebulae = 0;
      maxStellarMass = 5.0; // Gas depleted
    } else if (morphology === 'Elliptical') {
      numDust = 0;
      numNebulae = 0;
      maxStellarMass = 1.25; // Old population only
    } else if (morphology === 'Merger') {
      numDust = Math.floor(particleDensity * 0.1);
      numNebulae = 25;
    }

    // 1. Accretion disk around central black hole (present in active/spiral galaxies)
    const numAccretion = morphology === 'Elliptical' ? 10 : 80;
    for (let i = 0; i < numAccretion; i++) {
      accretion.push({
        r: 4 + rand() * 10,
        theta: rand() * 2 * Math.PI,
        color: rand() < 0.3 ? '#ffaa00' : rand() < 0.5 ? '#ff5500' : '#ff2200',
      });
    }

    // Helper to assign star details based on mass IMF (Initial Mass Function)
    const initStarDetails = (star, isOldGroup) => {
      let mass;
      if (isOldGroup) {
        mass = 0.08 + rand() * 1.02; // Bulges/ellipticals stars are low mass
      } else {
        const u = rand();
        if (u < 0.72) mass = 0.08 + rand() * 1.42;
        else if (u < 0.94) mass = 1.5 + rand() * 6.5;
        else mass = 8.0 + rand() * (maxStellarMass - 8.0);
      }

      // Map to spectral features
      let color = '#ff4d4d';
      let size = 0.55;
      let spectralClass = 'M';
      let temp = 3000;

      if (mass >= 16) {
        spectralClass = 'O'; temp = 35000; color = '#00e5ff'; size = 1.35;
      } else if (mass >= 8) {
        spectralClass = 'B'; temp = 18000; color = '#70a6ff'; size = 1.0;
      } else if (mass >= 2.1) {
        spectralClass = 'A'; temp = 8500; color = '#ffffff'; size = 0.8;
      } else if (mass >= 1.4) {
        spectralClass = 'F'; temp = 6800; color = '#fdfdf6'; size = 0.7;
      } else if (mass >= 1.04) {
        spectralClass = 'G'; temp = 5700; color = '#f1c40f'; size = 0.65;
      } else if (mass >= 0.45) {
        spectralClass = 'K'; temp = 4300; color = '#e67e22'; size = 0.55;
      } else {
        spectralClass = 'M'; temp = 3000; color = '#e74c3c'; size = 0.45;
      }

      let lifetime = 10000.0 * Math.pow(mass, -2.5); // Myr
      let age = lifetime * (0.05 + 0.9 * rand());

      let ccRisk = 'ZERO';
      let iaRisk = 'LOW';
      if (mass >= 8.0) {
        ccRisk = 'CRITICAL (Type II Progenitor)';
        iaRisk = 'ZERO';
      } else if (mass >= 0.8 && mass <= 1.4 && (morphology === 'Elliptical' || isOldGroup)) {
        iaRisk = 'HIGH (Binary WD)';
      }

      star.mass = mass;
      star.color = color;
      star.size = size;
      star.spectralClass = spectralClass;
      star.temp = temp;
      star.age = age;
      star.feh = -0.5 + 0.7 * Math.exp(-star.r / 80.0) + (rand() * 0.1 - 0.05);
      star.ccRisk = ccRisk;
      star.iaRisk = iaRisk;
    };

    // 2. Generate Stars depending on morphology
    if (morphology === 'Spiral') {
      const bulgeFraction = 0.25;
      for (let i = 0; i < numStars; i++) {
        const isBulge = rand() < bulgeFraction;
        let r, theta, x, y, z;
        if (isBulge) {
          r = 30 * Math.pow(rand(), 1.4);
          theta = rand() * 2 * Math.PI;
          x = r * Math.cos(theta);
          z = r * Math.sin(theta);
          y = (rand() - 0.5) * 18 * Math.exp(-r / 16);
        } else {
          // Logarithmic spiral arms
          r = 30 + 130 * Math.pow(rand(), 1.15);
          const arm = rand() < 0.5 ? 0 : 1;
          const armAngle = arm * Math.PI;
          const pitch = 0.26;
          const spiralAngle = armAngle + Math.log(r / 30) / pitch;
          theta = spiralAngle + (rand() - 0.5) * (18 / (r + 5) + 0.16);
          x = r * Math.cos(theta);
          z = r * Math.sin(theta);
          y = (rand() - 0.5) * 7 * Math.exp(-r / 75);
        }

        const star = { r, theta, x_offset: y, isBulge };
        initStarDetails(star, isBulge);
        stars.push(star);
      }
    } else if (morphology === 'Lenticular') {
      const bulgeFraction = 0.45;
      for (let i = 0; i < numStars; i++) {
        const isBulge = rand() < bulgeFraction;
        let r, theta, x, y, z;
        if (isBulge) {
          r = 45 * Math.pow(rand(), 1.3);
          theta = rand() * 2 * Math.PI;
          x = r * Math.cos(theta);
          z = r * Math.sin(theta);
          y = (rand() - 0.5) * 22 * Math.exp(-r / 22);
        } else {
          r = 45 + 115 * Math.pow(rand(), 1.0);
          theta = rand() * 2 * Math.PI;
          x = r * Math.cos(theta);
          z = r * Math.sin(theta);
          y = (rand() - 0.5) * 5 * Math.exp(-r / 60);
        }

        const star = { r, theta, x_offset: y, isBulge };
        initStarDetails(star, isBulge);
        stars.push(star);
      }
    } else if (morphology === 'Elliptical') {
      for (let i = 0; i < numStars; i++) {
        const r = 145 * Math.pow(rand(), 1.35);
        const theta = rand() * 2 * Math.PI;
        const phi = Math.acos(2 * rand() - 1);
        const star = {
          r,
          theta,
          inclination: rand() * Math.PI,
          ascendingNode: rand() * 2 * Math.PI,
          eta: rand() * 2 * Math.PI,
          isBulge: true,
        };
        initStarDetails(star, true);
        stars.push(star);
      }
    } else if (morphology === 'Merger') {
      // Two colliding cores
      const c1 = { x: -38, y: -4, z: -15 };
      const c2 = { x: 38, y: 4, z: 15 };

      for (let i = 0; i < numStars; i++) {
        const isC1 = i < numStars * 0.55;
        const center = isC1 ? c1 : c2;
        const r = 10 + Math.pow(rand(), 1.3) * 55;
        // Introduce tidally stretched arms
        const armAngle = isC1 ? 0 : Math.PI;
        const pitch = 0.35;
        const spiralAngle = armAngle + Math.log(r / 10) / pitch;
        const theta = spiralAngle + (rand() - 0.5) * 0.45;

        const star = {
          r,
          theta,
          x_offset: (rand() - 0.5) * 12 * Math.exp(-r / 25),
          center,
          isC1,
          isBulge: r < 18,
        };
        initStarDetails(star, r < 18);
        stars.push(star);
      }
    }

    // 3. Generate Star-forming Nebulae (Spiral and Merger only)
    if (morphology === 'Spiral' || morphology === 'Merger') {
      const c1 = { x: -38, y: -4, z: -15 };
      const c2 = { x: 38, y: 4, z: 15 };
      for (let i = 0; i < numNebulae; i++) {
        const isC1 = morphology === 'Merger' ? rand() < 0.55 : true;
        const center = morphology === 'Merger' ? (isC1 ? c1 : c2) : { x: 0, y: 0, z: 0 };
        const r = 30 + 115 * Math.pow(rand(), 1.15);
        const arm = rand() < 0.5 ? 0 : 1;
        const armAngle = arm * Math.PI;
        const pitch = 0.26;
        const theta = armAngle + Math.log(r / 30) / pitch + (rand() - 0.5) * 0.35;
        nebulae.push({
          r,
          theta,
          center,
          size: 15 + rand() * 20,
          color: rand() < 0.65 ? 'rgba(255, 0, 150, 0.035)' : 'rgba(0, 185, 255, 0.03)',
        });
      }
    }

    // 4. Generate Dust lanes (Spiral/Lenticular/Merger)
    for (let i = 0; i < numDust; i++) {
      let r, theta, center = { x: 0, y: 0, z: 0 };
      if (morphology === 'Spiral') {
        r = 30 + 110 * Math.pow(rand(), 1.05);
        const arm = rand() < 0.5 ? 0 : 1;
        const armAngle = arm * Math.PI;
        const pitch = 0.26;
        // Dust lanes track inside edge of arms
        theta = armAngle + Math.log(r / 30) / pitch + 0.14 + (rand() - 0.5) * 0.16;
      } else if (morphology === 'Merger') {
        const isC1 = rand() < 0.55;
        center = isC1 ? { x: -38, y: -4, z: -15 } : { x: 38, y: 4, z: 15 };
        r = 20 + 70 * rand();
        theta = rand() * 2 * Math.PI;
      } else {
        r = 45 + 85 * rand();
        theta = rand() * 2 * Math.PI;
      }
      dust.push({ r, theta, center, size: 2.5 + rand() * 3.5 });
    }

    // 3D camera projection logic
    const cameraRotateAndProject = (x, y, z) => {
      // 1. Rotate around Y-axis (Yaw)
      let x1 = x * Math.cos(angleY) - z * Math.sin(angleY);
      let z1 = x * Math.sin(angleY) + z * Math.cos(angleY);
      let y1 = y;

      // 2. Rotate around X-axis (Pitch)
      let y2 = y1 * Math.cos(angleX) - z1 * Math.sin(angleX);
      let z2 = y1 * Math.sin(angleX) + z1 * Math.cos(angleX);
      let x2 = x1;

      const dist = 380;
      if (dist + z2 <= 10) return null; // Behind camera plane
      const scale = dist / (dist + z2);

      const sx = cx + x2 * scale * zoomRef.current;
      const sy = cy + y2 * scale * zoomRef.current;

      return { sx, sy, scale, zc: z2 };
    };

    // Calculate a star's physical 3D coordinates at a given time step
    const getStarPosition = (star, stepCount) => {
      if (morphology === 'Spiral' || morphology === 'Lenticular') {
        const omega = getRotationVelocity(star.r) / (star.r * 18.0);
        star.theta += omega * simSpeed;
        return {
          x: star.r * Math.cos(star.theta),
          y: star.x_offset,
          z: star.r * Math.sin(star.theta),
        };
      } else if (morphology === 'Elliptical') {
        const omega = getRotationVelocity(star.r) / (star.r * 18.0);
        star.eta += omega * simSpeed;
        const xp = star.r * Math.cos(star.eta);
        const zp = star.r * Math.sin(star.eta);

        // Rotate into the inclined 3D orbit plane
        const x1 = xp;
        const y1 = -zp * Math.sin(star.inclination);
        const z1 = zp * Math.cos(star.inclination);

        const x_final =
          x1 * Math.cos(star.ascendingNode) - z1 * Math.sin(star.ascendingNode);
        const z_final =
          x1 * Math.sin(star.ascendingNode) + z1 * Math.cos(star.ascendingNode);
        const y_final = y1 * 0.75; // flatten oblate

        return { x: x_final, y: y_final, z: z_final };
      } else if (morphology === 'Merger') {
        // Interacting cores orbit each other slowly
        const orbitAngle = stepCount * 0.0006 * simSpeed;
        const dist = 38;
        const cx1 = -dist * Math.cos(orbitAngle);
        const cz1 = -dist * Math.sin(orbitAngle);
        const cy1 = -3 * Math.cos(orbitAngle);

        const cx2 = dist * Math.cos(orbitAngle);
        const cz2 = dist * Math.sin(orbitAngle);
        const cy2 = 3 * Math.cos(orbitAngle);

        // Update centers references
        star.center = star.isC1 ? { x: cx1, y: cy1, z: cz1 } : { x: cx2, y: cy2, z: cz2 };

        const omega = getRotationVelocity(star.r) / (star.r * 18.0);
        star.theta += omega * simSpeed;

        return {
          x: star.center.x + star.r * Math.cos(star.theta),
          y: star.center.y + star.x_offset,
          z: star.center.z + star.r * Math.sin(star.theta),
        };
      }
      return { x: 0, y: 0, z: 0 };
    };

    // Trigger supernova explosion shockwave
    const triggerSupernova = (x, y, z, isCC) => {
      const type = isCC ? 'CC' : 'Ia';
      const color = isCC ? 'rgba(0, 229, 255, 0.95)' : 'rgba(230, 126, 34, 0.95)';

      supernovae.push({
        x, y, z,
        radius: 1,
        maxRadius: isCC ? 36 : 22,
        opacity: 1.0,
        color,
        life: 80,
      });

      setSneCount((prev) => ({
        ...prev,
        [type]: prev[type] + 1,
      }));
    };

    // Canvas listeners
    const handleMouseDown = (e) => {
      isDragging = true;
      startX = e.clientX;
      startY = e.clientY;
    };

    const handleMouseMove = (e) => {
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;

      if (isDragging) {
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        angleY += dx * 0.005;
        angleX += dy * 0.005;
        // Clamp pitch to prevent gimbal lock
        angleX = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, angleX));
        startX = e.clientX;
        startY = e.clientY;
      }
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    const handleWheel = (e) => {
      e.preventDefault();
      zoomRef.current = Math.max(0.4, Math.min(3.5, zoomRef.current - e.deltaY * 0.001));
    };

    const handleClick = () => {
      if (hoveredStar) {
        const pos = getStarPosition(hoveredStar, frameCounter);
        const isCC = hoveredStar.mass >= 8.0 && morphology !== 'Elliptical';
        triggerSupernova(pos.x, pos.y, pos.z, isCC);
      }
    };

    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('wheel', handleWheel, { passive: false });
    canvas.addEventListener('click', handleClick);

    let frameCounter = 0;

    // Simulation loop
    const animate = () => {
      frameCounter++;

      // Slow orbit drift
      if (orbitMode && !isDragging) {
        angleY += 0.002;
      }

      // Draw background space
      ctx.fillStyle = '#090d16';
      ctx.fillRect(0, 0, width, height);

      // Cosmic background stars
      ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
      ctx.fillStyle = 'rgba(52, 152, 219, 0.04)';
      ctx.lineWidth = 1;
      ctx.strokeStyle = 'rgba(52, 152, 219, 0.03)';
      for (let i = 0; i < width; i += 50) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, height); ctx.stroke();
      }
      for (let j = 0; j < height; j += 50) {
        ctx.beginPath(); ctx.moveTo(0, j); ctx.lineTo(width, j); ctx.stroke();
      }

      // Depth list for sorting
      const renderList = [];

      // 1. Core SMBH(s) and background bulge/galactic glows
      if (morphology === 'Merger') {
        const orbitAngle = frameCounter * 0.0006 * simSpeed;
        const dist = 38;
        const cx1 = -dist * Math.cos(orbitAngle);
        const cz1 = -dist * Math.sin(orbitAngle);
        const cy1 = -3 * Math.cos(orbitAngle);

        const cx2 = dist * Math.cos(orbitAngle);
        const cz2 = dist * Math.sin(orbitAngle);
        const cy2 = 3 * Math.cos(orbitAngle);

        const p1 = cameraRotateAndProject(cx1, cy1, cz1);
        const p2 = cameraRotateAndProject(cx2, cy2, cz2);

        if (p1) {
          renderList.push({
            type: 'bh',
            sx: p1.sx,
            sy: p1.sy,
            scale: p1.scale,
            zc: p1.zc,
            size: 4 * p1.scale,
          });
          // Bulge glow centered on nucleus 1
          renderList.push({
            type: 'bulge_glow',
            sx: p1.sx,
            sy: p1.sy,
            scale: p1.scale,
            zc: p1.zc,
            redshiftZoomFactor: p1.redshiftZoomFactor,
            size: 45 * p1.scale
          });
        }
        if (p2) {
          renderList.push({
            type: 'bh',
            sx: p2.sx,
            sy: p2.sy,
            scale: p2.scale,
            zc: p2.zc,
            size: 3 * p2.scale,
          });
          // Bulge glow centered on nucleus 2
          renderList.push({
            type: 'bulge_glow',
            sx: p2.sx,
            sy: p2.sy,
            scale: p2.scale,
            zc: p2.zc,
            redshiftZoomFactor: p2.redshiftZoomFactor,
            size: 38 * p2.scale
          });
        }
      } else {
        const p = cameraRotateAndProject(0, 0, 0);
        if (p) {
          renderList.push({
            type: 'bh',
            sx: p.sx,
            sy: p.sy,
            scale: p.scale,
            zc: p.zc,
            size: 5.5 * p.scale,
          });

          // Bulge or galactic halo background glow centered on galaxy
          if (morphology === 'Elliptical') {
            renderList.push({
              type: 'elliptical_glow',
              sx: p.sx,
              sy: p.sy,
              scale: p.scale,
              zc: p.zc,
              redshiftZoomFactor: p.redshiftZoomFactor,
              size: 140 * p.scale
            });
          } else {
            // Spiral or Lenticular bulge glow
            renderList.push({
              type: 'bulge_glow',
              sx: p.sx,
              sy: p.sy,
              scale: p.scale,
              zc: p.zc,
              redshiftZoomFactor: p.redshiftZoomFactor,
              size: 60 * p.scale
            });
          }
        }
      }

      // 2. Accretion Disk particles
      accretion.forEach((p) => {
        p.theta += (getRotationVelocity(p.r) / (p.r * 10.0)) * 0.9 * simSpeed;
        const px = p.r * Math.cos(p.theta);
        const pz = p.r * Math.sin(p.theta);
        const py = 0;
        const proj = cameraRotateAndProject(px, py, pz);
        if (proj) {
          renderList.push({
            type: 'accretion',
            sx: proj.sx,
            sy: proj.sy,
            scale: proj.scale,
            zc: proj.zc,
            size: 1.5 * proj.scale,
            color: p.color,
          });
        }
      });

      // 3. Stellar particles
      stars.forEach((star) => {
        const pos = getStarPosition(star, frameCounter);
        const proj = cameraRotateAndProject(pos.x, pos.y, pos.z);
        if (proj) {
          renderList.push({
            type: 'star',
            sx: proj.sx,
            sy: proj.sy,
            scale: proj.scale,
            zc: proj.zc,
            size: star.size * proj.scale,
            color: star.color,
            starRef: star,
          });
        }
      });

      // 4. Gas Nebulae
      nebulae.forEach((neb) => {
        let n_cx = 0, n_cy = 0, n_cz = 0;
        if (morphology === 'Merger') {
          const orbitAngle = frameCounter * 0.0006 * simSpeed;
          const dist = 38;
          const isC1 = neb.center.x < 0; // identify center
          n_cx = isC1 ? -dist * Math.cos(orbitAngle) : dist * Math.cos(orbitAngle);
          n_cz = isC1 ? -dist * Math.sin(orbitAngle) : dist * Math.sin(orbitAngle);
          n_cy = isC1 ? -3 * Math.cos(orbitAngle) : 3 * Math.cos(orbitAngle);
        }
        neb.theta += (getRotationVelocity(neb.r) / (neb.r * 18.0)) * simSpeed;
        const nx = n_cx + neb.r * Math.cos(neb.theta);
        const nz = n_cz + neb.r * Math.sin(neb.theta);
        const ny = n_cy;
        const proj = cameraRotateAndProject(nx, ny, nz);
        if (proj) {
          renderList.push({
            type: 'nebula',
            sx: proj.sx,
            sy: proj.sy,
            scale: proj.scale,
            zc: proj.zc,
            size: neb.size * proj.scale,
            color: neb.color,
          });
        }
      });

      // 5. Dust lane particles
      dust.forEach((d) => {
        let d_cx = 0, d_cy = 0, d_cz = 0;
        if (morphology === 'Merger') {
          const orbitAngle = frameCounter * 0.0006 * simSpeed;
          const dist = 38;
          const isC1 = d.center.x < 0;
          d_cx = isC1 ? -dist * Math.cos(orbitAngle) : dist * Math.cos(orbitAngle);
          d_cz = isC1 ? -dist * Math.sin(orbitAngle) : dist * Math.sin(orbitAngle);
          d_cy = isC1 ? -3 * Math.cos(orbitAngle) : 3 * Math.cos(orbitAngle);
        }
        d.theta += (getRotationVelocity(d.r) / (d.r * 18.0)) * simSpeed;
        const dx = d_cx + d.r * Math.cos(d.theta);
        const dz = d_cz + d.r * Math.sin(d.theta);
        const dy = d_cy;
        const proj = cameraRotateAndProject(dx, dy, dz);
        if (proj) {
          renderList.push({
            type: 'dust',
            sx: proj.sx,
            sy: proj.sy,
            scale: proj.scale,
            zc: proj.zc,
            size: d.size * proj.scale,
          });
        }
      });

      // 6. Supernovae explosions
      supernovae = supernovae.filter((sn) => {
        sn.radius += (sn.maxRadius - sn.radius) * 0.07 * simSpeed;
        sn.opacity -= 0.02 * simSpeed;
        sn.life -= 1 * simSpeed;

        const proj = cameraRotateAndProject(sn.x, sn.y, sn.z);
        if (proj) {
          renderList.push({
            type: 'supernova',
            sx: proj.sx,
            sy: proj.sy,
            scale: proj.scale,
            zc: proj.zc,
            radius: sn.radius * proj.scale,
            color: sn.color.replace('0.95', sn.opacity.toFixed(2)),
            opacity: sn.opacity,
          });
        }
        return sn.life > 0;
      });

      // Sort by depth (back to front)
      renderList.sort((a, b) => b.zc - a.zc);

      // Highlight target search resets
      hoveredStar = null;
      let minMouseDist = 14;

      // Draw all elements
      renderList.forEach((el) => {
        if (el.type === 'bh') {
          // Einstein Ring Lensing glow
          const ringGrad = ctx.createRadialGradient(el.sx, el.sy, el.size * 0.9, el.sx, el.sy, el.size * 2.5);
          ringGrad.addColorStop(0, 'rgba(255, 140, 0, 0.85)'); // intense lensed light
          ringGrad.addColorStop(0.2, 'rgba(255, 190, 60, 0.9)');
          ringGrad.addColorStop(0.5, 'rgba(255, 120, 0, 0.25)');
          ringGrad.addColorStop(1, 'rgba(0,0,0,0)');
          
          ctx.beginPath();
          ctx.arc(el.sx, el.sy, el.size * 2.5, 0, Math.PI * 2);
          ctx.fillStyle = ringGrad;
          ctx.fill();

          // Event horizon black hole
          ctx.beginPath();
          ctx.arc(el.sx, el.sy, el.size, 0, Math.PI * 2);
          ctx.fillStyle = '#000000';
          ctx.fill();
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.65)';
          ctx.lineWidth = 1.0;
          ctx.stroke();
        } else if (el.type === 'bulge_glow') {
          const drawSize = el.size;
          const grad = ctx.createRadialGradient(el.sx, el.sy, 0, el.sx, el.sy, drawSize);
          grad.addColorStop(0, 'rgba(255, 235, 195, 0.42)'); // warm white-yellow core
          grad.addColorStop(0.25, 'rgba(255, 185, 100, 0.18)');
          grad.addColorStop(0.65, 'rgba(255, 120, 50, 0.04)');
          grad.addColorStop(1, 'rgba(0,0,0,0)');
          
          ctx.beginPath();
          ctx.arc(el.sx, el.sy, drawSize, 0, Math.PI * 2);
          ctx.fillStyle = grad;
          ctx.fill();
        } else if (el.type === 'elliptical_glow') {
          const drawSize = el.size;
          const grad = ctx.createRadialGradient(el.sx, el.sy, 0, el.sx, el.sy, drawSize);
          grad.addColorStop(0, 'rgba(245, 175, 100, 0.35)'); // yellowish spheroidal halo
          grad.addColorStop(0.35, 'rgba(225, 125, 55, 0.14)');
          grad.addColorStop(0.7, 'rgba(195, 85, 25, 0.03)');
          grad.addColorStop(1, 'rgba(0,0,0,0)');
          
          ctx.beginPath();
          ctx.arc(el.sx, el.sy, drawSize, 0, Math.PI * 2);
          ctx.fillStyle = grad;
          ctx.fill();
        } else if (el.type === 'accretion') {
          // Stamp pre-rendered glowing accretion particle
          const drawSize = el.size * 3.5 * el.scale;
          ctx.drawImage(accretionSprite, el.sx - drawSize / 2, el.sy - drawSize / 2, drawSize, drawSize);
        } else if (el.type === 'nebula') {
          // Gas nebulae (soft radial gradients)
          const drawSize = el.size * 0.45;
          const grad = ctx.createRadialGradient(
            el.sx,
            el.sy,
            0,
            el.sx,
            el.sy,
            drawSize
          );
          grad.addColorStop(0, el.color);
          grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
          ctx.beginPath();
          ctx.arc(el.sx, el.sy, drawSize, 0, Math.PI * 2);
          ctx.fillStyle = grad;
          ctx.fill();
        } else if (el.type === 'dust') {
          // Stamp soft absorbing dust lane cloud
          const drawSize = el.size * 7 * el.scale;
          ctx.drawImage(dustSprite, el.sx - drawSize / 2, el.sy - drawSize / 2, drawSize, drawSize);
        } else if (el.type === 'supernova') {
          ctx.beginPath();
          ctx.arc(el.sx, el.sy, el.radius, 0, Math.PI * 2);
          ctx.strokeStyle = el.color;
          ctx.lineWidth = 2 * el.scale;
          ctx.stroke();

          // Core flash glow
          ctx.beginPath();
          ctx.arc(el.sx, el.sy, el.radius * 0.4, 0, Math.PI * 2);
          ctx.fillStyle = el.color.replace(el.opacity.toFixed(2), (el.opacity * 0.25).toFixed(2));
          ctx.fill();
        } else if (el.type === 'star') {
          // Draw pre-rendered realistic stellar glow particle (smaller scale for high realism)
          const drawSize = el.size * 3.8 * el.scale;
          const half = drawSize / 2;
          ctx.drawImage(starSprites[el.starRef.spectralClass], el.sx - half, el.sy - half, drawSize, drawSize);

          // Check hover proximity
          const dx = mouseX - el.sx;
          const dy = mouseY - el.sy;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < minMouseDist) {
            minMouseDist = dist;
            hoveredStar = el.starRef;

            // Draw a hover ring around the star
            ctx.beginPath();
            ctx.arc(el.sx, el.sy, drawSize * 0.4 + 4, 0, Math.PI * 2);
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      });

      // Render Compass 3D Gizmo in Top Right corner
      const compassX = width - 40;
      const compassY = 40;
      // Draw axis vectors
      const rotateVector = (vx, vy, vz) => {
        let x1 = vx * Math.cos(angleY) - vz * Math.sin(angleY);
        let z1 = vx * Math.sin(angleY) + vz * Math.cos(angleY);
        let y2 = vy * Math.cos(angleX) - z1 * Math.sin(angleX);
        return { x: x1, y: y2 };
      };

      const axes = [
        { x: 20, y: 0, z: 0, color: '#ff4d4d', label: 'X' }, // RA
        { x: 0, y: 20, z: 0, color: '#2ecc71', label: 'Y' }, // Height
        { x: 0, y: 0, z: 20, color: '#00e5ff', label: 'Z' }, // Dec
      ];

      axes.forEach((a) => {
        const proj = rotateVector(a.x, a.y, a.z);
        ctx.beginPath();
        ctx.moveTo(compassX, compassY);
        ctx.lineTo(compassX + proj.x, compassY + proj.y);
        ctx.strokeStyle = a.color;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.fillStyle = a.color;
        ctx.font = '8px monospace';
        ctx.fillText(a.label, compassX + proj.x + 3, compassY + proj.y + 3);
      });

      // Render Active HUD overlay for hovered star
      if (hoveredStar) {
        ctx.fillStyle = 'rgba(10, 15, 30, 0.9)';
        ctx.strokeStyle = 'rgba(26, 188, 156, 0.4)';
        ctx.lineWidth = 1;
        ctx.fillRect(15, 15, 230, 135);
        ctx.strokeRect(15, 15, 230, 135);

        ctx.fillStyle = '#1abc9c';
        ctx.font = 'bold 11px sans-serif';
        ctx.fillText('🔭 STELLAR PROBE DETECTOR', 25, 32);

        ctx.fillStyle = '#f8fafc';
        ctx.font = '10px monospace';
        ctx.fillText(`Spectral Type: Class ${hoveredStar.spectralClass}`, 25, 52);
        ctx.fillText(`Temperature:   ${hoveredStar.temp} K`, 25, 67);
        ctx.fillText(`Stellar Mass:  ${hoveredStar.mass.toFixed(2)} M☉`, 25, 82);
        ctx.fillText(`Age:           ${hoveredStar.age.toFixed(1)} ${hoveredStar.mass < 1.04 ? 'Gyr' : 'Myr'}`, 25, 97);
        ctx.fillText(`Metallicity:   [Fe/H] = ${hoveredStar.feh.toFixed(2)}`, 25, 112);

        ctx.fillStyle = hoveredStar.mass >= 8.0 ? '#ff4d4d' : '#f1c40f';
        ctx.font = 'bold 9px monospace';
        ctx.fillText(`SNe Risk: CC=[${hoveredStar.ccRisk.substring(0,8)}] Ia=[${hoveredStar.iaRisk.substring(0,8)}]`, 25, 130);
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resizeCanvas);
      canvas.removeEventListener('mousedown', handleMouseDown);
      canvas.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      canvas.removeEventListener('wheel', handleWheel);
      canvas.removeEventListener('click', handleClick);
    };
  }, [morphology, particleDensity, simSpeed]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* 2-Column Dashboard Interface */}
      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: '24px', alignItems: 'start' }}>
        
        {/* Sidebar Controls Panel */}
        <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '22px' }}>
          <div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '6px', color: '#fff' }}>Simulation Controls</h3>
            <p style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Adjust physical coordinates to reach target database hosts</p>
          </div>

          <hr style={{ border: 'none', borderBottom: '1px solid rgba(255,255,255,0.06)' }} />

          {/* Mode Selector Toggle */}
          <div style={{ display: 'flex', background: 'rgba(255,255,255,0.025)', padding: '4px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
            <button
              onClick={() => setControlMode('redshift')}
              style={{
                flex: 1, padding: '8px', border: 'none', borderRadius: '6px',
                background: controlMode === 'redshift' ? 'rgba(26, 188, 156, 0.15)' : 'transparent',
                color: controlMode === 'redshift' ? '#1abc9c' : '#94a3b8',
                fontWeight: 600, fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s'
              }}
            >
              🔍 Redshift-Locked
            </button>
            <button
              onClick={() => setControlMode('full')}
              style={{
                flex: 1, padding: '8px', border: 'none', borderRadius: '6px',
                background: controlMode === 'full' ? 'rgba(52, 152, 219, 0.15)' : 'transparent',
                color: controlMode === 'full' ? '#3498db' : '#94a3b8',
                fontWeight: 600, fontSize: '0.75rem', cursor: 'pointer', transition: 'all 0.2s'
              }}
            >
              🎛️ Full Explorer
            </button>
          </div>

          {/* Redshift Slider */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
              <span style={{ fontWeight: 600, color: '#cbd5e1' }}>Redshift (z)</span>
              <span style={{ color: '#1abc9c', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{sliderZ.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.01"
              max="1.00"
              step="0.01"
              value={sliderZ}
              onChange={(e) => setSliderZ(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#1abc9c' }}
            />
          </div>

          {controlMode === 'redshift' ? (
            /* Redshift-Locked Mode controls */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              <div>
                <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>
                  Select Reached Galaxy ({redshiftGalaxies.length} found)
                </label>
                <select
                  value={selectedGalId}
                  onChange={handleGalSelectChange}
                  style={{
                    width: '100%', padding: '10px 12px', background: 'rgba(9, 13, 22, 0.85)',
                    border: '1px solid rgba(255,255,255,0.1)', color: '#fff', borderRadius: '8px',
                    fontSize: '0.85rem', cursor: 'pointer', outline: 'none'
                  }}
                >
                  {redshiftGalaxies.map((gal) => (
                    <option key={gal.id} value={gal.id}>
                      {gal.name} (z = {gal.z.toFixed(3)})
                    </option>
                  ))}
                </select>
              </div>

              {/* Read-only Mass and SFR feedback for the matched galaxy */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', background: 'rgba(255,255,255,0.015)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)', fontSize: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Stellar Mass:</span>
                  <strong style={{ color: '#3498db' }}>{sliderM.toFixed(2)} log(M*)</strong>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: '#94a3b8' }}>Star Formation Rate:</span>
                  <strong style={{ color: '#e67e22' }}>{sliderS.toFixed(2)} log(SFR)</strong>
                </div>
              </div>
            </div>
          ) : (
            /* Full Parameters Mode controls */
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {/* Stellar Mass Slider */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600, color: '#cbd5e1' }}>Stellar Mass (log₁₀ M*/M☉)</span>
                  <span style={{ color: '#3498db', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{sliderM.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="6.5"
                  max="12.5"
                  step="0.1"
                  value={sliderM}
                  onChange={(e) => setSliderM(parseFloat(e.target.value))}
                  style={{ width: '100%', cursor: 'pointer', accentColor: '#3498db' }}
                />
              </div>

              {/* Star Formation Rate Slider */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                  <span style={{ fontWeight: 600, color: '#cbd5e1' }}>Star Formation Rate (log₁₀ SFR)</span>
                  <span style={{ color: '#e67e22', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{sliderS.toFixed(1)}</span>
                </div>
                <input
                  type="range"
                  min="-5.0"
                  max="4.0"
                  step="0.1"
                  value={sliderS}
                  onChange={(e) => setSliderS(parseFloat(e.target.value))}
                  style={{ width: '100%', cursor: 'pointer', accentColor: '#e67e22' }}
                />
              </div>
            </div>
          )}

          <hr style={{ border: 'none', borderBottom: '1px solid rgba(255,255,255,0.06)' }} />

          {/* Particle Density Control */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
              <span style={{ fontWeight: 600, color: '#cbd5e1' }}>Particle Count</span>
              <span style={{ color: '#a855f7', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{particleDensity}</span>
            </div>
            <input
              type="range"
              min="1000"
              max="6000"
              step="100"
              value={particleDensity}
              onChange={(e) => setParticleDensity(parseInt(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#a855f7' }}
            />
          </div>

          {/* Simulation Speed Control */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
              <span style={{ fontWeight: 600, color: '#cbd5e1' }}>Simulation Speed</span>
              <span style={{ color: '#a855f7', fontFamily: 'JetBrains Mono', fontWeight: 700 }}>{simSpeed.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              min="0.2"
              max="2.0"
              step="0.1"
              value={simSpeed}
              onChange={(e) => setSimSpeed(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer', accentColor: '#a855f7' }}
            />
          </div>

        </div>

        {/* 3D Interactive Canvas Area */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Top matched galaxy HUD card */}
          <div className="glass-panel" style={{ padding: '20px 24px', display: 'grid', gridTemplateColumns: '1.2fr 1fr 1fr', gap: '20px', borderLeft: '4px solid var(--primary)' }}>
            <div>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600, letterSpacing: '0.05em' }}>Current Target Galaxy</span>
              <h4 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ffffff', margin: '4px 0' }}>
                {closestGalaxy ? closestGalaxy.name : 'Searching...'}
              </h4>
              <span style={{
                fontSize: '0.75rem',
                background: closestGalaxy && closestGalaxy.class > 0 ? 'rgba(26, 188, 156, 0.12)' : 'rgba(255,255,255,0.05)',
                color: closestGalaxy && closestGalaxy.class > 0 ? '#1abc9c' : '#cbd5e1',
                padding: '3px 8px', borderRadius: '4px', border: '1px solid rgba(255,255,255,0.1)',
                display: 'inline-block', marginTop: '4px', fontWeight: 600
              }}>
                {closestGalaxy ? (closestGalaxy.class === 1 ? 'Real Observation: Sharma et al.' : closestGalaxy.class === 2 ? 'Real Observation: SDSS-II SN' : 'Mock Universe Catalog') : 'Searching...'}
              </span>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600, letterSpacing: '0.05em' }}>Coordinates (RA / Dec)</span>
              <p style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc', marginTop: '6px', fontFamily: 'JetBrains Mono' }}>
                {closestGalaxy ? `${closestGalaxy.ra.toFixed(4)}° / ${closestGalaxy.dec.toFixed(4)}°` : '--'}
              </p>
            </div>
            <div>
              <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#94a3b8', fontWeight: 600, letterSpacing: '0.05em' }}>Luminosity Distance</span>
              <p style={{ fontSize: '1.15rem', fontWeight: 700, color: '#3498db', marginTop: '6px' }}>
                {distanceMpc.toFixed(1)} Mpc <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 500 }}>({distanceGly.toFixed(2)} Gly)</span>
              </p>
            </div>
          </div>

          {/* Canvas Wrapper */}
          <div style={{ position: 'relative', borderRadius: '16px', overflow: 'hidden', border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 12px 36px rgba(0,0,0,0.5)' }}>
            <canvas ref={canvasRef} style={{ display: 'block', cursor: 'crosshair', background: '#090d16' }} />

            {/* Interactive Zoom Overlay Controls */}
            <div style={{
              position: 'absolute', bottom: '20px', right: '20px',
              display: 'flex', gap: '8px', zIndex: 10
            }}>
              <button
                onClick={() => {
                  zoomRef.current = Math.min(3.5, zoomRef.current + 0.25);
                }}
                className="glow-btn"
                style={{
                  width: '36px', height: '36px', minWidth: 'auto',
                  display: 'flex', justifyContent: 'center', alignItems: 'center',
                  fontSize: '1.25rem', padding: 0, borderRadius: '8px',
                  background: 'rgba(9, 13, 22, 0.9)', border: '1px solid rgba(255,255,255,0.15)',
                  cursor: 'pointer', color: '#fff', fontWeight: 'bold'
                }}
                title="Zoom In (+)"
              >
                ＋
              </button>
              <button
                onClick={() => {
                  zoomRef.current = Math.max(0.4, zoomRef.current - 0.25);
                }}
                className="glow-btn"
                style={{
                  width: '36px', height: '36px', minWidth: 'auto',
                  display: 'flex', justifyContent: 'center', alignItems: 'center',
                  fontSize: '1.25rem', padding: 0, borderRadius: '8px',
                  background: 'rgba(9, 13, 22, 0.9)', border: '1px solid rgba(255,255,255,0.15)',
                  cursor: 'pointer', color: '#fff', fontWeight: 'bold'
                }}
                title="Zoom Out (-)"
              >
                －
              </button>
            </div>

            {/* Hover details notification label */}
            <div style={{
              position: 'absolute', top: '16px', right: '16px',
              background: 'rgba(9, 13, 22, 0.85)', padding: '8px 14px',
              borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.08)',
              fontSize: '0.75rem', color: '#cbd5e1', pointerEvents: 'none', display: 'flex', flexDirection: 'column', gap: '3px'
            }}>
              <span>🖱️ Drag to rotate view in 3D</span>
              <span>📜 Scroll/Buttons to zoom in/out</span>
              <span>🌌 Click stars to trigger Supernova</span>
            </div>

            {/* Bottom HUD bar with stats */}
            <div style={{
              position: 'absolute', bottom: '16px', left: '16px', right: '16px',
              background: 'rgba(9, 13, 22, 0.85)', padding: '12px 20px',
              borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.08)',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem'
            }}>
              <div>
                Morphology Class: <strong style={{ color: morphology === 'Merger' ? '#e74c3c' : morphology === 'Spiral' ? '#1abc9c' : morphology === 'Lenticular' ? '#f1c40f' : '#3498db' }}>{morphology}</strong>
              </div>
              <div style={{ display: 'flex', gap: '20px' }}>
                <div>
                  <span style={{ color: 'rgba(0, 229, 255, 0.95)', marginRight: '6px' }}>●</span>
                  Core-Collapse Supernovae (Type II): <strong style={{ color: '#fff' }}>{sneCount.CC + (closestGalaxy && closestGalaxy.class === 1 ? 1 : 0)}</strong>
                </div>
                <div>
                  <span style={{ color: 'rgba(230, 126, 34, 0.95)', marginRight: '6px' }}>●</span>
                  Thermonuclear Supernovae (Type Ia): <strong style={{ color: '#fff' }}>{sneCount.Ia + (closestGalaxy && closestGalaxy.class === 2 ? 1 : 0)}</strong>
                </div>
              </div>
            </div>
          </div>

          {/* Model outputs probabilities */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>
              🧠 Neural Network Progenitor Probability Inference
            </h4>
            <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '18px' }}>
              Multi-class Multi-Layer Perceptron (MLP) trained on binned mock galaxies and real host samples
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
              
              {/* Background */}
              <div style={{ background: 'rgba(255,255,255,0.015)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.04)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
                  <span style={{ color: '#94a3b8', fontWeight: 600 }}>Background Field</span>
                  <strong style={{ color: '#fff' }}>{(probabilities.bg * 100).toFixed(2)}%</strong>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ background: '#cbd5e1', width: `${probabilities.bg * 100}%`, height: '100%', transition: 'width 0.4s ease' }} />
                </div>
              </div>

              {/* CC-SN */}
              <div style={{ background: 'rgba(26, 188, 156, 0.02)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(26, 188, 156, 0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
                  <span style={{ color: '#1abc9c', fontWeight: 600 }}>Type II (Core-Collapse) Host</span>
                  <strong style={{ color: '#1abc9c' }}>{(probabilities.cc * 100).toFixed(2)}%</strong>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ background: '#1abc9c', width: `${probabilities.cc * 100}%`, height: '100%', transition: 'width 0.4s ease', boxShadow: '0 0 8px rgba(26, 188, 156, 0.5)' }} />
                </div>
              </div>

              {/* Ia-SN */}
              <div style={{ background: 'rgba(230, 126, 34, 0.02)', padding: '16px', borderRadius: '8px', border: '1px solid rgba(230, 126, 34, 0.1)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '6px' }}>
                  <span style={{ color: '#e67e22', fontWeight: 600 }}>Type Ia (Thermonuclear) Host</span>
                  <strong style={{ color: '#e67e22' }}>{(probabilities.ia * 100).toFixed(2)}%</strong>
                </div>
                <div style={{ background: 'rgba(255,255,255,0.05)', height: '6px', borderRadius: '3px', overflow: 'hidden' }}>
                  <div style={{ background: '#e67e22', width: `${probabilities.ia * 100}%`, height: '100%', transition: 'width 0.4s ease', boxShadow: '0 0 8px rgba(230, 126, 34, 0.5)' }} />
                </div>
              </div>

            </div>

            {/* Dominant Prediction HUD Banner */}
            <div style={{
              marginTop: '16px', padding: '10px 16px', borderRadius: '6px', fontSize: '0.8rem', fontWeight: 600,
              background: probabilities.cc > 0.5 ? 'rgba(26, 188, 156, 0.08)' : probabilities.ia > 0.5 ? 'rgba(230, 126, 34, 0.08)' : 'rgba(255,255,255,0.02)',
              color: probabilities.cc > 0.5 ? '#1abc9c' : probabilities.ia > 0.5 ? '#e67e22' : '#cbd5e1',
              border: '1px solid',
              borderColor: probabilities.cc > 0.5 ? 'rgba(26, 188, 156, 0.15)' : probabilities.ia > 0.5 ? 'rgba(230, 126, 34, 0.15)' : 'rgba(255,255,255,0.06)'
            }}>
              🚨 Model Inference Output: {probabilities.cc > 0.5 ? 'CORE-COLLAPSE SN PROGENITOR SITE CONFIRMED (Star-forming region detected)' : probabilities.ia > 0.5 ? 'THERMONUCLEAR SN PROGENITOR SITE CONFIRMED (Older stellar population detected)' : 'BACKGROUND FIELD ENVIRONMENT IDENTIFIED'}
            </div>
          </div>

        </div>

      </div>

    </div>
  );
}
