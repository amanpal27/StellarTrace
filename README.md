# Stellar Trace: Physics-Informed Machine Learning for Astronomical Transients

Welcome to **Stellar Trace**, an advanced undergraduate summer research and curriculum project offered by the **Astronomy Club**. 

This repository houses the end-to-end computational pipeline, research notebooks, and interactive simulation tools designed to study the host galaxy environments of astronomical transients (such as Core-Collapse and Type Ia Supernovae). The curriculum bridges the gap between statistical astrophysics, classical machine learning classifiers, and state-of-the-art **Physics-Informed Machine Learning (PIML)** convolved solvers.

---

## 👥 The Astronomy Club Team

This project was developed, audited, and executed during the Astronomy Club Summer Program.

### 🌟 Project Mentors
*   **Aman Pal** (Lead Mentor & Pipeline Architect)
*   **Preet Varu** (Statistical Modeling & MCMC Diagnostics)
*   **Aric Tirkey** (PyTorch PINN Design & Optimization)
*   **Ujjwal Prakash** (Streamlit WebGL Simulator & UX Lead)

### 🚀 Student Mentees
Our mentees cloned this repository, ran the physical simulations, bypassed database firewalls, and implemented the machine learning/convolution solvers across their individual assignment forks:
*   **Adit Bansal** & **Ankita Chatterjee**
*   **Aryan Trivedi** & **Chethana Kotla**
*   **Deeksha Badhan** & **Dhairya Garg**
*   **Gurmannat** & **Kanak**
*   **Kuldeep Turkar** & **Kushagra Rajput**
*   **Rajit Dhakad** & **Shriom Gupta**
*   **Sree Neha Reddy Gavva** & **Yash Kumar**

---

## 🌌 Project Overview & Working

The codebase is organized around a multi-phase research curriculum designed to model galaxy populations and transient rates:

```
[Volume-Complete Universe] ──> [Apply Telescope Limits (Malmquist Bias)]
                                          │
                                          ▼
[2D KS Testing (Fasano 1987)] <── [SDSS Ingestion & Cross-Matching]
              │
              ▼
[Stratified Split & ROS] ──> [MLP Multi-Class Tuning] ──> [OOP Engine]
                                                               │
                                                               ▼
[PyTorch DTD Convolution] <── [MCMC Bayesian Rate Fitting (A+B)]
```

### 1. Milestone 1: The Volume-Complete Universe
We generate a synthetic universe of $100,000$ galaxies by sampling physical scaling relations:
*   **Galaxy Mass Function:** Star mass ($M_\star$) is sampled from a Schechter mass function.
*   **Star Formation Main Sequence (SFMS):** Active star formation rate (SFR) is computed using a 2nd-degree polynomial mass relation.
*   **Color Bimodality:** Galaxy color $(g-r)$ is derived from the Specific Star Formation Rate ($\text{ssfr} = \log_{10} \text{SFR} - \log_{10} M_\star$) and stellar population synthesis models (Bell & de Jong 2001).

### 2. Phase 2: Observational Selection & Non-Parametric Statistics
*   **Malmquist Bias (Task 7):** Real telescopes are flux-limited, not volume-complete. We calculate luminosity distance $D_L(z)$ using a flat $\Lambda$CDM cosmology and apply an SDSS spectroscopic sensitivity mask ($m_r < 23.5$) to simulate observational selection effects.
*   **Data Ingestion & Cross-Matching (Task 8):** Ingests real Core-Collapse hosts (Sharma et al. 2024) and queries SDSS DR17 coordinates to link Type Ia supernovae to their host environments. Bypasses WAF blocks using flattened SQL syntax.
*   **2D Kolmogorov-Smirnov Test (Task 9):** Implements the Fasano & Franceschini (1987) 2D K-S test on the 2D Mass-sSFR plane to prove that supernova hosts occupy a distinct physical subspace compared to background field galaxies.

### 3. Phase 2: Machine Learning Host Classification
*   **Oversampling without Data Leakage (Task 10):** Resolves the massive class imbalance (150 field galaxies vs. 30 CC-SN vs. 20 Ia-SN) by implementing a stratified train-test split *before* performing random oversampling (ROS) to prevent validation contamination.
*   **MLP Optimization (Task 11):** Trains a Multi-Layer Perceptron (MLP) classifier, optimizing hidden layer sizes, activations (ReLU/tanh), and weight decay ($\alpha$) via 5-fold cross-validation (`GridSearchCV`).
*   **Permutation Importance & OOP wrapping (Task 12):** Computes feature importances using column shuffling to extract the network's learned rules, and wraps the preprocessors and classifiers into a production-grade class `StellarTraceEngine`.

