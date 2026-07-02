# ==============================================================================
# 🎨 PREMIUM DIAGNOSTIC & PUBLICATION-GRADE PLOTS FOR MOCK POPULATION STEP
# ==============================================================================
# This standalone script generates four highly useful and visually stunning 
# diagnostic plots that analyze the physical properties and selection biases
# of your mock galaxy population:
#
# Plot 1: Stellar Mass Distribution (PDF) — Before vs. After Magnitude Cut (Telescope Bias)
# Plot 2: SFR vs. Stellar Mass Hexbin — Visualizing the Main Sequence & Quenched Valley
# Plot 3: Color-Mass Diagram — The "Blue Cloud", "Green Valley", & "Red Sequence"
# Plot 4: Observed Apparent Magnitude vs. Mass — Showing the exact 23.5 Cutoff boundary
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d
import seaborn as sns

# Set beautiful style parameters for high-end scientific figures
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Helvetica', 'Arial'],
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'grid.alpha': 0.4,
    'grid.linestyle': ':'
})

# ==============================================================================
# 1. PHYSICAL MODELS
# ==============================================================================
H0, Om0, Olam = 70.0, 0.3, 0.7
c_speed = 299792.458

def luminosity_distance(z):
    if z == 0: return 0.0
    steps = 500
    z_grid = np.linspace(0, z, steps)
    dz = z / (steps - 1)
    ez = np.sqrt(Om0 * (1 + z_grid)**3 + Olam)
    integral = np.sum(1.0 / ez) * dz
    return (c_speed / H0) * integral * (1 + z)

def schechter_smf(log_mstar, phi_c=10**(-2.44), log_mc=10.8, alpha=-1.2):
    mstar = 10**log_mstar
    mc = 10**log_mc
    return np.log(10) * phi_c * (mstar / mc)**(alpha + 1) * np.exp(-mstar / mc)

def sample_mock_generation(num_samples=50000, target_z=0.3, rmag_limit=23.5):
    # Sample masses
    logm_min, logm_max = 6.5, 12.5
    m_grid = np.linspace(logm_min, logm_max, 5000)
    pdf = schechter_smf(m_grid)
    cdf = cumtrapz(pdf, m_grid, initial=0)
    cdf /= cdf[-1]
    inv_cdf = interp1d(cdf, m_grid, bounds_error=False, fill_value=(logm_min, logm_max))
    log_mstar = inv_cdf(np.random.rand(num_samples))
    
    # Sample SFR
    log_sfr = np.zeros(num_samples)
    sfr_mode = 0.8 * (log_mstar - 10.0) + 0.2 + 0.5 * target_z
    for i in range(num_samples):
        m = log_mstar[i]
        p_quenched = 1.0 / (1.0 + np.exp(-(m - 10.5) / 0.4))
        if np.random.rand() < p_quenched:
            log_sfr[i] = np.random.normal(loc=-2.2, scale=0.8)
        else:
            log_sfr[i] = np.random.normal(loc=sfr_mode[i], scale=0.3)
            
    # Sample Color (g - r)
    ssfr = log_sfr - log_mstar
    color_gr = np.clip(0.5 - 0.25 * (ssfr + 10.0), -0.1, 1.0)
    color_gr += np.random.normal(loc=0.0, scale=0.06, size=num_samples)
    
    # Mass-to-light ratios
    log_mtolg = 1.5 * color_gr - 0.7
    log_mtolr = log_mtolg - (color_gr / 2.5)
    
    # Magnitudes
    d_l = luminosity_distance(target_z)
    Mr_sun = 4.65
    Mr_galaxy = Mr_sun - 2.5 * (log_mstar - log_mtolr)
    rmag = Mr_galaxy + 5 * np.log10(d_l) + 25
    
    return log_mstar, log_sfr, sfr_mode, color_gr, rmag, rmag <= rmag_limit

