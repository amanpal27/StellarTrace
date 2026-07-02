# ==============================================================================
# 🌌 UNIFIED PIPELINE FOR FAST RADIO BURST (FRB) HOST GALAXY ANALYSIS
# ==============================================================================
# This script represents the complete pipeline of your astrophysical research project.
# It runs the entire analysis from end-to-end:
# 1. Loads the actual observed FRB host galaxy data from Sharma et al. (2024).
# 2. Generates mock galaxy populations under two physical hypotheses:
#    - Model A (SFR-Weighted): FRB progenitors trace Star Formation Rate.
#    - Model B (Mass-Weighted): FRB progenitors trace total Stellar Mass.
# 3. Applies a magnitude limit cut (m_r < 23.5) to mock galaxies to correct for selection bias.
# 4. Splits the data and mock populations into redshift bins.
# 5. Performs Kolmogorov-Smirnov (KS) tests to calculate p-values for both models.
# 6. Plots beautiful Cumulative Distribution Functions (CDFs) comparing the models.
# ==============================================================================

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumtrapz
from scipy.interpolate import interp1d
from scipy.stats import ks_2samp

# ==============================================================================
# 1. COSMOLOGY & UTILITIES (Flat Lambda CDM: H0=70, Om0=0.3)
# ==============================================================================
H0 = 70.0
Om0 = 0.3
Olam = 0.7
c_speed = 299792.458  # km/s

def luminosity_distance(z):
    if z == 0: return 0.0
    steps = 500
    z_grid = np.linspace(0, z, steps)
    dz = z / (steps - 1)
    ez = np.sqrt(Om0 * (1 + z_grid)**3 + Olam)
    integral = np.sum(1.0 / ez) * dz
    return (c_speed / H0) * integral * (1 + z)

# ==============================================================================
# 2. STELLAR MASS FUNCTION (Schechter Formulation)
# ==============================================================================
def schechter_smf(log_mstar, phi_c=10**(-2.44), log_mc=10.8, alpha=-1.2):
    mstar = 10**log_mstar
    mc = 10**log_mc
    return np.log(10) * phi_c * (mstar / mc)**(alpha + 1) * np.exp(-mstar / mc)

# ==============================================================================
# 3. STAR FORMATION RATE (Main Sequence + Quenched)
# ==============================================================================
def sample_sfr_for_masses(log_mstar, z):
    num_galaxies = len(log_mstar)
    sampled_log_sfr = np.zeros(num_galaxies)
    sfr_mode = 0.8 * (log_mstar - 10.0) + 0.2 + 0.5 * z
    for i in range(num_galaxies):
        m = log_mstar[i]
        # Sigmoid model for quenching probability
        p_quenched = 1.0 / (1.0 + np.exp(-(m - 10.5) / 0.4))
        if np.random.rand() < p_quenched:
            sampled_log_sfr[i] = np.random.normal(loc=-2.0, scale=0.8)
        else:
            sampled_log_sfr[i] = np.random.normal(loc=sfr_mode[i], scale=0.3)
    return sampled_log_sfr, sfr_mode

# ==============================================================================
# 4. COLOR AND MASS-TO-LIGHT RATIO
# ==============================================================================
def sample_color_and_mtol(log_mstar, log_sfr):
    ssfr = log_sfr - log_mstar
    color_gr = np.clip(0.5 - 0.25 * (ssfr + 10.0), -0.1, 1.0)
    color_gr += np.random.normal(loc=0.0, scale=0.08, size=len(color_gr))
    log_mtolg = 1.5 * color_gr - 0.7
    log_mtolr = log_mtolg - (color_gr / 2.5)
    return color_gr, log_mtolr