### 4. Phase 2: Physics-Informed ML & Bayesian Parameter Recovery
*   **Bayesian MCMC Rate Fitting (Task 13):** Fits prompt-delayed "A+B" rate equations to Type Ia hosts using Maximum Likelihood Estimation and a pure NumPy Metropolis-Hastings MCMC sampler, plotting joint posterior parameter degeneracies.
*   **PyTorch convolved DTD Solver (Task 15):** Reconstructs the delay time distribution power-law slope ($\Psi(\tau) \propto \tau^{-\gamma}$) of white dwarf binary mergers by convolving delayed-exponential galaxy Star Formation Histories:
    $$R_{\text{Ia}}(t) = \int_0^t \text{SFR}(t - \tau) \tau^{-\gamma} d\tau$$
    using a vectorized PyTorch convolved solver optimized with Adam.

---

## 📁 Repository Structure

```
StellarTrace/
├── dashboard/
│   ├── app.py                     # Streamlit 3D simulator & quiz application
│   └── requirements.txt           # Dashboard package dependencies
├── notebooks/
│   ├── stellar_trace_assignment1.ipynb  # Mentees' Milestone 1 Assignment
│   ├── stellar_trace_assignment2.ipynb  # Mentees' Phase 2 Assignment
│   ├── stellar_trace_solution1.ipynb    # Milestone 1 Solutions
│   └── stellar_trace_solution2.ipynb    # Phase 2 Solutions
├── data/
│   ├── mock_universe_catalog.csv  # Simulated galaxy catalog (11MB)
│   ├── sharma_hosts.dat           # Real CC-SN hosts data
│   └── sdss_data.dat              # SDSS query backup data
├── scripts/
│   ├── galfrb_project_pipeline.py # Computational pipelines
│   ├── generate_notebooks.py      # Notebook generator part 1
│   └── generate_notebooks_part2.py# Notebook generator part 2
├── slides/                        # LaTeX Beamer slide decks and tutorials
│   ├── session1_tasks7_9.tex      # Session 1 slides (Observational selection)
│   ├── session2_tasks10_12.tex    # Session 2 slides (ML Host classification)
│   ├── session3_tasks13_15.tex    # Session 3 slides (MCMC & DTD solver)
│   └── ... (tutorials for Stats, Neural Networks, PIML, and MCMC)
├── quizzes/
│   ├── stellar_trace_mentee_quiz.md      # Written academic test
│   ├── stellar_trace_mentor_answer_key.md # Mentor evaluation key
│   └── ... (PDF and spreadsheet quiz templates)
├── frontend/                      # React/Vite interactive showcase site
│   ├── src/                       # Custom source code (Galaxy, MCMC, DTD sims)
│   └── package.json               # Frontend dependencies
├── submissions/                   # Assignment submissions folder
│   ├── Adit_Bansal/               # Individual mentee folders with .gitkeep
│   ├── ... (all 14 mentees)
└── README.md                      # This documentation file
```

---

## 🛠️ Installation & Setup

To set up the environment and run the pipeline or the dashboard locally, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/StellarTrace.git
cd StellarTrace
```

### 2. Configure Virtual Environment & Install Dependencies
Ensure you have Python 3.10+ installed. Create a clean virtual environment and install the required scientific libraries:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r dashboard/requirements.txt
```

### 3. Run the Streamlit Simulation Dashboard
Launch the deployable interactive dashboard containing the 3D galaxy physics particle simulator (rendered via WebGL/Three.js) and the Cosmic Challenge gamified quiz:
```bash
streamlit run dashboard/app.py
```

### 4. Running the Jupyter Notebooks
To run and execute the assignments or review the reference solutions:
```bash
pip install jupyter
jupyter notebook
```
Navigate to the `notebooks/` folder and open the assignments.

---

## 📝 Mentee Submission Guide

If you are a mentee in the summer program, please follow this workflow to submit your completed assignments:
1. **Fork** this repository to your personal GitHub account.
2. Complete the code exercises in `stellar_trace_assignment1.ipynb` and `stellar_trace_assignment2.ipynb`.
3. Copy your completed notebooks into your dedicated folder inside `submissions/` (e.g., `submissions/Aryan_Trivedi/stellar_trace_assignment1.ipynb`).
4. Commit your changes and push them to your fork:
   ```bash
   git add submissions/Aryan_Trivedi/
   git commit -m "Submit assignment 1 - Aryan Trivedi"
   git push origin main
   ```
5. Open a **Pull Request** (PR) comparing your fork's submission folder against the main repository. Your assigned mentors will review your code, check the validation plots, and merge your submissions!

---

## 🔬 Scientific References
*   **Sharma et al. 2024:** Core-Collapse Supernova host properties.
*   **Lampeitl et al. 2010:** SDSS-II Supernova Survey host correlations.
*   **Fasano & Franceschini 1987:** A multidimensional version of the Kolmogorov-Smirnov test.
*   **Bell & de Jong 2001:** Stellar mass-to-light ratios and galaxy colors.
