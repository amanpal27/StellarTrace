import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
import time

# Set page configuration with a premium dark theme layout
st.set_page_config(
    page_title="Stellar Trace: Scientific Simulation Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using CSS injection with custom fonts
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    code, pre, .mono {
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Dark glassmorphism card styling */
    .metric-card {
        background: linear-gradient(135deg, rgba(10, 17, 30, 0.7) 0%, rgba(20, 30, 50, 0.4) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
        backdrop-filter: blur(12px);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(0, 245, 212, 0.3);
    }
    .metric-title {
        color: #9ca3af;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 38px;
        font-weight: 800;
    }
    .metric-desc {
        color: #6b7280;
        font-size: 12px;
        margin-top: 10px;
        line-height: 1.45;
    }
    
    /* Value text gradient colors */
    .val-morph {
        background: linear-gradient(90deg, #f1c40f 0%, #f39c12 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .val-prob {
        background: linear-gradient(90deg, #00f5d4 0%, #00bfa5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .val-sfr {
        background: linear-gradient(90deg, #bd00ff 0%, #8e44ad 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Quiz styling */
    .quiz-question-box {
        background: linear-gradient(135deg, rgba(17, 24, 39, 0.85) 0%, rgba(31, 41, 55, 0.6) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    .quiz-hud-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MACHINE LEARNING ENGINE LOAD & BACKEND PREDICTION
# ==============================================================================

@st.cache_resource
def get_trained_models():
    """
    Attempts to load the ML classifier and scaler from disk.
    If not found, trains a lightweight classifier on-the-fly on a representative
    cosmic population to ensure a self-contained, out-of-the-box run.
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.neural_network import MLPClassifier
    
    # Generate SDSS-like bimodal background population (Class 0)
    np.random.seed(42)
    n_bg = 150
    bg_m = np.random.normal(loc=9.8, scale=0.8, size=n_bg)
    bg_m = np.clip(bg_m, 8.0, 11.8)
    p_quenched = 1.0 / (1.0 + np.exp(-(bg_m - 10.4) / 0.4))
    bg_sfr = np.zeros(n_bg)
    for i in range(n_bg):
        if np.random.rand() < p_quenched[i]:
            bg_sfr[i] = np.random.normal(loc=-1.8 - 0.2 * (bg_m[i] - 10.0), scale=0.5)
        else:
            bg_sfr[i] = np.random.normal(loc=0.75 * (bg_m[i] - 10.0) + 0.2, scale=0.25)
    bg_z = np.random.uniform(0.01, 0.3, size=n_bg)
    
    # Generate mock observed host population (Class 1) matching Sharma et al. parameters
    n_host = 30
    host_m = np.random.normal(loc=10.1, scale=0.6, size=n_host)
    host_sfr = 0.75 * (host_m - 10.0) + 0.2 + np.random.normal(loc=0.0, scale=0.25, size=n_host)
    host_z = np.random.uniform(0.01, 0.4, size=n_host)
    
    # Construct combined training DataFrame
    df_bg = pd.DataFrame({'redshift': bg_z, 'log_mstar': bg_m, 'log_sfr': bg_sfr, 'class': 0})
    df_host = pd.DataFrame({'redshift': host_z, 'log_mstar': host_m, 'log_sfr': host_sfr, 'class': 1})
    df_ml = pd.concat([df_bg, df_host], ignore_index=True)
    df_ml['ssfr'] = df_ml['log_sfr'] - df_ml['log_mstar']
    
    X = df_ml[['redshift', 'log_mstar', 'log_sfr', 'ssfr']]
    y = df_ml['class']
    
    # Fit StandardScaler
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Fit MLPClassifier
    mlp = MLPClassifier(
        hidden_layer_sizes=(32, 16),
        activation='relu',
        solver='adam',
        alpha=0.1,
        max_iter=1000,
        random_state=42
    )
    mlp.fit(X_scaled, y)
    
    return mlp, scaler

# Load ML components
try:
    mlp, scaler = get_trained_models()
    model_loaded = True
except Exception as e:
    model_loaded = False

# Hardcoded coefficients for the 2nd-degree polynomial SFMS fit (from Milestone 1)
# y_sfr = beta0 + beta1 * logM + beta2 * logM^2
# Derived from SDSS star-forming fit
SFMS_BETA0 = -4.385
SFMS_BETA1 = 0.812
SFMS_BETA2 = -0.027

def predict_host_probability(log_mstar, redshift, morphology_type):
    """
    Predicts the host probability using SFMS regression and MLP classification,
    suppressing the SFR based on morphological classification (quenched vs. active).
    """
    # 1. Predict baseline log(SFR) on the main sequence
    log_sfr_baseline = SFMS_BETA0 + SFMS_BETA1 * log_mstar + SFMS_BETA2 * (log_mstar ** 2)
    
    # 2. Suppress star formation based on morphology
    if "Elliptical" in morphology_type:
        # Heavily quenched passive population
        log_sfr = log_sfr_baseline - 2.8
    elif "Lenticular" in morphology_type:
        # Transition/green-valley population
        log_sfr = log_sfr_baseline - 1.2
    else:
        # Spiral/Active star-forming
        log_sfr = log_sfr_baseline
        
    ssfr = log_sfr - log_mstar
    
    if not model_loaded:
        # Fallback math model
        prob = 1.0 / (1.0 + np.exp(-(log_sfr - 0.2 + 0.5 * ssfr)))
        return np.clip(prob, 0.0, 1.0), log_sfr
    
    # Scale features
    vec = np.array([[redshift, log_mstar, log_sfr, ssfr]])
    vec_scaled = scaler.transform(vec)
    
    # Predict classification probability
    prob = mlp.predict_proba(vec_scaled)[0, 1]
    return prob, log_sfr

# ==============================================================================
# HTML5 3D CANVAS + JAVASCRIPT GALAXY PHYSICS ORBIT SIMULATION TEMPLATE
# ==============================================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
body {
    margin: 0;
    padding: 0;
    background-color: #0b0f19;
    overflow: hidden;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: 'Outfit', sans-serif;
}
canvas {
    display: block;
    background-color: #0b0f19;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 16px 40px rgba(0,0,0,0.6);
    cursor: crosshair;
}
</style>
</head>
<body>
<canvas id="galaxyCanvas" width="600" height="500"></canvas>
<script>
const canvas = document.getElementById("galaxyCanvas");
const ctx = canvas.getContext("2d");
const cx = canvas.width / 2;
const cy = canvas.height / 2;

// Values interpolated from Streamlit sliders
const baryonicMass = %f;
const dmFraction = %f;
const coreRadius = %f;
const log_mbh = %f;
const morphology = "%s";
const particleCount = %d;
const simSpeed = %f;

// Arrays for simulation bodies
const stars = [];
const dust = [];
const nebulae = [];
const accretion = [];
const supernovae = [];

// Seeded random number generator (mulberry32) for layout determinism
function seededRandom(s) {
    return function() {
        let t = s += 0x6D2B79F5;
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    }
}
const rand = seededRandom(1337);

// Load camera view & detection counters from localStorage to preserve state across Streamlit updates
let angleX = parseFloat(localStorage.getItem('galaxy_angleX') || '0.6');
let angleY = parseFloat(localStorage.getItem('galaxy_angleY') || '0.5');
let zoom = parseFloat(localStorage.getItem('galaxy_zoom') || '1.8');
let ccCount = parseInt(localStorage.getItem('galaxy_ccCount') || '0');
let iaCount = parseInt(localStorage.getItem('galaxy_iaCount') || '0');
let orbitMode = localStorage.getItem('galaxy_orbitMode') !== 'false'; // defaults to true

let hudMessage = "SYSTEM RUNNING: READY FOR TRANSIENT MONITORS";
let hudTimer = 0;

// Radial speed profile calculations matched to Plotly
function getVelocity(r) {
    const r_kpc = r / 12.0;
    // SMBH Keplerian Spike in the inner parsecs
    const v_bh = 95.0 * Math.sqrt(Math.pow(10, log_mbh - 8.0) / (r_kpc + 0.01));
    // Baryonic mass Keplerian rotation curve
    const v_bar = 180.0 * Math.sqrt(baryonicMass / (r_kpc + 0.3));
    // Dark Matter Halo flat rotation curve
    const v_dm = 230.0 * Math.sqrt(dmFraction * r_kpc * r_kpc / (r_kpc * r_kpc + coreRadius * coreRadius + 0.1));
    return Math.sqrt(v_bh * v_bh + v_bar * v_bar + v_dm * v_dm);
}

// Particle limits
let numStars = particleCount;
let numDust = 0;
let numNebulae = 0;
let maxStellarMass = 60.0;

if (morphology === "Spiral") {
    numDust = Math.floor(particleCount * 0.12);
    numNebulae = 30;
} else if (morphology === "Lenticular") {
    numDust = Math.floor(particleCount * 0.03);
    numNebulae = 0;
    maxStellarMass = 5.0; // old features, limited gas
} else if (morphology === "Elliptical") {
    numDust = 0;
    numNebulae = 0;
    maxStellarMass = 1.25; // only old, low-mass dwarfs
}

// 1. Generate SMBH Accretion Disk particles
const numAccretion = 80;
for (let i = 0; i < numAccretion; i++) {
    const r = 5 + rand() * 12;
    accretion.push({
        r: r,
        theta: rand() * 2 * Math.PI,
        color: rand() < 0.3 ? "#ffaa00" : (rand() < 0.5 ? "#ff5500" : "#ff2200")
    });
}

// 2. Generate Stars based on Morphological density structures
for (let i = 0; i < numStars; i++) {
    let r, theta, x, y, z;
    let isBulge = false;
    
    if (morphology === "Spiral") {
        const bulgeFraction = 0.25;
        if (rand() < bulgeFraction) {
            isBulge = true;
            r = 35 * Math.pow(rand(), 1.5);
            theta = rand() * 2 * Math.PI;
            x = r * Math.cos(theta);
            z = r * Math.sin(theta);
            y = (rand() - 0.5) * 20 * Math.exp(-r / 20); // Thick dense bulge
        } else {
            // Logarithmic spiral arms
            r = 35 + 135 * Math.pow(rand(), 1.2);
            const arm = rand() < 0.5 ? 0 : 1;
            const armAngle = arm * Math.PI;
            const pitch = 0.28;
            const spiralAngle = armAngle + (Math.log(r / 35) / pitch);
            const scatter = (rand() - 0.5) * (18 / (r + 5) + 0.18);
            theta = spiralAngle + scatter;
            x = r * Math.cos(theta);
            z = r * Math.sin(theta);
            y = (rand() - 0.5) * 8 * Math.exp(-r / 80); // Exponential scale height thickness
        }
    } else if (morphology === "Lenticular") {
        const bulgeFraction = 0.40;
        if (rand() < bulgeFraction) {
            isBulge = true;
            r = 50 * Math.pow(rand(), 1.5);
            theta = rand() * 2 * Math.PI;
            x = r * Math.cos(theta);
            z = r * Math.sin(theta);
            y = (rand() - 0.5) * 25 * Math.exp(-r / 25);
        } else {
            // Featureless axisymmetric disk
            r = 50 + 110 * Math.pow(rand(), 1.0);
            theta = rand() * 2 * Math.PI;
            x = r * Math.cos(theta);
            z = r * Math.sin(theta);
            y = (rand() - 0.5) * 6 * Math.exp(-r / 70);
        }
    } else { // Elliptical (isotropic oblated spheroid)
        r = 150 * Math.pow(rand(), 1.4);
        theta = rand() * 2 * Math.PI;
        const phi = Math.acos(2 * rand() - 1);
        x = r * Math.sin(phi) * Math.cos(theta);
        z = r * Math.sin(phi) * Math.sin(theta);
        y = r * Math.cos(phi) * 0.75; // Oblateness flattening (E3 aspect ratio 10:7.5)
    }

    // Stellar mass sampling based on IMF (Initial Mass Function)
    let mass;
    if (isBulge || morphology === "Elliptical") {
        mass = 0.08 + rand() * 1.02; // max mass ~ 1.1Msun for old bulge stars
    } else {
        const u = rand();
        if (u < 0.72) {
            mass = 0.08 + rand() * 1.42; // Low mass dwarfs
        } else if (u < 0.94) {
            mass = 1.5 + rand() * 6.5; // Intermediate stars
        } else {
            mass = 8.0 + rand() * (maxStellarMass - 8.0); // O/B massive supergiants
        }
    }

    // Map mass to Spectral Class, Temperature, and Color
    let spectralClass = "M";
    let temp = 3000;
    let color = "#ff4d4d";
    let baseSize = 0.5;

    if (mass >= 16) {
        spectralClass = "O";
        temp = 30000 + Math.floor(rand() * 15000);
        color = "#00e5ff"; // glowing cyan
        baseSize = 1.3;
    } else if (mass >= 8) {
        spectralClass = "B";
        temp = 10000 + Math.floor(rand() * 20000);
        color = "#70a6ff"; // light blue
        baseSize = 1.0;
    } else if (mass >= 2.1) {
        spectralClass = "A";
        temp = 7500 + Math.floor(rand() * 2500);
        color = "#ffffff"; // white
        baseSize = 0.8;
    } else if (mass >= 1.4) {
        spectralClass = "F";
        temp = 6000 + Math.floor(rand() * 1500);
        color = "#fdfdf6"; // warm white
        baseSize = 0.7;
    } else if (mass >= 1.04) {
        spectralClass = "G";
        temp = 5200 + Math.floor(rand() * 800);
        color = "#f1c40f"; // yellow (Sun-like)
        baseSize = 0.65;
    } else if (mass >= 0.45) {
        spectralClass = "K";
        temp = 3700 + Math.floor(rand() * 1500);
        color = "#e67e22"; // orange
        baseSize = 0.6;
    } else {
        spectralClass = "M";
        temp = 2400 + Math.floor(rand() * 1300);
        color = "#e74c3c"; // red dwarf
        baseSize = 0.45;
    }

    // Main sequence lifetime: t_MS = 10^10 * (M/Msun)^-2.5 yr
    let lifetime = 10000.0 * Math.pow(mass, -2.5); // in Myr
    let age = lifetime * (0.05 + 0.9 * rand()); // current stellar age
    let ageUnit = "Myr";
    if (age > 1000) {
        age = age / 1000.0;
        ageUnit = "Gyr";
    }

    let r_kpc = r / 12.0;
    let feh = -0.65 + 0.85 * Math.exp(-r_kpc / 9.0) + (rand() * 0.1 - 0.05);
    if (morphology === "Elliptical") {
        feh = -0.4 + 0.45 * Math.exp(-r_kpc / 8.0) + (rand() * 0.15 - 0.075);
    }

    let ccRisk = "ZERO";
    let iaRisk = "LOW";
    if (mass >= 8.0) {
        ccRisk = "CRITICAL (Progenitor)";
        iaRisk = "ZERO";
    } else if (mass >= 0.8 && mass <= 1.4 && (morphology === "Elliptical" || isBulge)) {
        iaRisk = "HIGH (Binary WD)";
    }

    // 3D Orbital Plane parameters (inclination, ascending node) for isotropic orbits in Ellipticals
    let inclination = 0;
    let ascendingNode = 0;
    let eta = theta;
    
    if (morphology === "Elliptical") {
        inclination = rand() * Math.PI;
        ascendingNode = rand() * 2 * Math.PI;
        eta = rand() * 2 * Math.PI;
    }

    stars.push({
        r: r,
        theta: theta,
        y_offset: y,
        mass: mass,
        spectralClass: spectralClass,
        temp: temp,
        color: color,
        size: baseSize,
        isBulge: isBulge,
        age: age,
        ageUnit: ageUnit,
        feh: feh,
        ccRisk: ccRisk,
        iaRisk: iaRisk,
        inclination: inclination,
        ascendingNode: ascendingNode,
        eta: eta
    });
}

// 3. Generate Star-Forming Gas Nebulae along arms (Spiral only)
for (let i = 0; i < numNebulae; i++) {
    const r = 35 + 130 * Math.pow(rand(), 1.1);
    const arm = rand() < 0.5 ? 0 : 1;
    const armAngle = arm * Math.PI;
    const pitch = 0.28;
    const spiralAngle = armAngle + (Math.log(r / 35) / pitch);
    const scatter = (rand() - 0.5) * 0.3;
    const theta = spiralAngle + scatter;
    nebulae.push({
        r: r,
        theta: theta,
        size: 18 + rand() * 22,
        color: rand() < 0.65 ? "rgba(255, 0, 150, 0.035)" : "rgba(0, 180, 255, 0.03)" // H-alpha pink vs. OIII cyan
    });
}

// 4. Generate Dust lane clouds (obscuring gas)
for (let i = 0; i < numDust; i++) {
    let r, theta;
    if (morphology === "Spiral") {
        r = 35 + 120 * Math.pow(rand(), 1.0);
        const arm = rand() < 0.5 ? 0 : 1;
        const armAngle = arm * Math.PI;
        const pitch = 0.28;
        // Dust lanes are slightly offset angularly to line the inside edges of spiral arms
        const spiralAngle = armAngle + (Math.log(r / 35) / pitch) + 0.12;
        const scatter = (rand() - 0.5) * 0.18;
        theta = spiralAngle + scatter;
    } else {
        r = 50 + 90 * rand();
        theta = rand() * 2 * Math.PI;
    }
    dust.push({
        r: r,
        theta: theta,
        size: 3 + rand() * 4
    });
}

// Helper to compute a star's current 3D position in the galactic frame
function getStar3DPosition(star) {
    if (morphology === "Spiral" || morphology === "Lenticular") {
        const omega = getVelocity(star.r) / (star.r * 18.0);
        star.theta += omega * simSpeed;
        return {
            x: star.r * Math.cos(star.theta),
            y: star.y_offset,
            z: star.r * Math.sin(star.theta)
        };
    } else {
        const omega = getVelocity(star.r) / (star.r * 18.0);
        star.eta += omega * simSpeed;
        
        const xp = star.r * Math.cos(star.eta);
        const zp = star.r * Math.sin(star.eta);
        
        // Rotate into the inclined 3D orbit plane
        const x1 = xp;
        const y1 = -zp * Math.sin(star.inclination);
        const z1 = zp * Math.cos(star.inclination);
        
        const x_final = x1 * Math.cos(star.ascendingNode) - z1 * Math.sin(star.ascendingNode);
        const z_final = x1 * Math.sin(star.ascendingNode) + z1 * Math.cos(star.ascendingNode);
        const y_final = y1 * 0.75; // flatten oblate spheroid
        
        return {
            x: x_final,
            y: y_final,
            z: z_final
        };
    }
}

// 3D Perspective rotation and projection matrix calculations
function cameraRotateAndProject(x, y, z) {
    // 1. Rotate around Y-axis (Yaw)
    let x1 = x * Math.cos(angleY) - z * Math.sin(angleY);
    let z1 = x * Math.sin(angleY) + z * Math.cos(angleY);
    let y1 = y;

    // 2. Rotate around X-axis (Pitch)
    let y2 = y1 * Math.cos(angleX) - z1 * Math.sin(angleX);
    let z2 = y1 * Math.sin(angleX) + z1 * Math.cos(angleX);
    let x2 = x1;

    let dist = 380;
    if (dist + z2 <= 10) return null; // Behind camera plane
    
    let scale = dist / (dist + z2);
    let sx = cx + x2 * scale * zoom;
    let sy = cy + y2 * scale * zoom;
    
    return { sx: sx, sy: sy, scale: scale, zc: z2 };
}

// Rotation vector helper for the 3D compass axis display
function rotateVector(vx, vy, vz) {
    let x1 = vx * Math.cos(angleY) - vz * Math.sin(angleY);
    let z1 = vx * Math.sin(angleY) + vz * Math.cos(angleY);
    let y1 = vy;

    let y2 = y1 * Math.cos(angleX) - z1 * Math.sin(angleX);
    return { x: x1, y: y2 };
}

// Spawns Type II (CC) or Type Ia (thermonuclear) supernovae explosions
function triggerSupernova(x, y, z, isCC) {
    const color = isCC ? "#00ffcc" : "#ffaa00";
    if (isCC) {
        ccCount++;
        localStorage.setItem('galaxy_ccCount', ccCount.toString());
        hudMessage = "DETECTION: Core-Collapse SN (Type II)";
    } else {
        iaCount++;
        localStorage.setItem('galaxy_iaCount', iaCount.toString());
        hudMessage = "DETECTION: Thermonuclear SN (Type Ia)";
    }
    
    supernovae.push({
        x: x, y: y, z: z,
        radius: 2,
        maxRadius: isCC ? 38 : 22,
        opacity: 1.0,
        color: color,
        life: 80
    });
    hudTimer = 120;
}

// Interactive cursor positions and clicks
let mousePos = { x: -999, y: -999 };
let isDragging = false;
let startX, startY;

canvas.addEventListener("mousedown", function(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // UI Button clicks checks
    if (x >= 15 && x <= 85 && y >= 65 && y <= 83) {
        angleX = 0; angleY = 0;
        localStorage.setItem('galaxy_angleX', '0');
        localStorage.setItem('galaxy_angleY', '0');
        return;
    }
    if (x >= 90 && x <= 160 && y >= 65 && y <= 83) {
        angleX = Math.PI / 2; angleY = 0;
        localStorage.setItem('galaxy_angleX', (Math.PI/2).toString());
        localStorage.setItem('galaxy_angleY', '0');
        return;
    }
    if (x >= 165 && x <= 265 && y >= 65 && y <= 83) {
        orbitMode = !orbitMode;
        localStorage.setItem('galaxy_orbitMode', orbitMode ? 'true' : 'false');
        return;
    }
    if (x >= 15 && x <= 115 && y >= canvas.height - 30 && y <= canvas.height - 14) {
        ccCount = 0; iaCount = 0;
        localStorage.setItem('galaxy_ccCount', '0');
        localStorage.setItem('galaxy_iaCount', '0');
        hudMessage = "DETECTION LOGS CLEARED";
        hudTimer = 100;
        return;
    }
    
    isDragging = true;
    startX = e.clientX;
    startY = e.clientY;
});

canvas.addEventListener("mousemove", function(e) {
    const rect = canvas.getBoundingClientRect();
    mousePos.x = e.clientX - rect.left;
    mousePos.y = e.clientY - rect.top;
    
    if (isDragging) {
        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        
        angleY += dx * 0.005;
        angleX += dy * 0.005;
        
        // Clamp pitch to prevent rotation lock at poles
        angleX = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, angleX));
        
        startX = e.clientX;
        startY = e.clientY;
        
        localStorage.setItem('galaxy_angleX', angleX.toString());
        localStorage.setItem('galaxy_angleY', angleY.toString());
    }
});

canvas.addEventListener("mouseup", function() { isDragging = false; });
canvas.addEventListener("mouseleave", function() { isDragging = false; mousePos.x = -999; });

canvas.addEventListener("wheel", function(e) {
    e.preventDefault();
    zoom -= e.deltaY * 0.001;
    zoom = Math.max(0.5, Math.min(3.5, zoom));
    localStorage.setItem('galaxy_zoom', zoom.toString());
});

// Click a star to trigger a supernova at its coordinates
canvas.addEventListener("click", function(e) {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Ignore clicks on buttons
    if (y >= 65 && y <= 83 && x >= 15 && x <= 265) return;
    if (y >= canvas.height - 30 && y <= canvas.height - 14 && x >= 15 && x <= 115) return;
    
    if (hoveredStarParticle) {
        const star = hoveredStarParticle.starRef;
        const pos = getStar3DPosition(star);
        // Force CC supernova if mass >= 8Msun, else Type Ia
        const isCC = star.mass >= 8.0 && morphology !== "Elliptical";
        triggerSupernova(pos.x, pos.y, pos.z, isCC);
    }
});

let hoveredStarParticle = null;
let frameCounter = 0;

function animate() {
    frameCounter++;
    
    // Slow camera Y rotation in auto-orbit mode
    if (orbitMode && !isDragging) {
        angleY += 0.002;
    }
    
    // Clear canvas and draw trailing space background
    ctx.fillStyle = "rgba(11, 15, 25, 0.20)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 3D Depth list for stars, dust, gas, central SMBH, and SN shockwaves
    const renderList = [];
    
    // 1. Add SMBH Core
    let bh_proj = cameraRotateAndProject(0, 0, 0);
    if (bh_proj) {
        renderList.push({
            type: 'bh',
            sx: bh_proj.sx,
            sy: bh_proj.sy,
            scale: bh_proj.scale,
            zc: bh_proj.zc,
            size: 3 * bh_proj.scale * (log_mbh / 8.0)
        });
    }
    
    // 2. Add Accretion Disk particles
    for (let i = 0; i < accretion.length; i++) {
        const p = accretion[i];
        p.theta += getVelocity(p.r) / (p.r * 12.0) * simSpeed;
        let px = p.r * Math.cos(p.theta);
        let pz = p.r * Math.sin(p.theta);
        let py = (rand() - 0.5) * 1.5;
        let proj = cameraRotateAndProject(px, py, pz);
        if (proj) {
            renderList.push({
                type: 'accretion',
                sx: proj.sx,
                sy: proj.sy,
                scale: proj.scale,
                zc: proj.zc,
                size: (1.2 + rand() * 1.5) * proj.scale,
                color: p.color
            });
        }
    }
    
    // 3. Add stars with computed 3D positions
    for (let i = 0; i < stars.length; i++) {
        const star = stars[i];
        let pos = getStar3DPosition(star);
        let proj = cameraRotateAndProject(pos.x, pos.y, pos.z);
        if (proj) {
            renderList.push({
                type: 'star',
                sx: proj.sx,
                sy: proj.sy,
                scale: proj.scale,
                zc: proj.zc,
                size: star.size * proj.scale,
                color: star.color,
                starRef: star
            });
        }
    }
    
    // 4. Add Gaseous Nebulae
    for (let i = 0; i < nebulae.length; i++) {
        const neb = nebulae[i];
        neb.theta += getVelocity(neb.r) / (neb.r * 18.0) * simSpeed;
        let nx = neb.r * Math.cos(neb.theta);
        let nz = neb.r * Math.sin(neb.theta);
        let ny = (rand() - 0.5) * 3;
        let proj = cameraRotateAndProject(nx, ny, nz);
        if (proj) {
            renderList.push({
                type: 'nebula',
                sx: proj.sx,
                sy: proj.sy,
                scale: proj.scale,
                zc: proj.zc,
                size: neb.size * proj.scale,
                color: neb.color
            });
        }
    }
    
    // 5. Add Dust Clouds
    for (let i = 0; i < dust.length; i++) {
        const d = dust[i];
        d.theta += getVelocity(d.r) / (d.r * 18.0) * simSpeed;
        let dx = d.r * Math.cos(d.theta);
        let dz = d.r * Math.sin(d.theta);
        let dy = (rand() - 0.5) * 4 * Math.exp(-d.r / 80);
        let proj = cameraRotateAndProject(dx, dy, dz);
        if (proj) {
            renderList.push({
                type: 'dust',
                sx: proj.sx,
                sy: proj.sy,
                scale: proj.scale,
                zc: proj.zc,
                size: d.size * proj.scale
            });
        }
    }
    
    // 6. Add Supernovae
    for (let i = supernovae.length - 1; i >= 0; i--) {
        const sn = supernovae[i];
        sn.radius += (sn.maxRadius - sn.radius) * 0.08;
        sn.opacity = sn.life / 80.0;
        
        let proj = cameraRotateAndProject(sn.x, sn.y, sn.z);
        if (proj) {
            renderList.push({
                type: 'supernova',
                sx: proj.sx,
                sy: proj.sy,
                scale: proj.scale,
                zc: proj.zc,
                size: sn.radius * proj.scale,
                color: sn.color,
                opacity: sn.opacity,
                snRef: sn
            });
        }
        
        sn.life--;
        if (sn.life <= 0) {
            supernovae.splice(i, 1);
        }
    }
    
    // Dynamic Sorting (depth-buffer Painter's Algorithm)
    renderList.sort((a, b) => b.zc - a.zc);
    
    // Find closest star to cursor for inspection
    hoveredStarParticle = null;
    let minMouseDist = 12; // proximity threshold
    
    // Render sorted list
    for (let i = 0; i < renderList.length; i++) {
        const item = renderList[i];
        
        if (item.type === 'bh') {
            // SMBH Accretion disk radial back-glow
            let coreGlow = ctx.createRadialGradient(item.sx, item.sy, 2, item.sx, item.sy, item.size * 5);
            coreGlow.addColorStop(0, "rgba(255, 120, 0, 0.8)");
            coreGlow.addColorStop(0.2, "rgba(255, 60, 0, 0.4)");
            coreGlow.addColorStop(1, "rgba(11, 15, 25, 0)");
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size * 5, 0, 2 * Math.PI);
            ctx.fillStyle = coreGlow;
            ctx.fill();
            
            // Schwarzschild core
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size, 0, 2 * Math.PI);
            ctx.fillStyle = "#000000";
            ctx.shadowColor = "#ff5500";
            ctx.shadowBlur = 10 * item.scale;
            ctx.fill();
            ctx.shadowBlur = 0; // reset
            
        } else if (item.type === 'accretion') {
            ctx.globalCompositeOperation = "screen";
            ctx.fillStyle = item.color;
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size, 0, 2 * Math.PI);
            ctx.fill();
            ctx.globalCompositeOperation = "source-over";
            
        } else if (item.type === 'star') {
            // Check hover proximity
            let dx = item.sx - mousePos.x;
            let dy = item.sy - mousePos.y;
            let dist = Math.sqrt(dx*dx + dy*dy);
            if (dist < minMouseDist) {
                minMouseDist = dist;
                hoveredStarParticle = item;
            }
            
            // Star glow envelope
            ctx.fillStyle = item.color;
            ctx.globalAlpha = 0.16;
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size * 3.2, 0, 2 * Math.PI);
            ctx.fill();
            
            // Core
            ctx.globalAlpha = 1.0;
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size, 0, 2 * Math.PI);
            ctx.fill();
            
        } else if (item.type === 'nebula') {
            ctx.globalCompositeOperation = "screen";
            ctx.fillStyle = item.color;
            ctx.globalAlpha = item.color.includes("255") ? 0.045 : 0.035;
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size, 0, 2 * Math.PI);
            ctx.fill();
            ctx.globalAlpha = 1.0;
            ctx.globalCompositeOperation = "source-over";
            
        } else if (item.type === 'dust') {
            // Dark dust absorbs light (source-over composite draws normal occlusion)
            ctx.fillStyle = "rgba(18, 10, 4, 0.42)";
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size, 0, 2 * Math.PI);
            ctx.fill();
            
        } else if (item.type === 'supernova') {
            ctx.globalCompositeOperation = "screen";
            
            // Core flash
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, Math.max(1, 4 * item.opacity * item.scale), 0, 2 * Math.PI);
            ctx.fillStyle = "rgba(255, 255, 255, " + item.opacity + ")";
            ctx.fill();
            
            // Shockwave remnant shell
            ctx.beginPath();
            ctx.arc(item.sx, item.sy, item.size, 0, 2 * Math.PI);
            ctx.strokeStyle = item.color;
            ctx.lineWidth = 1.5;
            ctx.globalAlpha = item.opacity;
            ctx.stroke();
            
            ctx.globalAlpha = 1.0;
            ctx.globalCompositeOperation = "source-over";
        }
    }
    
    // Draw central black hole gravitational lensing halo
    if (bh_proj) {
        ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(bh_proj.sx, bh_proj.sy, bh_proj.scale * 30, 0, 2 * Math.PI);
        ctx.stroke();
    }
    
    // Core galactic diffuse star glow (bulge density envelope)
    if (bh_proj && morphology !== "Elliptical") {
        let coreDiff = ctx.createRadialGradient(bh_proj.sx, bh_proj.sy, 5, bh_proj.sx, bh_proj.sy, bh_proj.scale * 60);
        coreDiff.addColorStop(0, "rgba(241, 196, 15, 0.10)");
        coreDiff.addColorStop(0.5, "rgba(189, 0, 255, 0.03)");
        coreDiff.addColorStop(1, "rgba(11, 15, 25, 0)");
        ctx.fillStyle = coreDiff;
        ctx.beginPath();
        ctx.arc(bh_proj.sx, bh_proj.sy, bh_proj.scale * 60, 0, 2 * Math.PI);
        ctx.fill();
    }
    
    // Spontaneous Supernova checks
    let spontaneousChance = 0.0002;
    if (morphology === "Spiral") {
        spontaneousChance = 0.001 + 0.0018 * baryonicMass;
    } else if (morphology === "Lenticular") {
        spontaneousChance = 0.0003 + 0.0006 * baryonicMass;
    } else {
        spontaneousChance = 0.0001; // extremely rare Ia only
    }
    
    if (Math.random() < spontaneousChance && frameCounter %% 35 === 0) {
        const randIndex = Math.floor(Math.random() * stars.length);
        const star = stars[randIndex];
        const pos = getStar3DPosition(star);
        const isCC = star.mass >= 8.0 && morphology !== "Elliptical";
        triggerSupernova(pos.x, pos.y, pos.z, isCC);
    }
    
    // Draw HUD Instrumentation Overlays
    ctx.font = "10px monospace";
    ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
    
    // Grid indicators
    ctx.fillText("SYSTEM STATUS: ONLINE", 15, 20);
    ctx.fillText("GALAXY MODEL : " + morphology.toUpperCase(), 15, 32);
    ctx.fillText("CAMERA P/Y   : " + angleX.toFixed(2) + " / " + angleY.toFixed(2) + " rad", 15, 44);
    ctx.fillText("ZOOM SCALE   : " + zoom.toFixed(1) + "x", 15, 56);
    
    // Draw active Supernova logs HUD
    ctx.fillStyle = "#00ffcc";
    ctx.fillText("CC-SNe DETECTED (TYPE II): " + ccCount, 15, canvas.height - 52);
    ctx.fillStyle = "#ffaa00";
    ctx.fillText("IA-SNe DETECTED (TYPE IA): " + iaCount, 15, canvas.height - 38);
    
    // Spontaneous reset indicator
    ctx.fillStyle = "rgba(231, 76, 60, 0.5)";
    ctx.strokeStyle = "rgba(231, 76, 60, 0.2)";
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(15, canvas.height - 30, 100, 16, 3);
    else ctx.rect(15, canvas.height - 30, 100, 16);
    ctx.fill();
    ctx.stroke();
    ctx.fillStyle = "#ffffff";
    ctx.font = "bold 8px monospace";
    ctx.fillText("RESET DETECTIONS", 20, canvas.height - 19);
    
    // Controls instruction
    ctx.fillStyle = "rgba(255, 255, 255, 0.25)";
    ctx.font = "9px monospace";
    ctx.fillText("[DRAG TO ROTATE 3D | WHEEL TO ZOOM | CLICK STAR TO EXPLODE]", canvas.width - 340, canvas.height - 18);
    
    // Draw View preset buttons
    drawButton(15, 65, 70, 18, "[FACE-ON]");
    drawButton(90, 65, 70, 18, "[EDGE-ON]");
    drawButton(165, 65, 100, 18, orbitMode ? "[ORBITING]" : "[ORBIT OFF]", orbitMode ? "#00ffcc" : "rgba(255, 255, 255, 0.4)");
    
    // Render targeted Reticle and Inspector HUD
    if (hoveredStarParticle) {
        const star = hoveredStarParticle.starRef;
        
        // Target ring
        ctx.strokeStyle = "#00ffcc";
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.arc(hoveredStarParticle.sx, hoveredStarParticle.sy, hoveredStarParticle.size + 6 + Math.sin(Date.now() / 100) * 1.5, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Reticle ticks
        ctx.beginPath();
        ctx.moveTo(hoveredStarParticle.sx - hoveredStarParticle.size - 9, hoveredStarParticle.sy);
        ctx.lineTo(hoveredStarParticle.sx - hoveredStarParticle.size - 2, hoveredStarParticle.sy);
        ctx.moveTo(hoveredStarParticle.sx + hoveredStarParticle.size + 2, hoveredStarParticle.sy);
        ctx.lineTo(hoveredStarParticle.sx + hoveredStarParticle.size + 9, hoveredStarParticle.sy);
        ctx.moveTo(hoveredStarParticle.sx, hoveredStarParticle.sy - hoveredStarParticle.size - 9);
        ctx.lineTo(hoveredStarParticle.sx, hoveredStarParticle.sy - hoveredStarParticle.size - 2);
        ctx.moveTo(hoveredStarParticle.sx, hoveredStarParticle.sy + hoveredStarParticle.size + 2);
        ctx.lineTo(hoveredStarParticle.sx, hoveredStarParticle.sy + hoveredStarParticle.size + 9);
        ctx.stroke();
        
        // Probe HUD popup
        ctx.fillStyle = "rgba(9, 14, 25, 0.88)";
        ctx.strokeStyle = "rgba(0, 245, 212, 0.35)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        if (ctx.roundRect) ctx.roundRect(canvas.width - 230, 15, 215, 185, 8);
        else ctx.rect(canvas.width - 230, 15, 215, 185);
        ctx.fill();
        ctx.stroke();
        
        ctx.fillStyle = "#00ffcc";
        ctx.font = "bold 9px monospace";
        ctx.fillText("STELLAR PROBE OBSERVATION", canvas.width - 220, 28);
        ctx.strokeStyle = "rgba(0, 245, 212, 0.15)";
        ctx.beginPath();
        ctx.moveTo(canvas.width - 220, 34);
        ctx.lineTo(canvas.width - 25, 34);
        ctx.stroke();
        
        ctx.fillStyle = "#ffffff";
        ctx.font = "9px monospace";
        ctx.fillText("Spectral Class : " + star.spectralClass + "-Type Star", canvas.width - 220, 48);
        ctx.fillText("Stellar Mass   : " + star.mass.toFixed(2) + " Msun", canvas.width - 220, 62);
        ctx.fillText("Temperature    : " + star.temp.toLocaleString() + " K", canvas.width - 220, 76);
        ctx.fillText("Stellar Age    : " + star.age.toFixed(2) + " " + star.ageUnit, canvas.width - 220, 90);
        ctx.fillText("Metallicity    : [Fe/H] " + (star.feh >= 0 ? "+" : "") + star.feh.toFixed(2), canvas.width - 220, 104);
        
        const r_kpc = (star.r / 12.0).toFixed(2);
        const v_kms = getVelocity(star.r).toFixed(1);
        ctx.fillText("Galactic Rad   : " + r_kpc + " kpc", canvas.width - 220, 118);
        ctx.fillText("Orbital Velocity: " + v_kms + " km/s", canvas.width - 220, 132);
        
        // Draw risk metrics
        ctx.fillStyle = star.ccRisk.includes("CRITICAL") ? "#ff4444" : (star.iaRisk.includes("HIGH") ? "#ffaa00" : "#777777");
        ctx.fillText("CC-SN Risk     : " + star.ccRisk, canvas.width - 220, 152);
        ctx.fillStyle = star.iaRisk.includes("HIGH") ? "#ffaa00" : "#777777";
        ctx.fillText("Ia-SN Risk     : " + star.iaRisk, canvas.width - 220, 166);
        
        // Proximity indicator
        ctx.fillStyle = "rgba(255, 255, 255, 0.25)";
        ctx.fillText("[CLICK STAR TO DETONATE]", canvas.width - 220, 186);
    }
    
    // Draw Compass
    drawCompass();
    
    // Transients banners alerts
    if (hudTimer > 0) {
        ctx.fillStyle = hudMessage.includes("Type Ia") ? "rgba(255, 170, 0, 0.88)" : "rgba(0, 255, 204, 0.88)";
        ctx.fillRect(10, 10, canvas.width - 20, 20);
        ctx.font = "bold 9px monospace";
        ctx.fillStyle = "#0b0f19";
        ctx.fillText(hudMessage, 20, 23);
        hudTimer--;
    }
    
    requestAnimationFrame(animate);
}

function drawCompass() {
    let ox = canvas.width - 40;
    let oy = canvas.height - 40;
    
    // Compass labels X, Y, Z rotating with the camera
    let px = rotateVector(18, 0, 0);
    ctx.beginPath();
    ctx.moveTo(ox, oy); ctx.lineTo(ox + px.x, oy + px.y);
    ctx.strokeStyle = "#ff4d4d"; // Red X
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = "#ff4d4d";
    ctx.font = "bold 8px sans-serif";
    ctx.fillText("X", ox + px.x + 3, oy + px.y + 3);
    
    let py = rotateVector(0, 18, 0);
    ctx.beginPath();
    ctx.moveTo(ox, oy); ctx.lineTo(ox + py.x, oy + py.y);
    ctx.strokeStyle = "#4dff4d"; // Green Y
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = "#4dff4d";
    ctx.fillText("Y", ox + py.x + 3, oy + py.y + 3);
    
    let pz = rotateVector(0, 0, 18);
    ctx.beginPath();
    ctx.moveTo(ox, oy); ctx.lineTo(ox + pz.x, oy + pz.y);
    ctx.strokeStyle = "#4d94ff"; // Blue Z
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.fillStyle = "#4d94ff";
    ctx.fillText("Z", ox + pz.x + 3, oy + pz.y + 3);
}

function drawButton(x, y, w, h, label, activeColor) {
    ctx.fillStyle = "rgba(9, 14, 25, 0.85)";
    ctx.strokeStyle = activeColor || "rgba(255, 255, 255, 0.18)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, w, h, 4);
    else ctx.rect(x, y, w, h);
    ctx.fill();
    ctx.stroke();
    
    ctx.fillStyle = activeColor || "#ffffff";
    ctx.font = "bold 9px monospace";
    ctx.fillText(label, x + 8, y + 12);
}

animate();
</script>
</body>
</html>
"""

# ==============================================================================
# QUIZ DATA STRUCTURE & QUESTIONS (30 Shuffled MCQ Questions)
# ==============================================================================

QUIZ_QUESTIONS = [
    {
        "question": "1. In a flat $\\Lambda$CDM universe, which energy component dominates late-time cosmic expansion, and what is its dynamical effect?",
        "options": [
            "Matter density, leading to gravitational recollapse (a Big Crunch)",
            "Dark Energy (cosmological constant), leading to accelerated expansion",
            "Radiation density, leading to a decelerating expansion rate",
            "Spatial curvature, maintaining a static state"
        ],
        "correct": 1,
        "explanation": "In standard $\\Lambda$CDM cosmology, Dark Energy ($\\Omega_\\Lambda \\approx 0.7$) has a negative pressure equation of state ($w = -1$) that counteracts gravity, accelerating cosmic expansion at late times ($z \\lesssim 0.6$)."
    },
    {
        "question": "2. A photon is emitted from a galaxy at redshift $z = 1.0$. By what factor is its observed wavelength stretched compared to its rest-frame wavelength?",
        "options": [
            "Stretched by a factor of 1.5",
            "Stretched by a factor of 2.0",
            "Stretched by a factor of 1.0 (no change)",
            "Stretched by a factor of 0.5 (compressed)"
        ],
        "correct": 1,
        "explanation": "The observed wavelength is related to the rest-frame wavelength by the redshift relation: $\\lambda_{\\text{obs}} = \\lambda_{\\text{rest}} (1 + z)$. For $z = 1.0$, this yields $\\lambda_{\\text{obs}} = 2.0 \\lambda_{\\text{rest}}$."
    },
    {
        "question": "3. When generating a simulated isotropic galaxy distribution, why does sampling the declination angle (Dec) uniformly in degrees from -90 to +90 fail to produce a uniform spatial density?",
        "options": [
            "It causes galaxies to crowd unnaturally near the celestial poles (Dec = +/-90 degrees)",
            "It causes galaxies to cluster along the celestial equator (Dec = 0 degrees)",
            "It creates an artificial depletion at the polar coordinate singularities",
            "It introduces a radial bias relative to the observer's location"
        ],
        "correct": 0,
        "explanation": "The area element on a sphere is $dA = \\cos(\\text{Dec}) d\\text{RA} d\\text{Dec}$. Uniform sampling of the declination angle ignores the $\\cos(\\text{Dec})$ term, leading to an over-density of objects near the poles where the physical area per degree shrinks."
    },
    {
        "question": "4. Which physical mechanism is primarily responsible for the rapid quenching of star formation in massive galaxies ($M_* > M_c \\approx 10^{10.7} M_\\odot$), creating the exponential cutoff in the Stellar Mass Function?",
        "options": [
            "Supernova feedback",
            "Active Galactic Nuclei (AGN) feedback",
            "Stellar wind stripping",
            "Dark matter halo evaporation"
        ],
        "correct": 1,
        "explanation": "In high-mass galaxies, gas accretion onto the central Supermassive Black Hole releases jets and winds (AGN feedback) that heat or expel the cold gas reservoir, shutting down star formation and creating the exponential Schechter cutoff."
    },
    {
        "question": "5. Why is the faint-end slope ($\\alpha = -1.25$) of the Stellar Mass Function relatively flat compared to the dark matter halo mass function?",
        "options": [
            "Dwarf galaxies are dominated by active supermassive black holes",
            "Supernova feedback and UV heating eject gas from shallow potential wells",
            "Dwarf galaxies contain no dark matter to bind their gas",
            "Cosmic expansion prevents accretion in low-mass halos"
        ],
        "correct": 1,
        "explanation": "Dwarf galaxies reside in shallow gravitational potential wells with low escape velocities. Supernova energy injections and the background ionizing UV field easily heat and eject gas, limiting star formation efficiency."
    },
    {
        "question": "6. To generate mock galaxy masses following a Schechter mass function using a uniform random variable $U$ in $[0,1]$, which mathematical technique is applied?",
        "options": [
            "Pass $U$ through the Inverse Cumulative Distribution Function (Inverse CDF: $F^{-1}(U)$)",
            "Multiply U by the Hubble constant ($H_0$)",
            "Convolve U with a Gaussian measurement error",
            "Divide U by the critical density of the universe"
        ],
        "correct": 0,
        "explanation": "Under the Inverse Transform Sampling theorem, applying the inverse of the target Cumulative Distribution Function, $F^{-1}(U)$, to a uniformly distributed variable $U \\sim \\text{Uniform}(0, 1)$ yields values distributed according to the target probability density function."
    },
    {
        "question": "7. In Inverse Transform Sampling, drawing a random value $U = 0.50$ corresponds to returning which parameter of the target stellar mass distribution?",
        "options": [
            "The maximum stellar mass on the grid",
            "The mean stellar mass of the distribution",
            "The median stellar mass (50th percentile)",
            "The mode (most common mass) of the distribution"
        ],
        "correct": 2,
        "explanation": "By definition, the value of the physical variable where the cumulative distribution function $F(x) = 0.50$ is the median (50th percentile) of that distribution."
    },
    {
        "question": "8. Why must a stellar mass function, $\\Phi(M)$, be multiplied by $\\ln(10) M$ when evaluating it in logarithmic bins of $x = \\log_{10}(M)$?",
        "options": [
            "To account for stellar mass loss over cosmic time",
            "To conserve probability density under a change of variables (Jacobian transformation)",
            "To compensate for Malmquist bias in massive galaxies",
            "To align the mass scale with the Hubble parameter"
        ],
        "correct": 1,
        "explanation": "To preserve the total number of galaxies under coordinate transformation ($\\Phi(M) dM = \\Phi(x) dx$), we apply the derivative of the coordinate change: $dM/dx = d(10^x)/dx = 10^x \\ln(10) = M \\ln(10)$."
    },
    {
        "question": "9. In the bimodal distribution of galaxies, what is the term for the transitional region between the active 'Blue Cloud' and the passive 'Red Sequence'?",
        "options": [
            "The starburst sequence",
            "The Green Valley",
            "The dust gap",
            "The cosmic void"
        ],
        "correct": 1,
        "explanation": "The 'Green Valley' represents the transition zone containing galaxies that are undergoing active quenching, moving from the star-forming blue cloud to the quiescent red sequence."
    },
    {
        "question": "10. What empirical astrophysical scaling relation is represented by the Star Formation Main Sequence (SFMS)?",
        "options": [
            "The relationship between stellar mass and central black hole mass",
            "The correlation between a galaxy's stellar mass and its star formation rate",
            "The relationship between orbital velocity and galactic radius",
            "The ratio of gas mass to total dark matter mass"
        ],
        "correct": 1,
        "explanation": "The Star Formation Main Sequence (SFMS) is an empirical scaling relation showing that a galaxy's star formation rate is strongly correlated with its existing stellar mass, reflecting steady-state gas accretion growth."
    },
    {
        "question": "11. If a galaxy's Specific Star Formation Rate (sSFR) falls below $10^{-11} \\text{ yr}^{-1}$, what does this indicate about its evolutionary state?",
        "options": [
            "It is in an active starburst phase",
            "It is undergoing a major gas-rich merger",
            "It is quenched (passive/retired from forming stars)",
            "It is collapsing into a supermassive black hole"
        ],
        "correct": 2,
        "explanation": "An sSFR below $10^{-11} \\text{ yr}^{-1}$ indicates that the timescale to double the galaxy's stellar mass at its current star-formation rate exceeds the Hubble time, marking it as quenched."
    },
    {
        "question": "12. What does the typical scatter of ~0.3 dex around the Star Formation Main Sequence (SFMS) represent physically?",
        "options": [
            "Instrumental measurement noise in spectroscopic surveys",
            "Stochastic variations in star formation histories from episodic accretion and feedback",
            "Relativistic length contraction and lensing distortions",
            "Gravitational redshift effects near the galactic center"
        ],
        "correct": 1,
        "explanation": "The $\\approx 0.3$ dex scatter around the SFMS represents intrinsic physical variations driven by episodic gas inflows, feedback cycles, and minor mergers that perturb the star formation rate."
    },
    {
        "question": "13. What selection effect causes flux-limited astronomical catalogs to be dominated by intrinsically luminous objects at high redshifts?",
        "options": [
            "Eddington bias",
            "Lutz-Kelker bias",
            "Malmquist Bias",
            "Cosmic variance Selection"
        ],
        "correct": 2,
        "explanation": "Malmquist bias is the selection effect where distant objects in a flux-limited survey appear preferentially luminous because dimmer objects fall below the detection threshold."
    },
    {
        "question": "14. Why does a young, star-forming blue galaxy exhibit a much lower mass-to-light ratio than an old red galaxy of the same stellar mass?",
        "options": [
            "Blue galaxies are dominated by massive, hot O and B stars that emit high luminosity",
            "Red galaxies contain significantly more dark matter in their cores",
            "Blue galaxies are completely devoid of interstellar dust obscuration",
            "Red galaxies are expanding away from the observer at a faster rate"
        ],
        "correct": 0,
        "explanation": "Young blue galaxies contain short-lived, highly luminous spectral class O and B stars ($L \\propto M^4$). Despite their low mass fraction, they dominate the light output, lowering the mass-to-light ratio."
    },
    {
        "question": "15. In a galaxy survey with a spectroscopic limit of apparent magnitude $m = 23.5$, why is a galaxy with $m = 24.8$ excluded?",
        "options": [
            "Its radial velocity exceeds the Hubble flow limit",
            "It is below the detection threshold because it is too faint (higher apparent magnitude)",
            "It is classified as a foreground stellar contaminant",
            "Its light has been completely absorbed by cosmic dust"
        ],
        "correct": 1,
        "explanation": "Apparent magnitude is an inverse logarithmic scale; larger magnitudes represent dimmer objects. A galaxy with $m = 24.8$ is fainter than the survey limit of $23.5$ and falls below the detection threshold."
    },
    {
        "question": "16. By definition, absolute magnitude ($M$) is the apparent magnitude ($m$) a celestial object would exhibit if observed from a standard distance of:",
        "options": [
            "1 Astronomical Unit (AU)",
            "1 Megaparsec (Mpc)",
            "10 parsecs",
            "1 Light-Year"
        ],
        "correct": 2,
        "explanation": "Absolute magnitude scales out distance dependence by calculating the apparent magnitude an object would have at a standardized distance of exactly 10 parsecs."
    },
    {
        "question": "17. Which stellar spectral class corresponds to the hottest, most massive main-sequence stars that terminate as core-collapse supernovae?",
        "options": [
            "M-class (red dwarfs)",
            "K-class (orange dwarfs)",
            "A-class (white stars)",
            "O-class (blue supergiants)"
        ],
        "correct": 3,
        "explanation": "O-type stars are the most massive ($M \\ge 16 M_\\odot$) and hottest ($T > 30,000\\text{ K}$) stars on the main sequence, ending their short lifetimes as core-collapse supernovae."
    },
    {
        "question": "18. Which class of supernova is triggered by the thermonuclear runaway of a carbon-oxygen white dwarf exceeding the Chandrasekhar limit in a binary system?",
        "options": [
            "Type II Supernova",
            "Type Ia Supernova",
            "Kilonova",
            "Core-Collapse Supernova"
        ],
        "correct": 1,
        "explanation": "A Type Ia supernova is a thermonuclear explosion occurring when a carbon-oxygen white dwarf accretes enough mass to exceed the Chandrasekhar limit ($1.4 M_\\odot$), causing a complete runaway fusion event."
    },
    {
        "question": "19. Which event is triggered when a star with an initial mass $M \\ge 8 M_\\odot$ forms an iron core that collapses under gravity?",
        "options": [
            "Type II Supernova (Core-Collapse)",
            "Type Ia Supernova",
            "Helium Flash",
            "Planetary Nebula ejection"
        ],
        "correct": 0,
        "explanation": "Stars with initial masses $\\ge 8 M_\\odot$ fuse elements up to iron. Because iron fusion is endothermic, the core loses pressure support, collapses into a neutron star or black hole, and ejects the outer layers in a Type II supernova."
    },
    {
        "question": "20. What component of spiral galaxies is required to explain the flat rotation curves observed at large radii, where visible matter density is low?",
        "options": [
            "A central supermassive black hole",
            "A massive, extended Dark Matter Halo",
            "Interstellar magnetic fields",
            "Peculiar velocities from metric expansion"
        ],
        "correct": 1,
        "explanation": "Keplerian rotation speeds should decline at large radii where visible matter is sparse ($v \\propto r^{-0.5}$). Observed flat rotation curves imply the presence of a massive, extended dark matter halo."
    },
    {
        "question": "21. Using Hubble's Law ($v = H_0 \\cdot d$) with a Hubble constant $H_0 = 70\\text{ km/s/Mpc}$, what is the recession velocity of a galaxy at a distance of 2 Megaparsecs?",
        "options": [
            "70 km/s",
            "140 km/s",
            "35 km/s",
            "280 km/s"
        ],
        "correct": 1,
        "explanation": "Hubble's Law ($v = H_0 \\cdot d$) relates recession velocity to distance. With $H_0 = 70\\text{ km/s/Mpc}$ and $d = 2\\text{ Mpc}$, the velocity is $70 \\times 2 = 140\\text{ km/s}$."
    },
    {
        "question": "22. What is the primary physical cause of cosmological redshift in the spectrum of distant galaxies?",
        "options": [
            "Doppler shifts from galaxies moving physically through static space",
            "Scattering of light by interstellar and intergalactic dust",
            "The expansion of the space metric itself stretching light wavelengths during propagation",
            "Gravitational time dilation near massive galaxy clusters"
        ],
        "correct": 2,
        "explanation": "Cosmological redshift arises because the expanding space metric stretches the wavelength of traveling photons as they propagate between galaxies over cosmological time."
    },
    {
        "question": "23. What is the term for the cosmological postulate that, on sufficiently large scales, the universe is homogeneous and isotropic?",
        "options": [
            "The Cosmological Principle",
            "The Copernican Principle",
            "The Equivalence Principle",
            "The Einstein Postulate"
        ],
        "correct": 0,
        "explanation": "The Cosmological Principle states that on sufficiently large scales (~100 Mpc), the universe is homogeneous (looks the same at all locations) and isotropic (looks the same in all directions)."
    },
    {
        "question": "24. What is the expression for the Schwarzschild radius ($R_s$), which defines the event horizon of a spherically symmetric, non-rotating black hole?",
        "options": [
            "$R_s = GM / c^2$",
            "$R_s = 2GM / c^2$",
            "$R_s = GM / (2c^2)$",
            "$R_s = \\sqrt{GM / c}$"
        ],
        "correct": 1,
        "explanation": "The event horizon of a non-rotating Schwarzschild black hole of mass $M$ is defined by the radius $R_s = 2GM/c^2$, where the escape velocity equals the speed of light."
    },
    {
        "question": "25. Which light element was synthesized in trace amounts during Big Bang Nucleosynthesis, in addition to hydrogen and helium?",
        "options": [
            "Carbon",
            "Iron",
            "Lithium",
            "Oxygen"
        ],
        "correct": 2,
        "explanation": "Big Bang Nucleosynthesis (BBN) in the early universe synthesized primarily isotopes of hydrogen, helium, and a trace abundance of lithium-7."
    },
    {
        "question": "26. Excluding local peculiar velocities, how does the comoving distance between two distant galaxies change as the universe expands?",
        "options": [
            "It increases proportionally to the scale factor $a(t)$",
            "It remains constant by definition",
            "It decreases due to local gravitational attraction",
            "It increases exponentially due to dark energy"
        ],
        "correct": 1,
        "explanation": "Comoving distance factors out the universal expansion scale factor $a(t)$. Consequently, the comoving separation between two co-expanding galaxies remains constant over time."
    },
    {
        "question": "27. Why does stellar and supernova feedback suppress star formation in dwarf galaxies much more effectively than in massive galaxies?",
        "options": [
            "Dwarf galaxies lack dark matter halos entirely",
            "Dwarf galaxies have shallow potential wells and low escape velocities",
            "Dwarf galaxies have higher star formation efficiency",
            "Dwarf galaxies are closer to the cosmic web filaments"
        ],
        "correct": 1,
        "explanation": "Because of their lower total mass, dwarf galaxies have lower escape velocities ($v_{\\text{esc}} \\propto \\sqrt{M/R}$). Supernova winds can easily escape their shallow potential wells, ejecting the gas supply."
    },
    {
        "question": "28. The Star Formation Main Sequence (SFMS) has a sub-linear slope ($b \\approx 0.8$) in $\\log \\text{SFR}$ vs $\\log M_*$. What does this indicate about galaxy growth efficiency?",
        "options": [
            "Massive galaxies form stars more efficiently per unit mass",
            "Low-mass galaxies form stars more efficiently per unit mass (higher $\\text{sSFR}$)",
            "Star formation rates are independent of stellar mass",
            "Lower-mass galaxies are fully quenched"
        ],
        "correct": 1,
        "explanation": "A slope of $b \\approx 0.8$ yields a Specific Star Formation Rate (sSFR = SFR/$M_*$) that scales as $\\text{sSFR} \\propto M_*^{-0.2}$. This negative exponent means lower-mass galaxies are forming stars more rapidly relative to their mass than higher-mass galaxies."
    },
    {
        "question": "29. Two identical stars are observed, with Star B situated exactly 10 times further away than Star A. By how many magnitudes fainter will Star B appear?",
        "options": [
            "2.5 magnitudes fainter",
            "5.0 magnitudes fainter",
            "10.0 magnitudes fainter",
            "100.0 magnitudes fainter"
        ],
        "correct": 1,
        "explanation": "Using the distance modulus relation: $m_B - m_A = 5 \\log_{10}(d_B / d_A)$. For a distance ratio of 10, the difference in apparent magnitude is $5 \\log_{10}(10) = 5.0$ magnitudes dimmer."
    },
    {
        "question": "30. Why did Big Bang Nucleosynthesis fail to synthesize carbon, leaving the early universe with only light elements?",
        "options": [
            "The nuclear binding energy of carbon is unstable under any conditions",
            "The universe cooled and diluted too rapidly to permit the triple-alpha helium fusion process",
            "Dark matter particles absorbed the required free neutrons",
            "Strong stellar winds from early stars dispersed the helium nuclei"
        ],
        "correct": 1,
        "explanation": "Carbon synthesis requires the triple-alpha process, where three helium nuclei collide. This requires high densities and temperatures. The rapid expansion of the early universe cooled and diluted the plasma before these three-body collisions could occur."
    }
]

# Sidebar navigation
st.sidebar.markdown("---")
st.sidebar.subheader("🚀 Navigation")
workspace_page = st.sidebar.radio("Select Workspace Page:", ["3D Galaxy Physics Simulator", "Interactive Quiz: Cosmic Challenge"])

if workspace_page == "3D Galaxy Physics Simulator":

    # ==============================================================================
    # 3D GALAXY SIMULATION PAGE
    # ==============================================================================

    st.title("🌌 Stellar Trace: Astrophysics Simulation Dashboard")
    st.markdown("---")

    # Setup sidebar for model inputs and parameter configuration
    st.sidebar.header("🔧 Model Configuration")
    st.sidebar.markdown("Configure the parameters below to update the simulated galaxy environment and evaluate classification probability.")

    # Section 1: Stellar Target Parameters
    st.sidebar.subheader("Host Galaxy Parameters")
    morphology = st.sidebar.selectbox("Morphology Class", ["Spiral (Sbc)", "Lenticular (S0)", "Elliptical (E3)"])
    log_m = st.sidebar.slider("Stellar Mass: log10(M*/Msun)", min_value=7.0, max_value=12.0, value=10.1, step=0.1)
    z = st.sidebar.slider("Redshift (z)", min_value=0.01, max_value=0.5, value=0.1, step=0.01)

    # Section 2: Dark Matter Halo Parameters
    st.sidebar.subheader("Dark Matter Halo Parameters")
    dm_fraction = st.sidebar.slider("Dark Matter Fraction (f_DM)", min_value=0.0, max_value=0.95, value=0.6, step=0.05)
    core_radius = st.sidebar.slider("Halo Core Radius (kpc)", min_value=0.5, max_value=5.0, value=2.0, step=0.1)

    # Section 3: Central SMBH Parameters
    st.sidebar.subheader("Central Supermassive Black Hole")
    log_mbh = st.sidebar.slider("SMBH Mass: log10(M_bh/Msun)", min_value=5.0, max_value=10.0, value=8.0, step=0.5)

    # Section 4: Performance & Animation
    st.sidebar.subheader("Simulation Controls")
    particle_count = st.sidebar.slider("Stellar Particle Density", min_value=400, max_value=1500, value=1000, step=50)
    sim_speed = st.sidebar.slider("Simulation Speed Multiplier", min_value=0.2, max_value=2.0, value=1.0, step=0.1)

    # Ingest inputs and predict host probability via MLP
    prob, predicted_sfr = predict_host_probability(log_m, z, morphology)

    # Render Top-Level Glassmorphic Metrics Headers
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Galaxy Classification</div>
            <div class="metric-value val-morph">{morphology}</div>
            <div class="metric-desc">Configures stellar population age, Initial Mass Function (IMF) bounds, gas nebulae, and dust obscuration features.</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">CC-SN Host Probability</div>
            <div class="metric-value val-prob">{prob * 100:.2f}%</div>
            <div class="metric-desc">MLP neural network host probability based on mass and morphological star-forming activity (SSFR).</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Star Formation Rate</div>
            <div class="metric-value val-sfr">{10**predicted_sfr:.4f} M☉/yr</div>
            <div class="metric-desc">Calculated by applying the morphological offset to the Star-Forming Main Sequence (SFMS) baseline.</div>
        </div>
        """, unsafe_allow_html=True)

    # Render main panel split layout
    col1, col2 = st.columns([1.1, 1], gap="large")

    with col1:
        st.subheader("Galaxy Dynamics & 3D Orbit Simulation")
        st.markdown("Interactive 3D physics simulation. Outer stellar velocities are driven by the invisible dark matter halo, while the inner core orbital velocities are dominated by the supermassive black hole cusp.")
        
        # Scale baryonic mass parameter for javascript coordinate mapping
        scaled_baryonic_mass = 10 ** (log_m - 10.0)
        
        # Ingest parameters and display HTML5 Canvas component
        html_code = HTML_TEMPLATE % (
            scaled_baryonic_mass, 
            dm_fraction, 
            core_radius, 
            log_mbh, 
            morphology.split()[0], 
            particle_count, 
            sim_speed
        )
        components.html(html_code, height=520)
        
        st.markdown("""
        > [!TIP]
        > **Interactive Probe Controls:** Drag the canvas to tilt the galaxy in 3D. Hover your cursor over individual stars to probe their physical characteristics (temperature, class, mass, age, metallicity). Click to trigger localized supernovae!
        """)

    with col2:
        st.subheader("Galaxy Rotation Curve Analysis")
        st.markdown("Analytical velocity profile derived from central SMBH gravity, Keplerian baryonic mass, and flat dark matter halo potential. Illustrates how dark matter resolves the winding dilemma.")
        
        # Compute rotation curve arrays
        r_kpc = np.linspace(0.1, 15.0, 200) # Radius in kpc
        
        # SMBH Keplerian Spike component
        v_bh = 95.0 * np.sqrt((10 ** (log_mbh - 8.0)) / (r_kpc + 0.01))
        
        # Baryonic contribution v_bar (Keplerian decline)
        v_bar = 180.0 * np.sqrt(scaled_baryonic_mass / (r_kpc + 0.3))
        
        # Dark matter halo contribution v_dm
        v_dm = 230.0 * np.sqrt(dm_fraction * r_kpc**2 / (r_kpc**2 + core_radius**2 + 0.1))
        
        # Total rotation velocity
        v_tot = np.sqrt(v_bh**2 + v_bar**2 + v_dm**2)
        
        # Construct interactive Plotly line chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=r_kpc, y=v_bh, name='Central SMBH Kepler Cusp', line=dict(color='#f1c40f', dash='dashdot', width=1.5)))
        fig.add_trace(go.Scatter(x=r_kpc, y=v_bar, name='Baryonic Component (Stars/Gas)', line=dict(color='#e74c3c', dash='dot', width=2)))
        fig.add_trace(go.Scatter(x=r_kpc, y=v_dm, name='Dark Matter Halo Component', line=dict(color='#2ecc71', dash='dash', width=2)))
        fig.add_trace(go.Scatter(x=r_kpc, y=v_tot, name='Total Velocity Profile v(r)', line=dict(color='#3498db', width=3.2)))
        
        fig.update_layout(
            xaxis_title="Radius r (kpc)",
            yaxis_title="Orbital Velocity v (km/s)",
            template="plotly_dark",
            legend=dict(x=0.42, y=0.96, bgcolor='rgba(10,15,25,0.75)', font=dict(size=9)),
            margin=dict(l=40, r=20, t=10, b=40),
            height=380,
            yaxis=dict(range=[0, 360])
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Physical diagnostics text
        st.markdown("""
        ### Physical Diagnostics
        *   **SMBH Cusp:** The central Supermassive Black Hole dominates gravity at $r < 0.5$ kpc, causing a steep velocity spike. Adjusting the *SMBH Mass* controls the height and extent of this spike.
        *   **Baryonic Dominance:** Elevating the *Stellar Mass* raises the intermediate Keplerian peak, representing the stellar density profile of the bulge.
        *   **Dark Matter Halo:** Adjusting the *Dark Matter Fraction* ($f_{\\text{DM}}$) controls the flatness of the outer curve. Without dark matter, orbital speeds would drop in Keplerian fashion, causing galaxy outer arms to shear.
        """)

else:
    # ==============================================================================
    # INTERACTIVE GAMIFIED QUIZ PAGE: COSMIC CHALLENGE (30 Questions)
    # ==============================================================================

    st.title("🚀 Stellar Trace: Cosmic Data Science Quiz")
    st.markdown("---")

    # Initialize quiz states in st.session_state
    if "quiz_started" not in st.session_state:
        st.session_state.quiz_started = False
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "current_q" not in st.session_state:
        st.session_state.current_q = 0
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "quiz_streak" not in st.session_state:
        st.session_state.quiz_streak = 0
    if "max_streak" not in st.session_state:
        st.session_state.max_streak = 0
    if "quiz_lives" not in st.session_state:
        st.session_state.quiz_lives = 3
    if "quiz_start_time" not in st.session_state:
        st.session_state.quiz_start_time = 0.0
    if "user_answers" not in st.session_state:
        st.session_state.user_answers = [None] * len(QUIZ_QUESTIONS)
    if "correct_flags" not in st.session_state:
        st.session_state.correct_flags = [None] * len(QUIZ_QUESTIONS)
    if "answer_submitted_q" not in st.session_state:
        st.session_state.answer_submitted_q = False

    def restart_quiz():
        st.session_state.quiz_started = True
        st.session_state.quiz_submitted = False
        st.session_state.current_q = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_streak = 0
        st.session_state.max_streak = 0
        st.session_state.quiz_lives = 3
        st.session_state.quiz_start_time = time.time()
        st.session_state.user_answers = [None] * len(QUIZ_QUESTIONS)
        st.session_state.correct_flags = [None] * len(QUIZ_QUESTIONS)
        st.session_state.answer_submitted_q = False

    # Check Timer expiry (auto-submit if time exceeds 1 hour)
    quiz_timeout = False
    time_elapsed_str = ""
    if st.session_state.quiz_started and not st.session_state.quiz_submitted:
        elapsed = time.time() - st.session_state.quiz_start_time
        remaining = 3600 - elapsed
        if remaining <= 0:
            st.session_state.quiz_submitted = True
            quiz_timeout = True
        else:
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            time_elapsed_str = f"⏱️ TIME REMAINING: {mins:02d}:{secs:02d}"

    # 1. Landing / Start Screen
    if not st.session_state.quiz_started:
        st.subheader("Prepare for Orbit, Commander! 🛰️")
        st.markdown("""
        Welcome to the **Stellar Trace: Cosmic Data Science Challenge**! 
        This is a gamified interactive quiz designed to evaluate and solidify your knowledge of **Tasks 1 to 7** alongside core observational astronomy.

        ### 📋 Flight Parameters
        * **Total Questions:** 30 Multi-Choice Questions
        * **Time Limit:** 1 Hour (60 Minutes)
        * **Starting Health:** ❤️❤️❤️ (3 Lives). Answering incorrectly blows a fuse (losses a life).
        * **Point Multipliers:** Correct answers give **100 base points**. Maintain a streak to trigger the **Streak Fire bonus (+10 pts per streak level)**!
        * **Course Topics Covered:**
          * **Task 1:** Cosmogony, Space expansion, Comoving/Luminosity distances, sin(Dec) isotropic distributions, Comoving Volume conservation.
          * **Task 2 & 3:** The Schechter Stellar Mass Function, Supernova vs. AGN Feedback, log-space Jacobian scaling, gravitational potential wells, and Inverse CDF Sampling.
          * **Task 4 & 5:** Star Formation Main Sequence (SFMS) curves, sSFR cuts, cosmic variance (0.3 dex scatter), and population bimodal distribution.
          * **Task 6 & 7:** Catalog export columns alignment, Malmquist Bias (limiting magnitudes), distance modulus calculations, and stellar Mass-to-Light ratios.
          * **Basic Astronomy:** Black holes Schwarzschild radius, stellar classifications (O, B, A, F, G, K, M), and Big Bang nucleosynthesis constraints.
        """)
        
        st.markdown("---")
        if st.button("🚀 IGNITE THRUSTERS & START QUIZ", use_container_width=True):
            restart_quiz()
            st.rerun()

    # 2. Mission Failed Screen (Lives = 0 or Timeout)
    elif (st.session_state.quiz_lives <= 0 or quiz_timeout) and not st.session_state.quiz_submitted:
        st.session_state.quiz_submitted = True
        st.rerun()

    # 3. Active Quiz Question Screen
    elif st.session_state.quiz_started and not st.session_state.quiz_submitted:
        # Header HUD
        col_hud1, col_hud2, col_hud3 = st.columns(3)
        with col_hud1:
            # Hearts representation
            hearts = "❤️" * st.session_state.quiz_lives + "🖤" * (3 - st.session_state.quiz_lives)
            st.markdown(f"#### Health: <span class='quiz-hud-val' style='color:#e74c3c;'>{hearts}</span>", unsafe_allow_html=True)
        with col_hud2:
            st.markdown(f"#### Score: <span class='quiz-hud-val' style='color:#00f5d4;'>{st.session_state.quiz_score} pts</span>", unsafe_allow_html=True)
        with col_hud3:
            streak_fire = f"{st.session_state.quiz_streak} 🔥" if st.session_state.quiz_streak > 0 else "0"
            st.markdown(f"#### Streak: <span class='quiz-hud-val' style='color:#f1c40f;'>{streak_fire}</span>", unsafe_allow_html=True)
            
        st.markdown(f"**{time_elapsed_str}**")
        st.progress((st.session_state.current_q) / len(QUIZ_QUESTIONS))
        st.markdown(f"**Question {st.session_state.current_q + 1} of {len(QUIZ_QUESTIONS)}**")
        
        # Display active question
        q_idx = st.session_state.current_q
        q = QUIZ_QUESTIONS[q_idx]
        
        st.markdown(f"""
        <div class="quiz-question-box">
            <h3 style="margin-top:0; color:#ffffff;">{q['question']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Options selection
        # Disable options if already submitted for this question
        selected_option = st.radio(
            "Select the correct physical profile:",
            q['options'],
            index=None if st.session_state.user_answers[q_idx] is None else q['options'].index(st.session_state.user_answers[q_idx]),
            disabled=st.session_state.answer_submitted_q,
            key=f"q_radio_{q_idx}"
        )
        
        # Action Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1.2])
        
        with col_btn1:
            if st.session_state.current_q > 0:
                if st.button("⬅️ PREVIOUS", use_container_width=True):
                    st.session_state.current_q -= 1
                    st.session_state.answer_submitted_q = (st.session_state.user_answers[st.session_state.current_q] is not None)
                    st.rerun()
                    
        with col_btn2:
            # Submit button
            if not st.session_state.answer_submitted_q:
                if st.button("🚀 SUBMIT ANSWER", type="primary", use_container_width=True, disabled=(selected_option is None)):
                    st.session_state.user_answers[q_idx] = selected_option
                    st.session_state.answer_submitted_q = True
                    
                    # Grade answer
                    correct_idx = q['correct']
                    correct_answer_text = q['options'][correct_idx]
                    
                    if selected_option == correct_answer_text:
                        st.session_state.correct_flags[q_idx] = True
                        st.session_state.quiz_streak += 1
                        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.quiz_streak)
                        st.session_state.quiz_score += 100 + (st.session_state.quiz_streak * 10)
                        st.session_state.last_feedback = "CORRECT"
                    else:
                        st.session_state.correct_flags[q_idx] = False
                        st.session_state.quiz_lives -= 1
                        st.session_state.quiz_streak = 0
                        st.session_state.last_feedback = "INCORRECT"
                        
                    st.rerun()
            else:
                # Next button
                if st.session_state.current_q < len(QUIZ_QUESTIONS) - 1:
                    if st.button("NEXT QUESTION ➡️", use_container_width=True):
                        st.session_state.current_q += 1
                        st.session_state.answer_submitted_q = (st.session_state.user_answers[st.session_state.current_q] is not None)
                        st.rerun()
                else:
                    if st.button("🏁 FINISH & SUBMIT RESULTS", use_container_width=True):
                        st.session_state.quiz_submitted = True
                        st.rerun()
                        
        with col_btn3:
            # Sync countdown display
            if st.button("⏱️ SYNC TIMER", use_container_width=True):
                st.rerun()
                
        # Show instant feedback overlay
        if st.session_state.answer_submitted_q:
            is_correct = st.session_state.correct_flags[q_idx]
            correct_val = q['options'][q['correct']]
            if is_correct:
                st.success(f"💥 **CORRECT!** Streak: {st.session_state.quiz_streak} 🔥 (+{100 + st.session_state.quiz_streak * 10} pts)")
            else:
                st.error(f"❌ **INCORRECT!** Lost 1 life. The correct answer was: **{correct_val}**")
                
            st.info(f"📚 **Cosmological Explanation:** {q['explanation']}")

    # 4. Final Scoring Dashboard Screen
    elif st.session_state.quiz_submitted:
        st.subheader("Quiz Results Submitted! 🛸")
        
        # Calculate statistics
        answered_count = sum(1 for ans in st.session_state.user_answers if ans is not None)
        correct_count = sum(1 for flag in st.session_state.correct_flags if flag is True)
        accuracy = (correct_count / len(QUIZ_QUESTIONS)) * 100 if len(QUIZ_QUESTIONS) > 0 else 0.0
        
        # Custom grading title based on score
        if st.session_state.quiz_lives <= 0:
            grade_title = "MISSION FAILED: SHIP DESTROYED IN SUPERNOVA 💥"
            grade_color = "#ff4d4d"
            grade_desc = "Your ship ran out of thermal shielding (lives) while exploring dense gravitational regimes. Go back to the notebooks, review the physics, and try again!"
        elif accuracy >= 90.0:
            grade_title = "SUMMA CUM LAUDE (HIGH HONORS) 🌟"
            grade_color = "#00f5d4"
            grade_desc = "Astrophysical Mastermind! You have demonstrated absolute precision in cosmology, Schechter calculations, regression fits, and selection biases."
        elif accuracy >= 80.0:
            grade_title = "MAGNA CUM LAUDE (HONORS) 🎖️"
            grade_color = "#3b82f6"
            grade_desc = "Expert Space Commander! Exceptional command of galaxies statistics, empirical main sequences, and observational selection effects."
        elif accuracy >= 70.0:
            grade_title = "CUM LAUDE (PASS WITH MERIT) 🎓"
            grade_color = "#f1c40f"
            grade_desc = "Successful Flight! Clean grasp of basic astronomy and population synthesis model equations."
        elif accuracy >= 50.0:
            grade_title = "SATISFACTORY PASS 📝"
            grade_color = "#9ca3af"
            grade_desc = "Pass. Grasp of core elements, but requires review of the feedback mechanisms and selection biases before entering Phase 2."
        else:
            grade_title = "ACADEMIC REVIEW REQUIRED 📚"
            grade_color = "#ff4d4d"
            grade_desc = "Below passing threshold. Re-examine redshift geometries, SMF Jacobian transformations, and apparent magnitude integrations."

        # Display Summary cards
        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Final Score</div>
                <div class="metric-value" style="color:#00f5d4;">{st.session_state.quiz_score} pts</div>
                <div class="metric-desc">Includes base points plus streak multipliers.</div>
            </div>
            """, unsafe_allow_html=True)
        with sc2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Accuracy</div>
                <div class="metric-value" style="color:#bd00ff;">{accuracy:.1f}%%</div>
                <div class="metric-desc">{correct_count} correct out of {len(QUIZ_QUESTIONS)} questions.</div>
            </div>
            """, unsafe_allow_html=True)
        with sc3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Max Streak</div>
                <div class="metric-value" style="color:#f1c40f;">{st.session_state.max_streak} 🔥</div>
                <div class="metric-desc">Highest consecutive correct streak achieved.</div>
            </div>
            """, unsafe_allow_html=True)
        with sc4:
            lives_hud = "❤️" * st.session_state.quiz_lives if st.session_state.quiz_lives > 0 else "DESTROYED 💥"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">Vessel Integrity</div>
                <div class="metric-value" style="color:#e74c3c; font-size:26px; padding-top:12px;">{lives_hud}</div>
                <div class="metric-desc">Remaining shields (lives) out of 3.</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="border: 1px solid {grade_color}44; border-radius:12px; padding:24px; background-color:rgba(10, 15, 25, 0.5); margin-bottom:30px;">
            <h2 style="margin-top:0; color:{grade_color};">{grade_title}</h2>
            <p style="color:#ffffff; margin:0; line-height:1.6;">{grade_desc}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 RESTART COSMIC CHALLENGE", use_container_width=True):
            restart_quiz()
            st.rerun()

        # Detailed Question Review Panel
        st.markdown("---")
        st.subheader("📝 Cosmic Flight Log: Detailed Review")
        
        for idx, q in enumerate(QUIZ_QUESTIONS):
            user_ans = st.session_state.user_answers[idx]
            correct_ans = q['options'][q['correct']]
            is_correct = st.session_state.correct_flags[idx]
            
            with st.expander(
                f"Question {idx + 1}: " + ("✅ Correct" if is_correct else ("❌ Incorrect" if user_ans is not None else "⚠️ Unanswered")),
                expanded=False
            ):
                st.markdown(f"### {q['question']}")
                st.markdown(f"**Your Selected Answer:** {user_ans if user_ans else '*(No answer submitted)*'}")
                st.markdown(f"**Correct Answer:** {correct_ans}")
                
                if is_correct:
                    st.success("Correct!")
                else:
                    st.error("Incorrect or Unanswered")
                    
                st.info(f"📚 **Cosmological Explanation:** {q['explanation']}")
