# ==============================================================================
# 🌌 STANDALONE MOCK FRB HOST GALAXY GENERATOR (FROM SCRATCH)
# ==============================================================================
# This script is a completely self-contained, from-scratch implementation of a 
# mock galaxy population generator. It models:
# 1. Stellar Mass ($M_{\star}$) using a Schechter Stellar Mass Function.
# 2. Star Formation Rate (SFR) using a bimodal Gaussian Mixture Model (SFMS + Quenched).
# 3. Optical color $(g - r)$ and mass-to-light ratio.
# 4. Selection bias via an observed r-band magnitude cut ($m_r < 23.5$).
#
# No git repository cloning or external files are needed!
# ==============================================================================

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d

# ==============================================================================
# 1. COSMOLOGY & UTILITIES (Flat Lambda CDM: H0=70, Om0=0.3)
# ==============================================================================
H0 = 70.0  # km/s/Mpc
Om0 = 0.3
Olam = 0.7
c_speed = 299792.458  # km/s

def luminosity_distance(z):
    """
    Computes luminosity distance in Mpc for a Flat Lambda CDM cosmology
    using a simple numerical integration.
    """
    if z == 0:
        return 0.0
    # Numerical integration of 1 / E(z)
    steps = 1000
    z_grid = np.linspace(0, z, steps)
    dz = z / (steps - 1)
    ez = np.sqrt(Om0 * (1 + z_grid)**3 + Olam)
    integral = np.sum(1.0 / ez) * dz
    comoving_distance = (c_speed / H0) * integral
    return comoving_distance * (1 + z)

# ==============================================================================
# 2. STELLAR MASS FUNCTION (Schechter Formulation)
# ==============================================================================
def schechter_smf(log_mstar, phi_c=10**(-2.44), log_mc=10.8, alpha=-1.2):
    """
    Evaluates the single-component Schechter Stellar Mass Function:
    phi(M) = ln(10) * phi_c * (M/Mc)**(alpha+1) * exp(-M/Mc)
    """
    mstar = 10**log_mstar
    mc = 10**log_mc
    val = np.log(10) * phi_c * (mstar / mc)**(alpha + 1) * np.exp(-mstar / mc)
    return val

def sample_stellar_masses(num_samples, logm_min=6.5, logm_max=12.5):
    """
    Samples stellar masses using inverse transform sampling from the Schechter SMF.
    """
    m_grid = np.linspace(logm_min, logm_max, 5000)
    pdf = schechter_smf(m_grid)
    cdf = cumtrapz(pdf, m_grid, initial=0)
    cdf /= cdf[-1]  # Normalize to 1
    
    # Create the inverse CDF mapping
    inv_cdf = interp1d(cdf, m_grid, bounds_error=False, fill_value=(logm_min, logm_max))
    
    # Draw uniform random numbers and pass through the inverse CDF
    random_uniforms = np.random.rand(num_samples)
    sampled_log_mstar = inv_cdf(random_uniforms)
    return sampled_log_mstar

# ==============================================================================
# 3. STAR FORMATION RATE (Bimodal GMM: Main Sequence + Quenched)
# ==============================================================================
def sample_sfr_for_masses(log_mstar, z=0.5):
    """
    Samples SFR using a bimodal conditional formulation:
    - Star-Forming Main Sequence (SFMS) follows a log-normal distribution.
    - Quenched population has a lower SFR.
    - Quenching fraction increases for high-mass galaxies.
    """
    num_galaxies = len(log_mstar)
    sampled_log_sfr = np.zeros(num_galaxies)
    
    # SFMS ridge line mode: log(SFR) = a * log(M_star) + b + c * z
    # (Matches typical empirical main sequence slopes ~ 0.8)
    sfr_mode = 0.8 * (log_mstar - 10.0) + 0.2 + 0.5 * z
    
    for i in range(num_galaxies):
        m = log_mstar[i]
        
        # Quenching probability (higher mass galaxies are more likely to be quenched)
        # f_quenched(M) = 1 / (1 + exp(-(M - 10.5) / 0.4))
        p_quenched = 1.0 / (1.0 + np.exp(-(m - 10.5) / 0.4))
        
        if np.random.rand() < p_quenched:
            # Quenched galaxy: Low SFR with wider dispersion
            sampled_log_sfr[i] = np.random.normal(loc=-2.0, scale=0.8)
        else:
            # Star-Forming Main Sequence galaxy: Tight dispersion around the mode
            sampled_log_sfr[i] = np.random.normal(loc=sfr_mode[i], scale=0.3)
            
    return sampled_log_sfr, sfr_mode

# ==============================================================================
# 4. COLOR AND MASS-TO-LIGHT RATIO MODELING
# ==============================================================================
def sample_color_and_mtol(log_mstar, log_sfr, sfr_mode):
    """
    Calculates optical color (g - r) and rest-frame mass-to-light ratio.
    - Color (g - r) scales with specific SFR (sSFR = SFR / M_star).
    - Mass-to-light ratio is modeled based on the color.
    """
    ssfr = log_sfr - log_mstar
    
    # Blue galaxies have high sSFR; red/quenched have low sSFR
    # Mapping specific star formation rate to rest-frame g-r color
    color_gr = 0.5 - 0.25 * (ssfr + 10.0)
    color_gr = np.clip(color_gr, -0.1, 1.0)  # Clip to realistic physical limits
    
    # Add a bit of natural scatter/noise to the color
    color_gr += np.random.normal(loc=0.0, scale=0.08, size=len(color_gr))
    
    # Rest-frame Mass-to-Light ratio (M/L_g) scales exponentially with color (g - r)
    # log10(M/L_g) = 1.5 * (g - r) - 0.7
    log_mtolg = 1.5 * color_gr - 0.7
    
    # Convert M/L_g to M/L_r in the r-band: L_r = L_g * 10**( (g - r) / 2.5 )
    # Therefore: log10(M/L_r) = log10(M/L_g) - (g - r)/2.5
    log_mtolr = log_mtolg - (color_gr / 2.5)
    
    return color_gr, log_mtolr

