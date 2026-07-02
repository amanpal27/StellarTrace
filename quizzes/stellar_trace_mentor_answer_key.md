# Stellar Trace: Mentor Quiz Answer Key
## Phase 1 & 2 Core Evaluation (Tasks 1 to 7 & Basic Astronomy)

This document is the official grading key and review sheet for the Phase 1 & 2 written quiz.

---

### Answer Key Quick Grid
Use this grid for rapid grading of the student's answer sheet:

| Question | Correct Answer | Topic | | Question | Correct Answer | Topic |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **B** | Dark Energy Expansion | | **16** | **C** | Absolute Magnitude |
| **2** | **B** | Cosmological Redshift | | **17** | **D** | Spectral Classes (O/B) |
| **3** | **A** | Isotropic Dec Coordinates | | **18** | **B** | Type Ia Supernovae |
| **4** | **B** | AGN Feedback / Cutoff | | **19** | **A** | Type II Supernovae |
| **5** | **B** | Faint-end Slope | | **20** | **B** | Dark Matter Halo |
| **6** | **A** | Inverse CDF sampling | | **21** | **B** | Hubble's Law |
| **7** | **C** | Median (50th percentile) | | **22** | **C** | Cosmological Redshift |
| **8** | **B** | log-M SMF Jacobian | | **23** | **A** | Cosmological Principle |
| **9** | **B** | The Green Valley | | **24** | **B** | Schwarzschild Radius ($R_s$) |
| **10** | **B** | SFMS ($M_*$ vs. $\text{SFR}$) | | **25** | **C** | Big Bang Nucleosynthesis |
| **11** | **C** | Specific SFR (sSFR) | | **26** | **B** | Comoving Coordinates |
| **12** | **B** | Cosmic Variance | | **27** | **B** | Dwarf Galaxy Escape Velocity |
| **13** | **C** | Malmquist Bias | | **28** | **B** | SFMS Sub-linear Slope |
| **14** | **A** | Mass-to-Light ($M/L$) | | **29** | **B** | Distance Modulus & Magnitudes |
| **15** | **B** | Magnitude Limits | | **30** | **B** | BBN Carbon Bottleneck |

---

### Detailed Questions, Answers, & Scientific Explanations

#### 1. In a flat $\Lambda$CDM universe, which energy component dominates late-time cosmic expansion, and what is its dynamical effect?
* **Correct Answer:** **B) Dark Energy (cosmological constant), leading to accelerated expansion**
* **Explanation:** In standard $\Lambda$CDM cosmology, Dark Energy (parameterized by the cosmological constant $\Omega_\Lambda \approx 0.7$) has a negative pressure equation of state ($w = -1$). While gravity attracts, this negative pressure acts as a repulsive force on cosmic scales, leading to the accelerated expansion of the space metric. Matter density $\Omega_m$ dilutes as $(1+z)^3$ while dark energy remains constant, so dark energy dominates late-time cosmic dynamics ($z \lesssim 0.6$).

#### 2. A photon is emitted from a galaxy at redshift $z = 1.0$. By what factor is its observed wavelength stretched compared to its rest-frame wavelength?
* **Correct Answer:** **B) Stretched by a factor of 2.0**
* **Explanation:** Cosmological redshift $z$ stretches the wavelength of traveling light. The relation between observed and rest-frame wavelengths is:
  $$\lambda_{\text{obs}} = \lambda_{\text{rest}} (1 + z)$$
  Setting $z = 1.0$ yields $\lambda_{\text{obs}} = \lambda_{\text{rest}} (1 + 1) = 2 \lambda_{\text{rest}}$, which corresponds to a wavelength stretching factor of exactly 2.0.

#### 3. When generating a simulated isotropic galaxy distribution, why does sampling the declination angle (Dec) uniformly in degrees from -90 to +90 fail to produce a uniform spatial density?
* **Correct Answer:** **A) It causes galaxies to crowd unnaturally near the celestial poles (Dec = +/-90 degrees)**
* **Explanation:** The surface area element on a sphere is given by $dA = \cos(\delta) d\alpha d\delta$ (where $\delta$ is Declination and $\alpha$ is Right Ascension). If $\delta$ is sampled uniformly, the density of stars per unit area will spike at the poles where $\cos(\delta) \to 0$. To distribute galaxies isotropically (preserving equal area density), we must sample $\sin(\delta)$ uniformly from $-1$ to $1$, then calculate $\delta = \arcsin(U)$.

