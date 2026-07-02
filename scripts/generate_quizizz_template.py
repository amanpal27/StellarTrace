import pandas as pd
import os

# Define the 30 academic-style questions for Quizizz bulk upload
# Option indexes are standardized so they match across platforms
quiz_data = [
    {
        "Question Text": "In a flat Lambda-CDM universe, which energy component dominates late-time cosmic expansion, and what is its dynamical effect?",
        "Question Type": "Multiple Choice",
        "Option 1": "Matter density, leading to gravitational recollapse (a Big Crunch)",
        "Option 2": "Dark Energy (cosmological constant), leading to accelerated expansion",
        "Option 3": "Radiation density, leading to a decelerating expansion rate",
        "Option 4": "Spatial curvature, maintaining a static state",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "In the standard Lambda-CDM model of cosmology, Dark Energy (Omega_Lambda = 0.7) has a negative pressure equation of state (w = -1) that counteracts gravity, leading to accelerated expansion at late times (redshift z < 0.6)."
    },
    {
        "Question Text": "A photon is emitted from a galaxy at redshift z = 1.0. By what factor is its observed wavelength stretched compared to its rest-frame wavelength?",
        "Question Type": "Multiple Choice",
        "Option 1": "Stretched by a factor of 1.5",
        "Option 2": "Stretched by a factor of 2.0",
        "Option 3": "Stretched by a factor of 1.0 (no change)",
        "Option 4": "Stretched by a factor of 0.5 (compressed)",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "The observed wavelength is related to the rest-frame wavelength by: lambda_obs = lambda_rest * (1 + z). For z = 1.0, the factor is (1 + 1) = 2.0. The wavelength is doubled."
    },
    {
        "Question Text": "When generating a simulated isotropic galaxy distribution, why does sampling the declination angle (Dec) uniformly in degrees from -90 to +90 fail to produce a uniform spatial density?",
        "Question Type": "Multiple Choice",
        "Option 1": "It causes galaxies to crowd unnaturally near the celestial poles (Dec = +/-90 degrees)",
        "Option 2": "It causes galaxies to cluster along the celestial equator (Dec = 0 degrees)",
        "Option 3": "It creates an artificial depletion at the polar coordinate singularities",
        "Option 4": "It introduces a radial bias relative to the observer's location",
        "Correct Answer": "1",
        "Time in seconds": "120",
        "Explanation": "Uniform sampling in degrees ignores the cosine projection factor of a sphere (dA = cos(dec) dRA dDec). This leads to severe crowding at the poles. To fix this, you must sample sin(Dec) uniformly from -1 to 1, then calculate Dec = arcsin(U)."
    },
    {
        "Question Text": "Which physical mechanism is primarily responsible for the rapid quenching of star formation in massive galaxies (M_star > M_c), creating the exponential cutoff in the Stellar Mass Function?",
        "Question Type": "Multiple Choice",
        "Option 1": "Supernova feedback",
        "Option 2": "Active Galactic Nuclei (AGN) feedback",
        "Option 3": "Stellar wind stripping",
        "Option 4": "Dark matter halo evaporation",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "AGN feedback occurs when accretion onto the central SMBH releases enormous energy (winds/jets) that heats the galaxy's gas reservoir, preventing it from cooling and forming stars. This creates the exponential cutoff in the Schechter mass function."
    },
    {
        "Question Text": "Why is the faint-end slope (alpha = -1.25) of the Stellar Mass Function relatively flat compared to the dark matter halo mass function?",
        "Question Type": "Multiple Choice",
        "Option 1": "Dwarf galaxies are dominated by active supermassive black holes",
        "Option 2": "Supernova feedback and UV heating eject gas from shallow potential wells",
        "Option 3": "Dwarf galaxies contain no dark matter to bind their gas",
        "Option 4": "Cosmic expansion prevents accretion in low-mass halos",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "Low-mass dwarf galaxies have very shallow gravitational potential wells. The energy from supernova explosions and background UV radiation easily heats and expels their gas, suppressing star formation."
    },
    {
        "Question Text": "To generate mock galaxy masses following a Schechter mass function using a uniform random variable U in [0,1], which mathematical technique is applied?",
        "Question Type": "Multiple Choice",
        "Option 1": "Pass U through the Inverse Cumulative Distribution Function (Inverse CDF)",
        "Option 2": "Multiply U by the Hubble constant (H0)",
        "Option 3": "Convolve U with a Gaussian measurement error",
        "Option 4": "Divide U by the critical density of the universe",
        "Correct Answer": "1",
        "Time in seconds": "120",
        "Explanation": "In Inverse Transform Sampling, drawing U from Uniform(0,1) and calculating X = F^-1(U) yields random numbers that follow the exact PDF of the CDF F(x)."
    },
    {
        "Question Text": "In Inverse Transform Sampling, drawing a random value U = 0.50 corresponds to returning which parameter of the target stellar mass distribution?",
        "Question Type": "Multiple Choice",
        "Option 1": "The maximum stellar mass on the grid",
        "Option 2": "The mean stellar mass of the distribution",
        "Option 3": "The median stellar mass (50th percentile)",
        "Option 4": "The mode (most common mass) of the distribution",
        "Correct Answer": "3",
        "Time in seconds": "120",
        "Explanation": "The value where the cumulative probability CDF reaches exactly 0.50 corresponds to the median of the physical mass distribution."
    },
    {
        "Question Text": "Why must a stellar mass function, Phi(M), be multiplied by ln(10)*M when evaluating it in logarithmic bins of x = log10(M)?",
        "Question Type": "Multiple Choice",
        "Option 1": "To account for stellar mass loss over cosmic time",
        "Option 2": "To conserve probability density under a change of variables (Jacobian transformation)",
        "Option 3": "To compensate for Malmquist bias in massive galaxies",
        "Option 4": "To align the mass scale with the Hubble parameter",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "To ensure that the number of galaxies in a bin remains constant (Phi(M) dM = Phi(x) dx), we must apply the transformation derivative: dM/dx = M * ln(10)."
    },
    {
        "Question Text": "In the bimodal distribution of galaxies, what is the term for the transitional region between the active 'Blue Cloud' and the passive 'Red Sequence'?",
        "Question Type": "Multiple Choice",
        "Option 1": "The starburst sequence",
        "Option 2": "The Green Valley",
        "Option 3": "The dust gap",
        "Option 4": "The cosmic void",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "Galaxies in the process of shutting down star formation (quenching) transition from the Blue Cloud to the Red Sequence through the 'Green Valley'."
    },
    {
        "Question Text": "What empirical astrophysical scaling relation is represented by the Star Formation Main Sequence (SFMS)?",
        "Question Type": "Multiple Choice",
        "Option 1": "The relationship between stellar mass and central black hole mass",
        "Option 2": "The correlation between a galaxy's stellar mass and its star formation rate",
        "Option 3": "The relationship between orbital velocity and galactic radius",
        "Option 4": "The ratio of gas mass to total dark matter mass",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "The SFMS shows that actively star-forming galaxies have a Star Formation Rate (SFR) that scales as a power-law with their stellar mass, representing steady-state gas accretion."
    },
    {
        "Question Text": "If a galaxy's Specific Star Formation Rate (sSFR) falls below 10^-11 yr^-1, what does this indicate about its evolutionary state?",
        "Question Type": "Multiple Choice",
        "Option 1": "It is in an active starburst phase",
        "Option 2": "It is undergoing a major gas-rich merger",
        "Option 3": "It is quenched (passive/retired from forming stars)",
        "Option 4": "It is collapsing into a supermassive black hole",
        "Correct Answer": "3",
        "Time in seconds": "120",
        "Explanation": "An sSFR of 10^-11 yr^-1 means a galaxy would take 100 billion years (longer than the age of the universe) to double its mass at its current rate, indicating star formation has ceased (quenched)."
    },
    {
        "Question Text": "What does the typical scatter of ~0.3 dex around the Star Formation Main Sequence (SFMS) represent physically?",
        "Question Type": "Multiple Choice",
        "Option 1": "Instrumental measurement noise in spectroscopic surveys",
        "Option 2": "Stochastic variations in star formation histories from episodic accretion and feedback",
        "Option 3": "Relativistic length contraction and lensing distortions",
        "Option 4": "Gravitational redshift effects near the galactic center",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "While the SFMS is tight, star formation fluctuates stochastically due to episodic gas feeding and local feedback loops, producing a physical scatter of ~0.3 dex."
    },
    {
        "Question Text": "What selection effect causes flux-limited astronomical catalogs to be dominated by intrinsically luminous objects at high redshifts?",
        "Question Type": "Multiple Choice",
        "Option 1": "Eddington bias",
        "Option 2": "Lutz-Kelker bias",
        "Option 3": "Malmquist Bias",
        "Option 4": "Luminosity-distance degeneracy",
        "Correct Answer": "3",
        "Time in seconds": "120",
        "Explanation": "Malmquist bias is the selection effect in astronomy where a flux-limited sample is dominated by intrinsically bright objects at large distances because faint objects fall below the detection threshold."
    },
    {
        "Question Text": "Why does a young, star-forming blue galaxy exhibit a much lower mass-to-light ratio than an old red galaxy of the same stellar mass?",
        "Question Type": "Multiple Choice",
        "Option 1": "Blue galaxies are dominated by massive, hot O and B stars that emit high luminosity",
        "Option 2": "Red galaxies contain significantly more dark matter in their cores",
        "Option 3": "Blue galaxies are completely devoid of interstellar dust obscuration",
        "Option 4": "Red galaxies are expanding away from the observer at a faster rate",
        "Correct Answer": "1",
        "Time in seconds": "120",
        "Explanation": "O and B stars are extremely massive and hot, emitting up to 100,000 times more light than the Sun. Despite being rare, they dominate the light output of star-forming systems, yielding a low Mass-to-Light (M/L) ratio."
    },
    {
        "Question Text": "In a galaxy survey with a spectroscopic limit of apparent magnitude m = 23.5, why is a galaxy with m = 24.8 excluded?",
        "Question Type": "Multiple Choice",
        "Option 1": "Its radial velocity exceeds the Hubble flow limit",
        "Option 2": "It is below the detection threshold because it is too faint (higher apparent magnitude)",
        "Option 3": "It is classified as a foreground stellar contaminant",
        "Option 4": "Its light has been completely absorbed by cosmic dust",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "Apparent magnitudes increase as objects grow dimmer. A galaxy with m = 24.8 is fainter than the survey limit of 23.5, meaning it falls below the detection threshold and is excluded from the catalog."
    },
    {
        "Question Text": "By definition, absolute magnitude is the apparent magnitude a celestial object would exhibit if observed from a standard distance of:",
        "Question Type": "Multiple Choice",
        "Option 1": "1 Astronomical Unit (AU)",
        "Option 2": "1 Megaparsec (Mpc)",
        "Option 3": "10 parsecs",
        "Option 4": "1 Light-Year",
        "Correct Answer": "3",
        "Time in seconds": "120",
        "Explanation": "Absolute magnitude is a standardized measure of intrinsic brightness, defined as the apparent magnitude of an object placed exactly 10 parsecs away."
    },
    {
        "Question Text": "Which stellar spectral class corresponds to the hottest, most massive main-sequence stars that terminate as core-collapse supernovae?",
        "Question Type": "Multiple Choice",
        "Option 1": "M-class (red dwarfs)",
        "Option 2": "K-class (orange dwarfs)",
        "Option 3": "A-class (white stars)",
        "Option 4": "O-class (blue supergiants)",
        "Correct Answer": "4",
        "Time in seconds": "120",
        "Explanation": "O-type stars are the hottest (T > 30,000 K) and most massive (M > 16 Msun) stars. They have short lifetimes (a few million years) and end in core-collapse supernovae."
    },
    {
        "Question Text": "Which class of supernova is triggered by the thermonuclear runaway of a carbon-oxygen white dwarf exceeding the Chandrasekhar limit in a binary system?",
        "Question Type": "Multiple Choice",
        "Option 1": "Type II Supernova",
        "Option 2": "Type Ia Supernova",
        "Option 3": "Kilonova",
        "Option 4": "Core-Collapse Supernova",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "Type Ia supernovae occur when a white dwarf reaches the Chandrasekhar mass limit (1.4 Msun), causing carbon fusion to ignite explosively throughout the star, leaving no remnant behind."
    },
    {
        "Question Text": "Which event is triggered when a star with an initial mass M >= 8 M_sun forms an iron core that collapses under gravity?",
        "Question Type": "Multiple Choice",
        "Option 1": "Type II Supernova (Core-Collapse)",
        "Option 2": "Type Ia Supernova",
        "Option 3": "Helium Flash",
        "Option 4": "Planetary Nebula ejection",
        "Correct Answer": "1",
        "Time in seconds": "120",
        "Explanation": "Stars with initial masses above 8 Msun can fuse elements up to iron. Once iron forms in the core, fusion ceases, the core collapses into a neutron star or black hole, and the outer layers are ejected in a Type II supernova."
    },
    {
        "Question Text": "What component of spiral galaxies is required to explain the flat rotation curves observed at large radii, where visible matter density is low?",
        "Question Type": "Multiple Choice",
        "Option 1": "A central supermassive black hole",
        "Option 2": "A massive, extended Dark Matter Halo",
        "Option 3": "Interstellar magnetic fields",
        "Option 4": "Peculiar velocities from metric expansion",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "Newtonian gravity predicts speeds should drop as v proportional to r^-0.5 outside the visible mass. Flat curves require a massive, extended halo of invisible dark matter to provide the necessary gravitational attraction."
    },
    {
        "Question Text": "Using Hubble's Law (v = H0 * d) with a Hubble constant H0 = 70 km/s/Mpc, what is the recession velocity of a galaxy at a distance of 2 Megaparsecs?",
        "Question Type": "Multiple Choice",
        "Option 1": "70 km/s",
        "Option 2": "140 km/s",
        "Option 3": "35 km/s",
        "Option 4": "280 km/s",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "According to Hubble's Law (v = H0 * d), the recession velocity is 70 km/s/Mpc * 2 Mpc = 140 km/s."
    },
    {
        "Question Text": "What is the primary physical cause of cosmological redshift in the spectrum of distant galaxies?",
        "Question Type": "Multiple Choice",
        "Option 1": "Doppler shifts from galaxies moving physically through static space",
        "Option 2": "Scattering of light by interstellar and intergalactic dust",
        "Option 3": "The expansion of the space metric itself stretching light wavelengths during propagation",
        "Option 4": "Gravitational time dilation near massive galaxy clusters",
        "Correct Answer": "3",
        "Time in seconds": "120",
        "Explanation": "Cosmological redshift is not a Doppler shift from velocity through space; rather, it is space itself expanding, which stretches the wavelength of light as it propagates across the cosmos."
    },
    {
        "Question Text": "What is the term for the cosmological postulate that, on sufficiently large scales, the universe is homogeneous and isotropic?",
        "Question Type": "Multiple Choice",
        "Option 1": "The Cosmological Principle",
        "Option 2": "The Copernican Principle",
        "Option 3": "The Equivalence Principle",
        "Option 4": "The Einstein Postulate",
        "Correct Answer": "1",
        "Time in seconds": "120",
        "Explanation": "The Cosmological Principle is a fundamental postulate of modern cosmology, asserting that on scales larger than ~100 Mpc, there are no privileged observers or directions."
    },
    {
        "Question Text": "What is the expression for the Schwarzschild radius (Rs), which defines the event horizon of a spherically symmetric, non-rotating black hole?",
        "Question Type": "Multiple Choice",
        "Option 1": "Rs = GM / c^2",
        "Option 2": "Rs = 2GM / c^2",
        "Option 3": "Rs = GM / (2c^2)",
        "Option 4": "Rs = sqrt(GM / c)",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "The Schwarzschild radius defines the event horizon of a spherical, non-rotating black hole. Inside this radius, gravity is so strong that even light cannot escape."
    },
    {
        "Question Text": "Which light element was synthesized in trace amounts during Big Bang Nucleosynthesis, in addition to hydrogen and helium?",
        "Question Type": "Multiple Choice",
        "Option 1": "Carbon",
        "Option 2": "Iron",
        "Option 3": "Lithium",
        "Option 4": "Oxygen",
        "Correct Answer": "3",
        "Time in seconds": "120",
        "Explanation": "Big Bang Nucleosynthesis forged Hydrogen (~75%), Helium (~25%), and trace amounts of Deuterium, Helium-3, and Lithium-7. Heavier elements (carbon, oxygen, iron) were only synthesized later inside stellar cores."
    },
    {
        "Question Text": "Excluding local peculiar velocities, how does the comoving distance between two distant galaxies change as the universe expands?",
        "Question Type": "Multiple Choice",
        "Option 1": "It increases proportionally to the scale factor a(t)",
        "Option 2": "It remains constant by definition",
        "Option 3": "It decreases due to local gravitational attraction",
        "Option 4": "It increases exponentially due to dark energy",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "Comoving coordinates factor out the overall expansion of the universe (the scale factor a(t)). Therefore, the comoving distance between two coordinate points that just go with the 'Hubble Flow' remains constant over time."
    },
    {
        "Question Text": "Why does stellar and supernova feedback suppress star formation in dwarf galaxies much more effectively than in massive galaxies?",
        "Question Type": "Multiple Choice",
        "Option 1": "Dwarf galaxies lack dark matter halos entirely",
        "Option 2": "Dwarf galaxies have shallow potential wells and low escape velocities",
        "Option 3": "Dwarf galaxies have higher star formation efficiency",
        "Option 4": "Dwarf galaxies are closer to the cosmic web filaments",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "The escape velocity from a galaxy's gravitational well is v_esc = sqrt(2GM/R). Dwarf galaxies have small masses M, so their potential wells are shallow, allowing stellar feedback to easily blow gas away."
    },
    {
        "Question Text": "The Star Formation Main Sequence (SFMS) has a sub-linear slope (b ~ 0.8) in log SFR vs log M_star. What does this indicate about galaxy growth efficiency?",
        "Question Type": "Multiple Choice",
        "Option 1": "Massive galaxies form stars more efficiently per unit mass",
        "Option 2": "Low-mass galaxies form stars more efficiently per unit mass (higher sSFR)",
        "Option 3": "Star formation rates are independent of stellar mass",
        "Option 4": "Lower-mass galaxies are fully quenched",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "A slope of ~0.8 is less than 1 (sub-linear). Since sSFR = SFR/M_star, this means sSFR decreases as stellar mass increases (sSFR proportional to M_star^-0.2). Thus, lower-mass galaxies are actually more active in star formation relative to their size than massive ones."
    },
    {
        "Question Text": "Two identical stars are observed, with Star B situated exactly 10 times further away than Star A. By how many magnitudes fainter will Star B appear?",
        "Question Type": "Multiple Choice",
        "Option 1": "2.5 magnitudes fainter",
        "Option 2": "5.0 magnitudes fainter",
        "Option 3": "10.0 magnitudes fainter",
        "Option 4": "100.0 magnitudes fainter",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "According to the inverse-square law, flux scales as 1/d^2. Star B is 10 times further away, so its observed flux is 1/100 of Star A. In the logarithmic magnitude scale, a factor of 100 in flux corresponds to exactly 5 magnitudes (m_B - m_A = 5 * log10(d_B/d_A) = 5 * log10(10) = 5)."
    },
    {
        "Question Text": "Why did Big Bang Nucleosynthesis fail to synthesize carbon, leaving the early universe with only light elements?",
        "Question Type": "Multiple Choice",
        "Option 1": "The nuclear binding energy of carbon is unstable under any conditions",
        "Option 2": "The universe cooled and diluted too rapidly to permit the triple-alpha helium fusion process",
        "Option 3": "Dark matter particles absorbed the required free neutrons",
        "Option 4": "Strong stellar winds from early stars dispersed the helium nuclei",
        "Correct Answer": "2",
        "Time in seconds": "120",
        "Explanation": "Fusing helium into carbon requires the 'triple-alpha process' (3 * He4 -> C12), which requires high temperatures and high densities. During BBN, by the time helium was forged, the expansion of the universe had lowered the density and temperature too quickly to allow this three-body collision to occur."
    }
]

# Create a DataFrame matching the Quizizz bulk-import template
df = pd.DataFrame(quiz_data)
df['Option 5'] = "" # Keep Option 5 blank

columns_order = [
    'Question Text', 'Question Type', 
    'Option 1', 'Option 2', 'Option 3', 'Option 4', 'Option 5', 
    'Correct Answer', 'Time in seconds', 'Explanation'
]

df = df[columns_order]

# Save to Excel
output_path = os.path.join("c:\\Users\\Lenovo\\OneDrive\\Desktop", "stellar_trace_quizizz.xlsx")
df.to_excel(output_path, index=False)

print(f"Quizizz bulk upload template successfully created at: {output_path}")
print(f"Total questions exported: {len(df)}")