# ==============================================================================
# 5. MAGNITUDE CUT & SELECTION BIAS (rmag < 23.5)
# ==============================================================================
def apply_magnitude_cut(log_mstar, log_mtolr, z, rmag_limit=23.5):
    """
    Converts absolute stellar mass and mass-to-light ratio into apparent r-band magnitude.
    Filters out galaxies fainter than rmag_limit.
    """
    d_l = luminosity_distance(z)
    
    # Absolute magnitude of the Sun in r-band
    Mr_sun = 4.65
    
    # Absolute magnitude of the galaxy: M_r = M_sun - 2.5 * log10(L_r)
    # Since log10(L_r) = log10(M_star) - log10(M/L_r)
    Mr_galaxy = Mr_sun - 2.5 * (log_mstar - log_mtolr)
    
    # Apparent magnitude: m_r = M_r + 5 * log10(d_l_pc) - 5
    # (Note: d_l is in Mpc, so 5 * log10(d_l * 10**6) - 5 = M_r + 5 * log10(d_l) + 25)
    rmag = Mr_galaxy + 5 * np.log10(d_l) + 25
    
    # Filter indices matching magnitude limit
    valid_indices = rmag <= rmag_limit
    return rmag, valid_indices

# ==============================================================================
# 6. MAIN SIMULATION PIPELINE
# ==============================================================================
def run_from_scratch_generator(num_samples=10000, target_z=0.3, rmag_limit=23.5):
    print("🚀 Starting Standalone Mock Galaxy Population Simulation...")
    print(f"Target Redshift: z = {target_z}")
    print(f"Number of Initial Galaxies: {num_samples}")
    
    # Step 1: Sample Stellar Masses
    print("Sampling Stellar Masses from Schechter SMF...")
    log_mstar = sample_stellar_masses(num_samples)
    
    # Step 2: Sample Star Formation Rates
    print("Sampling SFRs from Bimodal Main Sequence Mixture Model...")
    log_sfr, sfr_mode = sample_sfr_for_masses(log_mstar, z=target_z)
    
    # Step 3: Compute Color & Mass-to-Light ratio
    print("Modeling Colors and Mass-to-Light ratios...")
    color_gr, log_mtolr = sample_color_and_mtol(log_mstar, log_sfr, sfr_mode)
    
    # Step 4: Convert to Apparent Magnitude and Apply Cut
    print(f"Applying selection bias (rmag < {rmag_limit})...")
    rmag, valid_idx = apply_magnitude_cut(log_mstar, log_mtolr, target_z, rmag_limit)
    
    # Filtered lists
    mstar_filtered = log_mstar[valid_idx]
    sfr_filtered = log_sfr[valid_idx]
    color_filtered = color_gr[valid_idx]
    rmag_filtered = rmag[valid_idx]
    
    print("\n--- RESULTS ---")
    print(f"Galaxies passing magnitude cut: {len(mstar_filtered)} / {num_samples} ({len(mstar_filtered)/num_samples*100:.1f}%)")
    print(f"Average Mass (Before Cut): 10^{np.mean(log_mstar):.2f} M_sun")
    print(f"Average Mass (After Cut): 10^{np.mean(mstar_filtered):.2f} M_sun (Selection Bias visible!)")
    
    # Plotting
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    
    # Subplot 1: Hexbin of SFR vs Stellar Mass for all generated galaxies
    hb = axs[0].hexbin(log_mstar, log_sfr, gridsize=35, cmap='plasma', mincnt=1)
    axs[0].plot(log_mstar, sfr_mode, color='cyan', linestyle='--', linewidth=2, label='Main Sequence Mode')
    axs[0].set_title(f"All Generated Galaxies (z = {target_z})", fontsize=12)
    axs[0].set_xlabel(r"$\log M_{\star} \ [M_{\odot}]$", fontsize=11)
    axs[0].set_ylabel(r"$\log \mathrm{SFR} \ [M_{\odot} \mathrm{yr}^{-1}]$", fontsize=11)
    axs[0].legend(loc='upper left')
    fig.colorbar(hb, ax=axs[0], label='Galaxy Count')
    axs[0].grid(True, linestyle=':', alpha=0.5)
    
    # Subplot 2: Cumulative distribution (CDF) comparing before vs after magnitude cut
    axs[1].hist(log_mstar, bins=100, density=True, histtype='step', cumulative=True, 
                color='gray', linewidth=2, label='Before Magnitude Cut (Raw SMF)')
    axs[1].hist(mstar_filtered, bins=100, density=True, histtype='step', cumulative=True, 
                color='red', linewidth=2, label=f'After Magnitude Cut (m_r < {rmag_limit})')
    axs[1].set_title("Stellar Mass Cumulative Distribution Function (CDF)", fontsize=12)
    axs[1].set_xlabel(r"$\log M_{\star} \ [M_{\odot}]$", fontsize=11)
    axs[1].set_ylabel("CDF", fontsize=11)
    axs[1].legend(loc='upper left')
    axs[1].grid(True, linestyle=':', alpha=0.5)
    
    plt.tight_layout()
    output_img = './mock_generator_from_scratch_results.png'
    plt.savefig(output_img, dpi=300)
    print(f"\n🎨 Saved diagnostic plots to: {output_img}")
    plt.show()

if __name__ == '__main__':
    run_from_scratch_generator()