#### 4. Which physical mechanism is primarily responsible for the rapid quenching of star formation in massive galaxies ($M_* > M_c \approx 10^{10.7} M_\odot$), creating the exponential cutoff in the Stellar Mass Function?
* **Correct Answer:** **B) Active Galactic Nuclei (AGN) feedback**
* **Explanation:** Massive galaxies exceed the characteristic mass $M_c \approx 10^{10.7} M_\odot$. In these systems, accretion onto the central Supermassive Black Hole (SMBH) releases massive jets, winds, and radiation. This "AGN Feedback" heats the cold gas reservoir or expels it entirely from the galactic halo, preventing gas from cooling to form stars. This triggers rapid quenching, creating the sharp exponential cutoff in the Schechter mass function.

#### 5. Why is the faint-end slope ($\alpha = -1.25$) of the Stellar Mass Function relatively flat compared to the dark matter halo mass function?
* **Correct Answer:** **B) Supernova feedback and UV heating eject gas from shallow potential wells**
* **Explanation:** Low-mass dwarf galaxies have shallow gravitational potential wells (low escape velocities). Energy injected by supernova explosions and the background ionizing UV radiation field easily heats the gas beyond the escape velocity. The gas is blown out of the system, halting star formation and keeping the faint-end slope ($\alpha$) flat.

#### 6. To generate mock galaxy masses following a Schechter mass function using a uniform random variable $U$ in $[0,1]$, which mathematical technique is applied?
* **Correct Answer:** **A) Pass $U$ through the Inverse Cumulative Distribution Function (Inverse CDF: $F^{-1}(U)$)**
* **Explanation:** Inverse Transform Sampling states that if $U \sim \text{Uniform}(0, 1)$, then the variable $X = F^{-1}(U)$ follows the probability distribution described by the CDF $F(x)$. This is the standard numerical technique for generating galaxy populations from arbitrary analytical functions like the Schechter mass function.

#### 7. In Inverse Transform Sampling, drawing a random value $U = 0.50$ corresponds to returning which parameter of the target stellar mass distribution?
* **Correct Answer:** **C) The median stellar mass (50th percentile)**
* **Explanation:** The Cumulative Distribution Function (CDF) maps the range of a random variable to a probability interval $[0, 1]$. By definition, the value of the physical variable $X$ corresponding to $F(X) = 0.50$ represents the 50th percentile, which is the median of the distribution.

#### 8. Why must a stellar mass function, $\Phi(M)$, be multiplied by $\ln(10) M$ when evaluating it in logarithmic bins of $x = \log_{10}(M)$?
* **Correct Answer:** **B) To conserve probability density under a change of variables (Jacobian transformation)**
* **Explanation:** Probability mass must be conserved under coordinate transformations ($\Phi(M) dM = \Phi(x) dx$, where $x = \log_{10} M$). The Jacobian factor is the derivative of the coordinate change:
  $$\frac{dM}{dx} = \frac{d(10^x)}{dx} = 10^x \ln(10) = M \ln(10)$$
  Multiplying the linear mass function by $\ln(10) M$ yields the correct density per unit logarithmic mass bin.

#### 9. In the bimodal distribution of galaxies, what is the term for the transitional region between the active 'Blue Cloud' and the passive 'Red Sequence'?
* **Correct Answer:** **B) The Green Valley**
* **Explanation:** The distribution of galaxies is bimodal, split between the active "Blue Cloud" (high star formation) and the passive "Red Sequence" (dead/quenched stars). The intermediate region is known as the "Green Valley", which is populated by transition galaxies undergoing quenching.

#### 10. What empirical astrophysical scaling relation is represented by the Star Formation Main Sequence (SFMS)?
* **Correct Answer:** **B) The correlation between a galaxy's stellar mass and its star formation rate**
* **Explanation:** The Star Formation Main Sequence (SFMS) is an empirical scaling relation showing that a galaxy's star formation rate is strongly correlated with its existing stellar mass. This relation represents the steady-state growth of galaxies fueled by continuous gas accretion.

#### 11. If a galaxy's Specific Star Formation Rate ($\text{sSFR}$) falls below $10^{-11} \text{ yr}^{-1}$, what does this indicate about its evolutionary state?
* **Correct Answer:** **C) It is quenched (passive/retired from forming stars)**
* **Explanation:** The Specific Star Formation Rate is defined as $\text{sSFR} = \text{SFR}/M_*$. An sSFR below $10^{-11} \text{ yr}^{-1}$ means the galaxy would take 100 billion years (longer than the age of the universe) to double its current mass at its active rate, indicating that star formation is effectively shut down (quenched).

#### 12. What does the typical scatter of ~0.3 dex around the Star Formation Main Sequence (SFMS) represent physically?
* **Correct Answer:** **B) Stochastic variations in star formation histories from episodic accretion and feedback**
* **Explanation:** While the SFMS is stable, a galaxy's accretion rate fluctuates. Episodic gas inflows, feedback loops, and minor mergers cause temporary starbursts or quenching dips, introducing an intrinsic cosmic variance ($\approx 0.3$ dex) around the average scaling relation.