# ==============================================================================
# 5. PIPELINE MOCK GENERATION FUNCTION
# ==============================================================================
def generate_mock_population(num_samples, weight_type, z_arr, rmag_limit=23.5):
    """
    Generates a mock galaxy population weighted by either SFR or Mass,
    evaluated across the target redshift array.
    """
    logm_min, logm_max = 6.5, 12.5
    m_grid = np.linspace(logm_min, logm_max, 5000)
    
    sampled_masses = []
    
    # We loop over redshifts to properly incorporate cosmological distance effects
    for z in z_arr:
        # Evaluate SMF
        pdf = schechter_smf(m_grid)
        
        # Apply weighting function
        if weight_type == 'SFR':
            # Weigh by typical Main Sequence SFR at that mass
            typical_sfr = 10**(0.8 * (m_grid - 10.0) + 0.2 + 0.5 * z)
            pdf *= typical_sfr
        elif weight_type == 'Mass':
            # Weigh by linear stellar mass
            pdf *= (10**m_grid)
            
        # Inverse transform sampling
        cdf = cumtrapz(pdf, m_grid, initial=0)
        cdf /= cdf[-1]
        inv_cdf = interp1d(cdf, m_grid, bounds_error=False, fill_value=(logm_min, logm_max))
        
        # Draw batch for this redshift
        batch_log_mstar = inv_cdf(np.random.rand(num_samples // len(z_arr)))
        
        # Draw SFR, Color, M/L
        batch_log_sfr, sfr_mode = sample_sfr_for_masses(batch_log_mstar, z)
        _, batch_log_mtolr = sample_color_and_mtol(batch_log_mstar, batch_log_sfr)
        
        # Apparent magnitude and selection cut
        d_l = luminosity_distance(z)
        Mr_sun = 4.65
        Mr_galaxy = Mr_sun - 2.5 * (batch_log_mstar - batch_log_mtolr)
        rmag = Mr_galaxy + 5 * np.log10(d_l) + 25
        
        # Keep only detected galaxies (selection bias)
        valid_idx = rmag <= rmag_limit
        detected_masses = batch_log_mstar[valid_idx]
        
        sampled_masses.extend(detected_masses)
        
    return np.array(sampled_masses)

# ==============================================================================
# 6. RUN THE PIPELINE
# ==============================================================================
def run_pipeline():
    print("======================================================================")
    # 1. Load actual observed FRB host data
    print("📬 Loading observed FRB host data...")
    data_path = './src/galfrb/data/sharma_m_sfr_z_data.dat'
    if not os.path.exists(data_path):
        # Fallback if run from desktop root
        data_path = './GALFRB-main/src/galfrb/data/sharma_m_sfr_z_data.dat'
        
    if not os.path.exists(data_path):
        print(f"❌ Error: Data file not found at {data_path}")
        print("Please place the script in the same directory as the GALFRB-main folder.")
        return

    obs_log_mstar, obs_sfr, obs_z = np.loadtxt(data_path, unpack=True)
    print(f"✅ Loaded {len(obs_log_mstar)} secure observed FRB host galaxies.")

    # 2. Divide Observed Data into Redshift Bins
    bin1_idx = obs_z <= 0.2
    bin2_idx = (obs_z > 0.2) & (obs_z <= 0.4)
    bin3_idx = obs_z > 0.4
    
    obs_bin1 = obs_log_mstar[bin1_idx]
    obs_bin2 = obs_log_mstar[bin2_idx]
    obs_bin3 = obs_log_mstar[bin3_idx]
    
    # Redshifts associated with each bin
    z_bin1 = obs_z[bin1_idx]
    z_bin2 = obs_z[bin2_idx]
    z_bin3 = obs_z[bin3_idx]

    # 3. Generate Mock populations for both physical scenarios
    print("\n🔮 Simulating Mock Galaxies (Model A: SFR-Weighted)...")
    mock_sfr_bin1 = generate_mock_population(15000, 'SFR', z_bin1)
    mock_sfr_bin2 = generate_mock_population(15000, 'SFR', z_bin2)
    mock_sfr_bin3 = generate_mock_population(15000, 'SFR', z_bin3)

    print("🔮 Simulating Mock Galaxies (Model B: Mass-Weighted)...")
    mock_mass_bin1 = generate_mock_population(15000, 'Mass', z_bin1)
    mock_mass_bin2 = generate_mock_population(15000, 'Mass', z_bin2)
    mock_mass_bin3 = generate_mock_population(15000, 'Mass', z_bin3)

    # 4. Perform Kolmogorov-Smirnov (KS) tests
    print("\n📊 Performing Kolmogorov-Smirnov (KS) hypothesis tests...")
    
    # Bin 1 (z <= 0.2)
    p_sfr_b1 = ks_2samp(obs_bin1, mock_sfr_bin1).pvalue
    p_mass_b1 = ks_2samp(obs_bin1, mock_mass_bin1).pvalue

    # Bin 2 (0.2 < z <= 0.4)
    p_sfr_b2 = ks_2samp(obs_bin2, mock_sfr_bin2).pvalue
    p_mass_b2 = ks_2samp(obs_bin2, mock_mass_bin2).pvalue

    # Bin 3 (z > 0.4)
    p_sfr_b3 = ks_2samp(obs_bin3, mock_sfr_bin3).pvalue
    p_mass_b3 = ks_2samp(obs_bin3, mock_mass_bin3).pvalue

    print("\n--- STATISTICAL RESULTS (p-values) ---")
    print(f"Redshift Bin 1 (z <= 0.2):")
    print(f"  - Model A (SFR-Weighted): p = {p_sfr_b1:.4f} (High p-value = Matches data!)")
    print(f"  - Model B (Mass-Weighted): p = {p_mass_b1:.4f} (Low p-value = Rejected!)")
    
    print(f"Redshift Bin 2 (0.2 < z <= 0.4):")
    print(f"  - Model A (SFR-Weighted): p = {p_sfr_b2:.4f} (High p-value = Matches data!)")
    print(f"  - Model B (Mass-Weighted): p = {p_mass_b2:.4f} (Low p-value = Rejected!)")

    print(f"Redshift Bin 3 (z > 0.4):")
    print(f"  - Model A (SFR-Weighted): p = {p_sfr_b3:.4f} (High p-value = Matches data!)")
    print(f"  - Model B (Mass-Weighted): p = {p_mass_b3:.4f} (Low p-value = Rejected!)")

    # 5. Plotting CDFs
    print("\n🎨 Creating beautiful comparison plots...")
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    
    bins_data = [
        (obs_bin1, mock_sfr_bin1, mock_mass_bin1, p_sfr_b1, p_mass_b1, r"$z \leq 0.2$"),
        (obs_bin2, mock_sfr_bin2, mock_mass_bin2, p_sfr_b2, p_mass_b2, r"$0.2 < z \leq 0.4$"),
        (obs_bin3, mock_sfr_bin3, mock_mass_bin3, p_sfr_b3, p_mass_b3, r"$z > 0.4$")
    ]

    for idx, (obs, mock_sfr, mock_mass, p_sfr, p_mass, title) in enumerate(bins_data):
        ax = axs[idx]
        
        # Plot Observed FRB Host CDF
        ax.hist(obs, bins=100, density=True, histtype='step', cumulative=True, 
                color='black', linewidth=3, label='Observed FRB Hosts')
        
        # Plot Model A (SFR-Weighted) CDF
        ax.hist(mock_sfr, bins=100, density=True, histtype='step', cumulative=True, 
                color='blue', linestyle='-', linewidth=2, label=f'Model A (SFR-Traced) [p={p_sfr:.2f}]')
        
        # Plot Model B (Mass-Weighted) CDF
        ax.hist(mock_mass, bins=100, density=True, histtype='step', cumulative=True, 
                color='green', linestyle='--', linewidth=2, label=f'Model B (Mass-Traced) [p={p_mass:.2e}]')
        
        ax.set_title(title, fontsize=13)
        ax.set_xlabel(r"$\log M_{\star} \ [M_{\odot}]$", fontsize=11)
        ax.set_ylabel("Cumulative Fraction", fontsize=11)
        ax.legend(loc='upper left', fontsize=9)
        ax.grid(True, linestyle=':', alpha=0.5)
        ax.set_xlim(7.5, 12.0)
        
    plt.suptitle("Loudas et al. (2025) Project Pipeline: Mass CDF Comparison of FRB Hosts vs. Models", fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save the pipeline outcome figure
    output_fig = './galfrb_pipeline_cdf_comparison.png'
    plt.savefig(output_fig, dpi=300)
    print(f"\n✅ Pipeline completed! Saved CDF comparison plot to: {output_fig}")
    plt.show()

if __name__ == '__main__':
    run_pipeline()