# ==============================================================================
# 2. RUN SIMULATION & CREATE PLOTS
# ==============================================================================
def generate_premium_diagnostic_plots():
    z = 0.3
    rmag_limit = 23.5
    log_mstar, log_sfr, sfr_mode, color_gr, rmag, valid_idx = sample_mock_generation(50000, z, rmag_limit)
    
    fig, axs = plt.subplots(2, 2, figsize=(16, 13))
    
    # --------------------------------------------------------------------------
    # PLOT 1: Before vs. After Magnitude Cut PDF (Telescope Bias)
    # --------------------------------------------------------------------------
    ax = axs[0, 0]
    sns.histplot(log_mstar, bins=100, ax=ax, stat='density', element='step', fill=True,
                 color='#888888', alpha=0.3, label='Raw Generated SMF (True Universe)')
    sns.histplot(log_mstar[valid_idx], bins=100, ax=ax, stat='density', element='step', fill=True,
                 color='#e63946', alpha=0.5, label=f'Detected Galaxies (m_r < {rmag_limit})')
    
    ax.set_title("Stellar Mass PDF: Visualizing Selection Bias", fontweight='bold')
    ax.set_xlabel(r"$\log M_{\star} \ [M_{\odot}]$")
    ax.set_ylabel("Probability Density")
    ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)
    ax.set_xlim(6.5, 12.0)
    
    # --------------------------------------------------------------------------
    # PLOT 2: SFR vs. Stellar Mass Hexbin (Main Sequence & Quenched Valley)
    # --------------------------------------------------------------------------
    ax = axs[0, 1]
    hb = ax.hexbin(log_mstar[valid_idx], log_sfr[valid_idx], gridsize=40, cmap='plasma', mincnt=1, edgecolors='none')
    ax.plot(log_mstar[valid_idx], sfr_mode[valid_idx], color='#00f5d4', linestyle='--', linewidth=2.5, label='SFMS Mode')
    
    # Annotate zones
    ax.text(7.5, 1.0, "Star-Forming Cloud", color='white', fontweight='bold', bbox=dict(facecolor='black', alpha=0.4, boxstyle='round,pad=0.3'))
    ax.text(10.2, -2.8, "Quenched Valley", color='white', fontweight='bold', bbox=dict(facecolor='black', alpha=0.4, boxstyle='round,pad=0.3'))
    
    ax.set_title("Star Formation Rate vs. Stellar Mass", fontweight='bold')
    ax.set_xlabel(r"$\log M_{\star} \ [M_{\odot}]$")
    ax.set_ylabel(r"$\log \mathrm{SFR} \ [M_{\odot} \mathrm{yr}^{-1}]$")
    ax.legend(loc='upper left', frameon=True)
    fig.colorbar(hb, ax=ax, label='Detected Galaxy Count')
    ax.set_xlim(7.0, 12.0)
    ax.set_ylim(-3.5, 2.0)
    
    # --------------------------------------------------------------------------
    # PLOT 3: Color-Mass Diagram (Blue Cloud, Green Valley, Red Sequence)
    # --------------------------------------------------------------------------
    ax = axs[1, 0]
    # Filter for cleaner hexbin representation
    hb_color = ax.hexbin(log_mstar[valid_idx], color_gr[valid_idx], gridsize=40, cmap='viridis', mincnt=1, edgecolors='none')
    
    # Annotate galaxy zones
    ax.text(7.2, 0.15, "Blue Cloud (Star-Forming)", color='white', fontweight='bold', bbox=dict(facecolor='black', alpha=0.4, boxstyle='round'))
    ax.text(9.5, 0.45, "Green Valley", color='white', fontweight='bold', bbox=dict(facecolor='black', alpha=0.4, boxstyle='round'))
    ax.text(10.5, 0.78, "Red Sequence (Quenched)", color='white', fontweight='bold', bbox=dict(facecolor='black', alpha=0.4, boxstyle='round'))
    
    ax.set_title("Color-Mass Diagram: Rest-Frame $(g - r)$ vs. Mass", fontweight='bold')
    ax.set_xlabel(r"$\log M_{\star} \ [M_{\odot}]$")
    ax.set_ylabel("Rest-Frame $(g - r)$ Color")
    fig.colorbar(hb_color, ax=ax, label='Detected Galaxy Count')
    ax.set_xlim(7.0, 12.0)
    ax.set_ylim(-0.15, 1.0)
    
    # --------------------------------------------------------------------------
    # PLOT 4: Apparent Magnitude vs. Stellar Mass (Showing Cutoff Boundary)
    # --------------------------------------------------------------------------
    ax = axs[1, 1]
    # Sample a smaller subset for the scatter plot to prevent overplotting
    sample_indices = np.random.choice(len(log_mstar), size=5000, replace=False)
    sub_mass = log_mstar[sample_indices]
    sub_rmag = rmag[sample_indices]
    sub_valid = valid_idx[sample_indices]
    
    # Scatter plot
    ax.scatter(sub_mass[sub_valid], sub_rmag[sub_valid], color='#457b9d', alpha=0.6, s=12, label='Detected Galaxies')
    ax.scatter(sub_mass[~sub_valid], sub_rmag[~sub_valid], color='#e63946', alpha=0.15, s=6, label='Faint / Hidden Galaxies')
    
    # Horizontal Cutoff Line
    ax.axhline(y=rmag_limit, color='#e63946', linestyle=':', linewidth=2, label=f'Detection Limit (m_r = {rmag_limit})')
    
    ax.set_title("Apparent Magnitude $m_r$ vs. Stellar Mass", fontweight='bold')
    ax.set_xlabel(r"$\log M_{\star} \ [M_{\odot}]$")
    ax.set_ylabel("Observed $r$-band Magnitude ($m_r$)")
    ax.invert_yaxis()  # Magnitudes are plotted inverted (brighter galaxies are at the top)
    ax.legend(loc='lower left', frameon=True, facecolor='white', framealpha=0.9)
    ax.set_xlim(7.0, 12.0)
    ax.set_ylim(28.0, 14.0)
    
    # Title & Save
    plt.suptitle(f"🎨 Mock Galaxy Population Simulation Diagnostics (z = {z})", fontsize=18, fontweight='bold', y=0.96)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    output_path = './mock_population_premium_diagnostics.png'
    plt.savefig(output_path, dpi=300)
    print(f"✅ Four premium publication-grade plots generated successfully!")
    print(f"🎨 Figures saved directly to your workspace: {output_path}")
    plt.show()

if __name__ == '__main__':
    generate_premium_diagnostic_plots()