#### 13. What selection effect causes flux-limited astronomical catalogs to be dominated by intrinsically luminous objects at high redshifts?
* **Correct Answer:** **C) Malmquist Bias**
* **Explanation:** In a flux-limited survey, the telescope can only detect sources brighter than a specific apparent magnitude threshold. As distance increases, the apparent brightness of dwarf galaxies drops below this limit, leaving only the intrinsically luminous (massive) galaxies visible. This selection bias is known as Malmquist Bias.

#### 14. Why does a young, star-forming blue galaxy exhibit a much lower mass-to-light ratio than an old red galaxy of the same stellar mass?
* **Correct Answer:** **A) Blue galaxies are dominated by massive, hot O and B stars that emit high luminosity**
* **Explanation:** Highly massive, young O and B class stars emit enormous amounts of luminosity ($L \propto M^4$ on the main sequence). Even though they are a small fraction of the galaxy's total mass, they completely dominate the light output, leading to low Mass-to-Light ($M/L$) ratios compared to older red populations dominated by red dwarfs.

#### 15. In a galaxy survey with a spectroscopic limit of apparent magnitude $m = 23.5$, why is a galaxy with $m = 24.8$ excluded?
* **Correct Answer:** **B) It is below the detection threshold because it is too faint (higher apparent magnitude)**
* **Explanation:** In astronomical magnitudes, larger values represent dimmer objects. A spectroscopic limiting magnitude of $23.5$ means that any galaxy with an apparent magnitude of $m = 24.8$ is dimmer than the threshold, making it too faint for the telescope to detect or spectroscopically classify.

#### 16. By definition, absolute magnitude ($M$) is the apparent magnitude ($m$) a celestial object would exhibit if observed from a standard distance of:
* **Correct Answer:** **C) 10 parsecs**
* **Explanation:** Absolute magnitude ($M$) is the apparent magnitude ($m$) an object would exhibit if placed at a standard distance of exactly 10 parsecs (approximately 32.6 light-years). This scales out the distance dependence, allowing direct comparison of intrinsic luminosity.

#### 17. Which stellar spectral class corresponds to the hottest, most massive main-sequence stars that terminate as core-collapse supernovae?
* **Correct Answer:** **D) O-class (blue supergiants)**
* **Explanation:** Main sequence stars are classified by temperature (O, B, A, F, G, K, M). O-class stars are the hottest ($T > 30,000$ K) and most massive ($M \ge 16 M_\odot$). They burn hydrogen rapidly and end their lives as core-collapse supernovae.

#### 18. Which class of supernova is triggered by the thermonuclear runaway of a carbon-oxygen white dwarf exceeding the Chandrasekhar limit in a binary system?
* **Correct Answer:** **B) Type Ia Supernova**
* **Explanation:** Type Ia supernovae are thermonuclear runaways of carbon-oxygen white dwarfs in binary systems. When the white dwarf accretes enough gas to exceed the Chandrasekhar mass limit ($1.4 M_\odot$), carbon fusion ignites explosively, destroying the entire star and leaving no compact remnant behind.

#### 19. Which event is triggered when a star with an initial mass $M \ge 8 M_\odot$ forms an iron core that collapses under gravity?
* **Correct Answer:** **A) Type II Supernova (Core-Collapse)**
* **Explanation:** Stars with initial masses $\ge 8 M_\odot$ fuse elements in their cores up to iron. Fusing iron consumes energy rather than releasing it, leading to a sudden loss of pressure support. The core collapses into a neutron star or black hole, and the outer layers rebound in a Type II supernova.

#### 20. What component of spiral galaxies is required to explain the flat rotation curves observed at large radii, where visible matter density is low?
* **Correct Answer:** **B) A massive, extended Dark Matter Halo**
* **Explanation:** According to Keplerian physics, the orbital speeds of stars outside the galaxy's baryonic core should decrease as $v \propto r^{-0.5}$. Vera Rubin's observation of flat rotation curves showed that outer speeds remain high, which can only be explained by a massive, extended halo of invisible dark matter.

#### 21. Using Hubble's Law ($v = H_0 \cdot d$) with a Hubble constant $H_0 = 70\text{ km/s/Mpc}$, what is the recession velocity of a galaxy at a distance of 2 Megaparsecs?
* **Correct Answer:** **B) 140 km/s**
* **Explanation:** According to Hubble's Law ($v = H_0 \cdot d$), where $H_0 \approx 70\text{ km/s/Mpc}$, a galaxy at a distance $d = 2\text{ Mpc}$ recedes at a velocity of:
  $$v = 70\text{ km/s/Mpc} \times 2\text{ Mpc} = 140\text{ km/s}$$

#### 22. What is the primary physical cause of cosmological redshift in the spectrum of distant galaxies?
* **Correct Answer:** **C) The expansion of the space metric itself stretching light wavelengths during propagation**
* **Explanation:** Cosmological redshift is caused by the expansion of space itself. As a photon travels through expanding space, its wavelength is physically stretched. It is distinct from local Doppler shifts caused by a galaxy's motion *through* space.

#### 23. What is the term for the cosmological postulate that, on sufficiently large scales, the universe is homogeneous and isotropic?
* **Correct Answer:** **A) The Cosmological Principle**
* **Explanation:** The Cosmological Principle is a fundamental postulate stating that on sufficiently large scales (greater than ~100 Mpc), the universe is both homogeneous (identical from all locations) and isotropic (identical in all directions).

#### 24. What is the expression for the Schwarzschild radius ($R_s$), which defines the event horizon of a spherically symmetric, non-rotating black hole?
* **Correct Answer:** **B) $R_s = 2GM / c^2$**
* **Explanation:** The Schwarzschild radius defines the event horizon of a non-rotating, spherically symmetric black hole of mass $M$. Inside this radius, gravity is so strong that the escape velocity exceeds the speed of light.

#### 25. Which light element was synthesized in trace amounts during Big Bang Nucleosynthesis, in addition to hydrogen and helium?
* **Correct Answer:** **C) Lithium**
* **Explanation:** Big Bang Nucleosynthesis forged Hydrogen, Helium, and trace amounts of Deuterium and Lithium-7. Elements heavier than lithium (like Carbon, Oxygen, and Iron) were not synthesized until the first generation of stars formed and evolved.

#### 26. Excluding local peculiar velocities, how does the comoving distance between two distant galaxies change as the universe expands?
* **Correct Answer:** **B) It remains constant by definition**
* **Explanation:** Comoving coordinates factor out the universal expansion factor $a(t)$. Therefore, as space expands, the comoving distance between two standard points that are carried along with the Hubble flow remains constant. It is the *physical* distance ($d_{\text{phys}} = a(t) d_{\text{com}}$) that increases.

#### 27. Why does stellar and supernova feedback suppress star formation in dwarf galaxies much more effectively than in massive galaxies?
* **Correct Answer:** **B) Dwarf galaxies have shallow potential wells and low escape velocities**
* **Explanation:** The depth of a galaxy's gravitational well is determined by its mass. Dwarf galaxies have very low masses ($M \sim 10^7 - 10^9 M_\odot$), leading to shallow potential wells and low escape velocities ($v_{\text{esc}} \approx 30\text{ km/s}$). Stellar winds and supernova shockwaves easily exceed this limit, blowing gas into the intergalactic medium and shutting off star formation.

#### 28. The Star Formation Main Sequence (SFMS) has a sub-linear slope ($b \approx 0.8$) in $\log \text{SFR}$ vs $\log M_*$. What does this indicate about galaxy growth efficiency?
* **Correct Answer:** **B) Low-mass galaxies form stars more efficiently per unit mass (higher $\text{sSFR}$) than massive galaxies**
* **Explanation:** The Star Formation Main Sequence has a slope of $b \approx 0.8$ (sub-linear). Specific Star Formation Rate is defined as $\text{sSFR} = \text{SFR}/M_*$. Since $\text{SFR} \propto M_*^{0.8}$, we get $\text{sSFR} \propto M_*^{-0.2}$. This negative exponent means that as stellar mass increases, the sSFR decreases; hence, lower-mass galaxies are actively forming stars at a faster rate *relative to their current size* than massive galaxies.

#### 29. Two identical stars are observed, with Star B situated exactly 10 times further away than Star A. By how many magnitudes fainter will Star B appear?
* **Correct Answer:** **B) 5.0 magnitudes fainter**
* **Explanation:** Apparent brightness (flux $F$) follows the inverse-square law: $F \propto 1/d^2$. Star B is 10 times further than Star A, so its flux is $1/10^2 = 1/100$ of Star A. The magnitude system is defined such that a factor of 100 in flux difference corresponds to exactly 5.0 magnitudes:
  $$m_B - m_A = 5 \log_{10}(d_B / d_A) = 5 \log_{10}(10) = 5.0$$

#### 30. Why did Big Bang Nucleosynthesis fail to synthesize carbon, leaving the early universe with only light elements?
* **Correct Answer:** **B) The universe cooled and diluted too rapidly to permit the triple-alpha helium fusion process**
* **Explanation:** Carbon synthesis requires the triple-alpha process, where three helium-4 nuclei ($^4\text{He}$) collide almost simultaneously to form carbon-12 ($^{12}\text{C}$). This requires extreme temperatures and densities. During Big Bang Nucleosynthesis, by the time helium was synthesized, the universe's rapid expansion had cooled and diluted the plasma below the threshold required for three-body collisions, halting nucleosynthesis at lithium.
