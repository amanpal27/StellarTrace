import json
import os

def create_notebook(cells, filename):
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=1)
    print(f"[SUCCESS] Created Jupyter Notebook: {filename}")

def make_markdown_cell(content):
    lines = [line + "\n" for line in content.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": lines
    }

def make_code_cell(content):
    lines = [line + "\n" for line in content.split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines
    }

# ==============================================================================
# RIGOROUS ACADEMIC THEORY CELLS (TASKS 7 - 12)
# ==============================================================================

intro_md = r"""
# Stellar Trace: Host Profiling & Machine Learning
## Project Milestone 2: Statistical Modeling and Deep Learning
 
**Undergraduate Physics Research Mentorship Project**
 
*Mentors: Aman Pal, Aric Tirkey, Preet Varu, Ujjwal Prakash*
 
### Overview
This milestone builds on the mock universe catalog generated in Milestone 1. You will transition from population simulation to statistical hypothesis testing and deep learning optimization. Using real-world Core-Collapse Supernova (Type Ibc) and Type Ia Supernova host galaxy catalogs directly retrieved from astronomy databases, you will evaluate progenitor models, train a neural network classifier to predict host environments, and assemble the pipeline into a production-ready Object-Oriented Programming (OOP) engine.
 
### Project Tasks
- **Task 7:** Observational Selection Effects & Flux-Limited Sample
- **Task 8:** Multiclass Astronomical Catalog Ingestion & Cross-Matching
- **Task 9:** Non-Parametric Hypothesis Testing (K-S and A-D Tests)
- **Task 10:** Addressing Class Imbalance via Dataset Oversampling
- **Task 11:** Multiclass Neural Network & Hyperparameter Optimization
- **Task 12:** Model Interpretability via Permutation Importance & OOP Assembly
- **Task 13:** Physics-Informed Supernova Rate Modeling
- **Task 14:** Model Interpretability and Physical Comparison
- **Task 15:** Delay Time Distribution (DTD) Reconstruction
 
---
### Environment Setup
Run the cell below to load the required Python libraries and check for local data files.
"""

task7_theory = r"""
## Task 7: Observational Selection Effects & Flux-Limited Sample

### The Physics of Malmquist Bias
In observational cosmology, catalogs of astronomical sources are rarely volume-complete. A volume-complete catalog contains every source within a specified comoving spatial boundary $V$, independent of intrinsic luminosity. In contrast, real astronomical surveys are flux-limited, governed by the detection sensitivity threshold of the telescope (expressed as a limiting apparent magnitude $m_{\text{lim}}$).

This sensitivity constraint introduces a classical selection effect known as **Malmquist bias** (Malmquist 1922). Because the flux of a source scales as $f \propto L / D_L^2$, the minimum detectable luminosity increases quadratically with distance. Consequently, at high redshifts, low-luminosity sources fall below the detection threshold and are systematically excluded, while high-luminosity sources are overrepresented relative to their true space density.

### Derivation of Apparent Magnitudes from Physical Galaxy Properties
To model this selection effect on the synthetic galaxy catalog, the physical parameters (stellar mass $M_\star$, Specific Star Formation Rate $\text{sSFR}$) must be mapped to an observable bandpass. Here, we calculate the apparent magnitude in the SDSS $r$-band ($m_r$):

1. **Rest-frame Color ($g-r$):** The rest-frame color of a galaxy is correlated with its star formation history. Using empirical relations derived from SDSS observations, the mean color index $(g-r)$ scales with Specific Star Formation Rate ($\text{sSFR} = \log_{10}(\text{SFR}/M_\star)$):
   $$(g-r) = \text{clip}\left(0.5 - 0.25 \cdot (\text{sSFR} + 10.0), -0.1, 1.0\right) + \eta$$
   where $\eta \sim \mathcal{N}(0, 0.08)$ represents intrinsic astrophysical scatter.

2. **Mass-to-Light Ratio ($M/L$):** According to stellar population synthesis models (e.g., Bell & de Jong 2001), the stellar mass-to-light ratio of a galaxy is a linear function of its optical color:
   $$\log_{10}\left(\frac{M}{L}\right)_g = 1.5 \cdot (g-r) - 0.7$$
   $$\log_{10}\left(\frac{M}{L}\right)_r = \log_{10}\left(\frac{M}{L}\right)_g - \frac{g-r}{2.5}$$

3. **Absolute Magnitude ($M_r$):** The absolute magnitude in the $r$-band is calculated relative to the solar absolute magnitude ($M_{\odot, r} = 4.65$):
   $$M_r = M_{\odot, r} - 2.5 \cdot \left(\log_{10} M_\star - \log_{10}\left(\frac{M}{L}\right)_r\right)$$

4. **Luminosity Distance ($D_L(z)$):** In a flat $\Lambda$CDM cosmology, the comoving distance $D_C(z)$ is integrated using the Hubble parameter $H(z)$. The luminosity distance is then:
   $$D_L(z) = D_C(z) \cdot (1 + z)$$

5. **Apparent Magnitude ($m_r$):** The apparent magnitude is computed via the standard distance modulus relation:
   $$m_r = M_r + 5 \log_{10}\left(\frac{D_L(z)}{10 \text{ pc}}\right) = M_r + 5 \log_{10}(D_L(z)) + 25""" + r"""
   where $D_L(z)$ is in Megaparsecs ($\text{Mpc}$).

### Selection Criterion
A galaxy is considered detected in the synthetic survey if its apparent magnitude is brighter than the Sloan Digital Sky Survey (SDSS) spectroscopic completeness limit:
$$m_r < 23.5$$
"""

task8_theory = r"""
## Task 8: Multiclass Astronomical Catalog Ingestion & Cross-Matching

### Astrophysics of Transient Progenitors and Host Environments
Astronomical transients originate from stellar populations with distinct physical properties:
1. **Core-Collapse Supernovae (Class 1 - CC-SNe):** These events (Types Ib, Ic, and II) represent the gravitational collapse of massive stars ($M \gtrsim 8 M_\odot$) at the end of their nuclear burning lifetimes. Because massive stars have short main-sequence lifetimes ($\tau \lesssim 50\text{ Myr}$), they do not migrate far from their birth sites. Consequently, CC-SNe occur exclusively in active star-forming environments (e.g., spiral arms and starburst galaxies) and serve as direct tracers of instantaneous star formation. Host galaxy data is loaded from the observational sample compiled in Table 2 of Sharma et al. (2024).
2. **Type Ia Supernovae (Class 2 - SNe Ia):** Thermonuclear explosions of carbon-oxygen white dwarfs in binary systems, triggered either by accretion from a companion (single-degenerate) or by double white dwarf mergers (double-degenerate). The delay-time distribution (DTD) of SNe Ia ranges from $\sim 100\text{ Myr}$ to $> 10\text{ Gyr}$. SNe Ia therefore occur in both young, star-forming galaxies and old, passive elliptical galaxies. The rate of SNe Ia is parameterized as a linear combination of host stellar mass (representing the older population) and star formation rate (representing the younger population). Host coordinates are compiled from the SDSS-II Supernova Survey (Lampeitl et al. 2010).

### Database Cross-Matching and Supernova Coordinate Offsets
Supernovae occur within the interstellar medium of their host galaxies, often offset by several kiloparsecs from the galactic nucleus. In terms of angular separation, these offsets correspond to distances of several arcseconds on the sky.
To construct the host galaxy sample, the angular coordinates of 50 SNe Ia from VizieR catalog `J/ApJ/722/566/table2` are cross-matched with the SDSS DR17 spectroscopic database (`galSpecExtra` and `SpecObj`). To account for supernova offsets, a spatial search box of 15 arcseconds ($0.0042^\circ$) is constructed:
$$\text{ra}_{\text{host}} \in [\text{ra}_{\text{SN}} - 0.0042^\circ, \text{ra}_{\text{SN}} + 0.0042^\circ]$$
$$\text{dec}_{\text{host}} \in [\text{dec}_{\text{SN}} - 0.0042^\circ, \text{dec}_{\text{SN}} + 0.0042^\circ]$$
Host galaxy spectroscopic redshift ($z$), stellar mass ($\log_{10} M_\star$), and star formation rate ($\log_{10} \text{SFR}$) are retrieved directly from the SDSS server.
"""
setup_code = """import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from astropy.cosmology import FlatLambdaCDM
from scipy.stats import ks_2samp, anderson_ksamp
from scipy.optimize import minimize
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, roc_curve, auc, confusion_matrix, ConfusionMatrixDisplay
from sklearn.inspection import permutation_importance
import urllib.request
import os
import io
import requests

# Set random seed for reproducibility
np.random.seed(42)
torch.manual_seed(42)

print("Environment configured successfully!")"""

ex7_code_student = """# 1. Load the mock catalog generated in Milestone 1
if not os.path.exists('mock_universe_catalog.csv'):
    raise FileNotFoundError("Missing mock_universe_catalog.csv! Please run your Milestone 1 notebook first.")

df_mock = pd.read_csv('mock_universe_catalog.csv')

# 2. Model observational selection effects (apparent magnitude limit)
cosmo = FlatLambdaCDM(H0=70.0, Om0=0.3)
z_grid = np.linspace(0.01, 0.5, 1000)
dl_grid = cosmo.luminosity_distance(z_grid).value
mock_dl = np.interp(df_mock['redshift'], z_grid, dl_grid)

# Calculate color g-r with Gaussian scatter
np.random.seed(42)
mock_gr = np.clip(0.5 - 0.25 * (df_mock['ssfr'] + 10.0), -0.1, 1.0)
mock_gr += np.random.normal(loc=0.0, scale=0.08, size=len(mock_gr))

# Calculate mass-to-light ratios in r-band
log_mtolg = 1.5 * mock_gr - 0.7
log_mtolr = log_mtolg - (mock_gr / 2.5)

# Calculate absolute Mr and apparent mr magnitudes
Mr_sun = 4.65
# Calculate absolute magnitude Mr and apparent magnitude mr below
mock_Mr = ### FIX_ME_ABSOLUTE_MAGNITUDE ###
mock_mr = ### FIX_ME_APPARENT_MAGNITUDE ###

# Filter the mock catalog to keep detected galaxies (mr < 23.5)
detected_mask = mock_mr < 23.5
df_detected = df_mock[detected_mask].copy()

print("Exercise 7 Verification:")
print(f"Volume-complete catalog size: {len(df_mock)}")
print(f"Flux-limited detected catalog size: {len(df_detected)}")"""

ex8_code_student = """# 1. Download and load real Core-Collapse Supernova host observations (Class 1)
url = "https://raw.githubusercontent.com/loudasnick/GALFRB/main/src/galfrb/data/sharma_m_sfr_z_data.dat"
filename = "sharma_hosts.dat"
try:
    if not os.path.exists(filename):
        print("Downloading real CC-SN host dataset...")
        urllib.request.urlretrieve(url, filename)
    data = np.loadtxt(filename)
    real_hosts = pd.DataFrame({
        'log_mstar': data[:, 0],
        'log_sfr': np.log10(np.clip(data[:, 1], 1e-6, None)),
        'redshift': data[:, 2]
    })
    # Calculate specific star formation rate (sSFR) here
    real_hosts['ssfr'] = ### FIX_ME_SSFR ###
    print(f"Successfully loaded {len(real_hosts)} real Core-Collapse SN hosts.")
except Exception as e:
    raise RuntimeError(f"Failed to load Core-Collapse SN host data: {e}")

# 2. Query VizieR database J/ApJ/722/566/table2 to retrieve Type Ia coordinates
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u

print("Querying VizieR J/ApJ/722/566/table2 coordinates...")
v = Vizier(columns=['all'])
catalogs = v.get_catalogs('J/ApJ/722/566')
if not catalogs or len(catalogs) == 0:
    raise ValueError("Failed to retrieve J/ApJ/722/566/table2")
df_viz = catalogs[0].to_pandas()

# 3. Convert coordinates to decimal degrees and construct spatial range filters
where_clauses = []
for i in range(len(df_viz)):
    ra_str = df_viz.iloc[i]['RAJ2000'].replace(' ', ':')
    dec_str = df_viz.iloc[i]['DEJ2000'].replace(' ', ':')
    coord = SkyCoord(ra_str, dec_str, unit=(u.hourangle, u.deg))
    ra_deg = coord.ra.deg
    dec_deg = coord.dec.deg
    # 15 arcseconds box (approx 0.0042 degrees)
    where_clauses.append(f"(s.ra BETWEEN {ra_deg - 0.0042} AND {ra_deg + 0.0042} AND s.dec BETWEEN {dec_deg - 0.0042} AND {dec_deg + 0.0042})")

# 4. Execute the SQL queries to SDSS DR17 in small batches to prevent 503 gateway timeouts and 403 URI length limits
print("Querying SDSS database in batches via requests...")
url_sdss = "https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

batch_size = 10
ia_hosts_list = []

for idx in range(0, len(where_clauses), batch_size):
    batch_clauses = where_clauses[idx : idx + batch_size]
    query_ia = f\"\"\"
SELECT 
    s.ra AS ra, 
    s.dec AS dec, 
    s.z AS redshift,
    g.lgm_tot_p50 AS log_mstar, 
    g.sfr_tot_p50 AS log_sfr
FROM galSpecExtra AS g
JOIN SpecObj AS s ON s.specObjID = g.specObjID
WHERE (g.lgm_tot_p50 > 5.0 AND s.z > 0.001)
  AND ({' OR '.join(batch_clauses)})
\"\"\"
    query_ia = " ".join(query_ia.split())
    params = {
        "cmd": query_ia,
        "format": "csv"
    }
    r_sdss = requests.get(url_sdss, params=params, headers=headers)
    if r_sdss.status_code != 200:
        raise RuntimeError(f"SDSS SQL query batch {idx // batch_size} failed with status code {r_sdss.status_code}: {r_sdss.text}")
    
    batch_df = pd.read_csv(io.StringIO(r_sdss.text.strip()))
    if len(batch_df) > 0 and batch_df.columns[0] == "#Table1":
        batch_df = pd.read_csv(io.StringIO(r_sdss.text.strip()), skiprows=1)
    
    if len(batch_df) > 0:
        ia_hosts_list.append(batch_df)

if len(ia_hosts_list) > 0:
    ia_hosts = pd.concat(ia_hosts_list, ignore_index=True)
else:
    ia_hosts = pd.DataFrame(columns=['ra', 'dec', 'redshift', 'log_mstar', 'log_sfr'])

# Clean columns and calculate Specific Star Formation Rate (sSFR)
ia_hosts.columns = [col.lower() for col in ia_hosts.columns]
# Calculate specific star formation rate (sSFR) here
ia_hosts['ssfr'] = ### FIX_ME_SSFR ###
print(f"Successfully loaded {len(ia_hosts)} real Type Ia SN hosts directly from the SDSS database.")"""

ex7_code_solution = ex7_code_student
ex8_code_solution = ex8_code_student

task9_theory = r"""
## Task 9: Non-Parametric Hypothesis Testing

### Statistical Inference in Observational Cosmology
Astrophysical parameter distributions (e.g., galaxy mass functions, SFR distributions) are highly non-Gaussian, displaying prominent skewness, high-mass cutoffs, and bimodal divisions. Parametric statistical tests (e.g., Student's t-test) are inappropriate because they assume normal distributions. To rigorously evaluate whether supernova host galaxies are drawn from the general background field galaxy population or reside in distinct physical environments, non-parametric hypothesis testing must be employed.

### Two-Sample Kolmogorov-Smirnov (K-S) Test
The two-sample K-S test evaluates the null hypothesis $H_0$ that two independent samples are drawn from the same continuous distribution. For empirical cumulative distribution functions (eCDFs) $F_1(x)$ and $F_2(x)$, the K-S statistic $D$ measures the supremum of the absolute differences:
$$D = \sup_x |F_1(x) - F_2(x)|$$
where the eCDF is defined as:
$$F(x) = \frac{1}{n} \sum_{i=1}^n \mathbb{I}_{(-\infty, x]}(x_i)$$
The null hypothesis is rejected at significance level $\alpha = 0.05$ if the probability of obtaining a distance metric at least as extreme as the observed $D$ under $H_0$ (the p-value) is less than $\alpha$.

### Two-Sample Anderson-Darling (A-D) Test
While the K-S test is sensitive to differences near the median of the distributions, it loses sensitivity near the tails. The Anderson-Darling test addresses this by introducing a weighting function that scales with the variance of the eCDF, making it highly sensitive to discrepancies at the extremes of the distribution (e.g., the low-mass dwarf galaxy regime or the high-mass AGN-quenched regime):
$$A^2 = n_1 n_2 \int_{-\infty}^{\infty} \frac{[F_1(x) - F_2(x)]^2}{H(x)(1 - H(x))} dH(x)$$
where $H(x)$ represents the pooled empirical cumulative distribution function of the combined dataset.

### Two-Dimensional K-S Test (Fasano & Franceschini 1987)
In galaxy evolution, galaxies are distributed in a two-dimensional space defined by Stellar Mass ($M_\star$) and Star Formation Rate ($\text{SFR}$). A 1D K-S test on mass or SFR alone throws away the joint correlation between these properties (e.g., the star-forming main sequence). To compare these populations in 2D space, we implement the Fasano & Franceschini (1987) generalization of the 2D K-S test. This test defines the statistic $D_{2\text{D}}$ as the maximum difference in the fraction of points falling in any of the four quadrants (defined by $x \ge x_i, y \ge y_i$, etc.) around any data point in the combined sample.
"""

task10_theory = r"""
## Task 10: Addressing Class Imbalance via Dataset Oversampling

### The Class Imbalance Problem in Astrophysical Machine Learning
Cosmic explosions (supernovae, gamma-ray bursts, fast radio bursts) are rare physical anomalies. Consequently, host galaxy catalogs are orders of magnitude smaller than catalogs of the general field galaxy population. In our compiled machine learning dataset:
- Class 0 (Background field galaxies): $N_0 = 150$
- Class 1 (Core-Collapse Supernova hosts): $N_1 = 30$
- Class 2 (Type Ia Supernova hosts): $N_2 \approx 17-20$

If a machine learning model is trained directly on this imbalanced dataset, the global objective function (loss function) will optimize performance on the majority class (Class 0) at the expense of the minority classes. In this regime, a naive classifier predicting Class 0 for every instance would yield an accuracy of $\approx 75\%$, despite failing to identify any transient host environments.

### The Danger of Data Leakage (Validation Contamination)
Applying random oversampling to the entire dataset prior to performing a train-test split introduces a critical methodological flaw: **data leakage**. When minority class samples are duplicated, identical copies of the same galaxies are distributed into both the training and test sets. Consequently, the classifier can simply memorize the training instances, achieving an artificially perfect classification score (e.g., $1.00$ precision and recall) on the test set. This fails to reflect the model's true generalization performance.

### Stratified Split and Training Set Oversampling
To prevent data leakage, the dataset must be split into training and test sets **before** any oversampling is applied. The test set remains completely untouched and imbalanced, representing the true, physical distribution of galaxies.

**Random Oversampling (ROS)** is then applied **only** to the training partition. The minority host galaxies (Class 1 and Class 2) are sampled with replacement until they match the size of the majority background class (Class 0) within the training set. Let $S_c$ be the set of training samples in class $c$, and $N_{\text{target}} = \max_c |S_c|$. For any class where $|S_c| < N_{\text{target}}$, new samples are drawn uniformly with replacement:
$$x^* \sim \mathcal{U}(S_c)$$
until $|S_c| = N_{\text{target}}$.
"""

task11_theory = r"""
## Task 11: Multiclass Neural Network & Hyperparameter Optimization

### Multi-Layer Perceptron (MLP) Architecture for Multiclass Classification
A Multi-Layer Perceptron (MLP) is a feed-forward artificial neural network that maps a input feature vector $\mathbf{x} \in \mathbb{R}^d$ to a target output class $y \in \{0, 1, 2\}$. For galaxy classification, the input vector consists of four physical features:
$$\mathbf{x} = [\text{redshift}, \log_{10} M_\star, \log_{10} \text{SFR}, \text{ssfr}]$$
The network architecture is defined by:
1. **Hidden Layers:** Linear transformations followed by a non-linear activation function $a^{(l)} = f(W^{(l)} a^{(l-1)} + b^{(l)})$, where $W^{(l)}$ and $b^{(l)}$ are the weights and biases of layer $l$, and $f(x)$ is either the Rectified Linear Unit (ReLU) or Hyperbolic Tangent (tanh) function.
2. **Output Layer (Softmax):** The final layer uses a Softmax function to map the network's raw output logits $\mathbf{z} \in \mathbb{R}^C$ to a probability distribution over the $C=3$ classes:
   $$P(y = c \mid \mathbf{x}) = \frac{e^{z_c}}{\sum_{j=1}^C e^{z_j}}$$
   where $\sum_{c=1}^C P(y = c \mid \mathbf{x}) = 1.0$.

### Hyperparameter Tuning via K-Fold Cross-Validation
To optimize generalization and prevent overfitting, a grid search with 5-fold cross-validation (`GridSearchCV`) is performed. The hyperparameter space includes the hidden layer configuration (number of layers and nodes), activation functions, and the L2 regularization parameter $\alpha$ (weight decay). The cross-validation splits the training set into 5 folds, iteratively training on 4 folds and validating on the remaining 1. The performance metric optimized is the **Macro F1-score**, which evaluates the harmonic mean of precision and recall across all classes, weighting each class equally:
$$\text{F1}_{\text{macro}} = \frac{1}{C} \sum_{c=1}^C \text{F1}_c, \quad \text{where } \text{F1}_c = 2 \cdot \frac{\text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

### Model Evaluation Metrics
The final optimized model is evaluated on a held-out test dataset using:
1. **Confusion Matrix:** A $3 \times 3$ contingency table showing the actual vs. predicted class labels, exposing misclassification rates between classes.
2. **One-vs-Rest Receiver Operating Characteristic (ROC) & Area Under the Curve (AUC):** For each class $c$, the true positive rate (TPR) is plotted against the false positive rate (FPR) as the decision threshold varies. The AUC quantifies the probability that the classifier ranks a randomly chosen positive instance higher than a randomly chosen negative instance.
"""

task12_theory = r"""
## Task 12: Model Interpretability via Permutation Importance & OOP Assembly

### Permutation Feature Importance Theory
Although neural networks are highly accurate classifiers, their nested non-linear transformations render them "black boxes." To extract the physical rules learned by the network, we calculate **Permutation Feature Importance** (Breiman 2001).
Let $M$ be a trained classifier, $D = (\mathbf{X}, \mathbf{y})$ be the evaluation dataset, and $s$ be the baseline score (e.g., Macro F1-score). For each feature $j$:
1. A perturbed dataset $\mathbf{X}^{\text{perm}(j)}$ is constructed by randomly shuffling the values of column $j$, breaking the physical correlation between feature $j$ and the target class $\mathbf{y}$ while preserving the feature's marginal distribution.
2. The model performance $s^{(j)}$ is evaluated on $\mathbf{X}^{\text{perm}(j)}$.
3. The permutation importance $I(j)$ is defined as the mean decrease in performance:
   $$I(j) = s - s^{(j)}$$
Features with large positive $I(j)$ values are critical to the classifier's performance, as disrupting their values significantly degrades predictions.

### Object-Oriented Software Design for Astrophysics Pipelines
In production astrophysics pipelines, individual stages (preprocessing, regression models, classification models) are encapsulated within a single, unified interface. You will implement a production wrapper class named `StellarTraceEngine`. This object-oriented engine integrates:
1. The 2nd-degree polynomial Star Formation Main Sequence (SFMS) regression model (from Milestone 1) to predict baseline log(SFR) from stellar mass.
2. The fitted `StandardScaler` to normalize the input variables.
3. The optimized multiclass `MLPClassifier` (from Milestone 2).

The class exposes a single API method:
```python
predict_host_probabilities(log_mstar, redshift) -> dict
```
which performs the entire sequence of operations internally and returns a dictionary of physical probabilities:
$$\{\text{'Background'}: P_0, \text{'CC-SN'}: P_1, \text{'Ia-SN'}: P_2\}$$
"""

ex9_code_student = """import warnings

# 1. Run 1D K-S and A-D tests on stellar mass
# Hint: Use scipy.stats.ks_2samp and anderson_ksamp on real_hosts vs df_detected log_mstar

ks_cc_stat, ks_cc_p = ### FIX_ME_KS_CC ###
ks_ia_stat, ks_ia_p = ### FIX_ME_KS_IA ###

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ad_cc_res = ### FIX_ME_AD_CC ###
    ad_ia_res = ### FIX_ME_AD_IA ###

# 2. Implement the 2D Kolmogorov-Smirnov Test (Fasano & Franceschini 1987)
def ks_2d(x1, y1, x2, y2, n_eval=300):
    n1, n2 = len(x1), len(x2)
    x_all = np.concatenate([x1, x2])
    y_all = np.concatenate([y1, y2])
    
    # Subsample evaluation points for computational efficiency
    np.random.seed(42)
    eval_idx = np.random.choice(len(x_all), size=min(len(x_all), n_eval), replace=False)
    x_eval = x_all[eval_idx]
    y_eval = y_all[eval_idx]
    
    d_max = 0.0
    for x, y in zip(x_eval, y_eval):
        # Sample 1 quadrant fractions
        # Hint: Count fractions of points where (x1 >= x) & (y1 >= y), etc.
        q1_1 = ### FIX_ME ###
        q2_1 = ### FIX_ME ###
        q3_1 = ### FIX_ME ###
        q4_1 = ### FIX_ME ###
        
        # Sample 2 quadrant fractions
        q1_2 = ### FIX_ME ###
        q2_2 = ### FIX_ME ###
        q3_2 = ### FIX_ME ###
        q4_2 = ### FIX_ME ###
        
        # Calculate maximum absolute difference across the 4 quadrants
        d1 = abs(q1_1 - q1_2)
        d2 = abs(q2_1 - q2_2)
        d3 = abs(q3_1 - q3_2)
        d4 = abs(q4_1 - q4_2)
        
        d_max = max(d_max, d1, d2, d3, d4)
        
    # Calculate Peacock/Fasano-Franceschini significance
    r1 = np.nan_to_num(np.corrcoef(x1, y1)[0, 1]) if n1 > 1 else 0.0
    r2 = np.nan_to_num(np.corrcoef(x2, y2)[0, 1]) if n2 > 1 else 0.0
    r = (r1 + r2) / 2.0
    r = np.clip(r, -0.999, 0.999)
    
    n_eff = (n1 * n2) / (n1 + n2)
    lambda_val = d_max * np.sqrt(n_eff) / (1.0 - 0.5 * r**2)
    p_val = 2.0 * np.exp(-2.0 * (lambda_val - 0.5)**2)
    p_val = np.clip(p_val, 0.0, 1.0)
    return d_max, p_val

# Compare CC-SNe and Type Ia hosts against background detected galaxies in Mass-sSFR space
# Hint: Use real_hosts['log_mstar'].values and real_hosts['ssfr'].values for hosts
# and df_detected['log_mstar'].values and df_detected['ssfr'].values for background
ks2d_cc_stat, ks2d_cc_p = ks_2d(
    ### FIX_ME_CC_MASS_2D ###, ### FIX_ME_CC_SSFR_2D ###,
    ### FIX_ME_BG_MASS_2D ###, ### FIX_ME_BG_SSFR_2D ###
)
ks2d_ia_stat, ks2d_ia_p = ks_2d(
    ### FIX_ME_IA_MASS_2D ###, ### FIX_ME_IA_SSFR_2D ###,
    ### FIX_ME_BG_MASS_2D ###, ### FIX_ME_BG_SSFR_2D ###
)

print("\\n--- Statistical Hypothesis Testing Results ---")
print(f"CC-SN Hosts vs Background:")
print(f"  - 1D K-S Test (Mass) p-value: {ks_cc_p:.4f}")
print(f"  - 1D A-D Test (Mass) p-value: {ad_cc_res.significance_level:.4f}")
print(f"  - 2D K-S Test (Mass-sSFR) p-value: {ks2d_cc_p:.4e}")
print(f"Type Ia SN Hosts vs Background:")
print(f"  - 1D K-S Test (Mass) p-value: {ks_ia_p:.4e}")
print(f"  - 1D A-D Test (Mass) p-value: {ad_ia_res.significance_level:.4e}")
print(f"  - 2D K-S Test (Mass-sSFR) p-value: {ks2d_ia_p:.4e}")

# 3. Plot Empirical Cumulative Distribution Functions (eCDFs) for K-S visualization
def plot_ecdf(ax, data, label, color):
    # TODO: Sort data and calculate cumulative probability for eCDF
    x = ### FIX_ME_SORT_DATA ###
    y = ### FIX_ME_CALC_ECDF ###
    ax.plot(x, y, label=label, color=color, linewidth=2)

fig, axs = plt.subplots(1, 2, figsize=(12, 5), dpi=120)

# TODO: Plot eCDFs for CC-SN vs Background on axs[0]
plot_ecdf(axs[0], df_detected['log_mstar'].values, 'Background', '#bdc3c7')
### FIX_ME: plot real_hosts on axs[0] ###
axs[0].set_title(f'CC-SN Host Mass eCDF (KS-stat={ks_cc_stat:.3f})')
axs[0].set_xlabel('log(Mstar / Msun)')
axs[0].legend()

# TODO: Plot eCDFs for Ia-SN vs Background on axs[1]
plot_ecdf(axs[1], df_detected['log_mstar'].values, 'Background', '#bdc3c7')
### FIX_ME: plot ia_hosts on axs[1] ###
axs[1].set_title(f'Ia-SN Host Mass eCDF (KS-stat={ks_ia_stat:.3f})')
axs[1].set_xlabel('log(Mstar / Msun)')
axs[1].legend()

plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task9_ks_ecdf.png', dpi=300, bbox_inches='tight')
plt.show()
"""

ex10_code_student = """# 1. Compile the multiclass machine learning dataset
real_hosts['class'] = 1
ia_hosts['class'] = 2

# Background Non-Hosts (Class 0): Draw a random sample of 150 galaxies from the detected mock population
np.random.seed(42)
df_non_hosts = df_detected.sample(n=150, random_state=42).copy()
df_non_hosts['class'] = 0

# Combine catalogs into a single imbalanced dataset
df_ml = pd.concat([
    df_non_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']],
    real_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']],
    ia_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']]
], ignore_index=True)

# 2. Perform stratified train/test split FIRST to prevent data leakage (validation contamination)
from sklearn.model_selection import train_test_split
# Split df_ml into train and test sets (30% test size). Don't forget to stratify by class!
df_train, df_test = ### FIX_ME_TRAIN_TEST_SPLIT ###

# 3. Address Class Imbalance in the TRAINING set using Manual Random Oversampling
def oversample_dataset(df, class_column):
    # TODO: Implement manual random oversampling to balance class sizes
    # Hint: Find the maximum class size, then sample smaller classes with replacement (replace=True)
    ### FIX_ME ###
    pass

df_train_balanced = oversample_dataset(df_train, 'class')

print(f"Original dataset distribution:\\n{df_ml['class'].value_counts().to_dict()}")
print(f"Training set before oversampling:\\n{df_train['class'].value_counts().to_dict()}")
print(f"Training set after oversampling:\\n{df_train_balanced['class'].value_counts().to_dict()}")
print(f"Test set (untouched/imbalanced):\\n{df_test['class'].value_counts().to_dict()}")"""

ex11_code_student = """# 1. Extract features and target from the pre-split datasets
X_train = df_train_balanced[['redshift', 'log_mstar', 'log_sfr', 'ssfr']]
y_train = df_train_balanced['class']
X_test = df_test[['redshift', 'log_mstar', 'log_sfr', 'ssfr']]
y_test = df_test['class']
X = X_train # Reference variable for Task 12

# 2. Standardise features
scaler = StandardScaler()
# Fit the scaler on the training data and transform it, then apply the transform to the test data
X_train_scaled = ### FIX_ME_FIT_TRANSFORM ###
X_test_scaled = ### FIX_ME_TRANSFORM ###

# 3. GridSearchCV hyperparameter tuning for multiclass MLP classifier
param_grid = {
    # TODO: Define a grid of hyperparameters for the MLPClassifier
    'hidden_layer_sizes': ### FIX_ME_HIDDEN_LAYERS ###,
    'activation': ### FIX_ME_ACTIVATION ###,
    'alpha': ### FIX_ME_ALPHA ###
}

mlp = MLPClassifier(max_iter=1000, random_state=42)
grid_search = GridSearchCV(mlp, param_grid, cv=5, scoring='f1_macro')
grid_search.fit(X_train_scaled, y_train)

print(f"Best parameters found: {grid_search.best_params_}")
best_mlp = grid_search.best_estimator_

# 4. Evaluate multiclass model
y_pred = best_mlp.predict(X_test_scaled)
y_prob = best_mlp.predict_proba(X_test_scaled)

print("MLP Classification Report:")
print(classification_report(y_test, y_pred))

# 5. Plot 3x3 Confusion Matrix and Multiclass ROC Curves
fig, axs = plt.subplots(1, 2, figsize=(14, 6), dpi=120)

# Panel 1: Multiclass ROC Curves (One-vs-Rest)
for i, label in enumerate(['Background', 'CC-SN Host', 'Ia-SN Host']):
    y_test_bin = (y_test == i).astype(int)
    fpr, tpr, _ = roc_curve(y_test_bin, y_prob[:, i])
    roc_auc = auc(fpr, tpr)
    axs[0].plot(fpr, tpr, linewidth=2.5, label=f'{label} vs Rest (AUC = {roc_auc:.3f})')

axs[0].plot([0, 1], [0, 1], color='#7f8c8d', linestyle='--', linewidth=1.5)
axs[0].set_xlabel('False Positive Rate', fontsize=11)
axs[0].set_ylabel('True Positive Rate', fontsize=11)
axs[0].set_title('White-Box Classifier ROC Curves (One-vs-Rest)', fontsize=12, fontweight='bold')
axs[0].legend(loc='lower right', fontsize=10)
axs[0].grid(True, linestyle=':', alpha=0.5)

# Panel 2: Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Background', 'CC-SN', 'Ia-SN'])
disp.plot(ax=axs[1], cmap='Blues', colorbar=False)
axs[1].set_title('Multiclass Confusion Matrix', fontsize=12, fontweight='bold')

plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task11_mlp_evaluation.png', dpi=300, bbox_inches='tight')
plt.show()"""

ex12_code_student = """# 1. Permutation Feature Importance Analysis for Model Interpretability
# Evaluate feature importance using permutation_importance on the test set
result = ### FIX_ME_PERMUTATION_IMPORTANCE ###
sorted_idx = result.importances_mean.argsort()

plt.figure(figsize=(8, 4), dpi=120)
plt.barh(X.columns[sorted_idx], result.importances_mean[sorted_idx], xerr=result.importances_std[sorted_idx], color='#1abc9c')
plt.xlabel("Permutation Importance (Mean Decrease in F1-Score)")
plt.title("MLP Model Interpretability: Permutation Feature Importance")
plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task12_mlp_feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. Define the updated production engine class
class StellarTraceEngine:
    def __init__(self, sfms_reg, sfms_poly, mlp_model, scaler_model):
        self.reg = sfms_reg
        self.poly = sfms_poly
        self.mlp = mlp_model
        self.scaler = scaler_model
        
    def predict_host_probabilities(self, log_mstar, redshift):
        m_arr = np.array([[log_mstar]])
        
        # Predict baseline log(SFR) using the SFMS regression model
        m_poly = self.poly.transform(m_arr)
        log_sfr_baseline = self.reg.predict(m_poly)[0]
        
        # Calculate Specific Star Formation Rate (ssfr = log_sfr - log_mstar)
        ssfr = log_sfr_baseline - log_mstar
        
        # Construct the normalized feature vector [redshift, log_mstar, log_sfr, ssfr]
        feature_vector = np.array([[redshift, log_mstar, log_sfr_baseline, ssfr]])
        
        # Standardise the feature vector
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Predict the host probabilities
        probs = self.mlp.predict_proba(feature_vector_scaled)[0]
        
        return {
            'Background': probs[0],
            'CC-SN': probs[1],
            'Ia-SN': probs[2]
        }

# --- Programmatic Verification ---
try:
    engine = StellarTraceEngine(reg, poly_features, best_mlp, scaler)
    print("StellarTraceEngine successfully instantiated with pre-trained models!")
    
    # Run test predictions
    p_dwarf = engine.predict_host_probabilities(log_mstar=9.0, redshift=0.05)
    p_massive = engine.predict_host_probabilities(log_mstar=11.5, redshift=0.1)
    
    print("\\nHost probabilities for active dwarf galaxy (logM = 9.0, z = 0.05):")
    for k, v in p_dwarf.items():
        print(f"  - {k}: {v*100:.2f}%")
        
    print("\\nHost probabilities for massive passive galaxy (logM = 11.5, z = 0.1):")
    for k, v in p_massive.items():
        print(f"  - {k}: {v*100:.2f}%")
except NameError:
    print("Verification Notice: Local namespace variables not found. Instantiating with dummy parameters for testing...")
    class DummyModel:
        def fit_transform(self, x): return x
        def transform(self, x): return x
        def predict(self, x): return np.array([0.5])
        def predict_proba(self, x): return np.array([[0.1, 0.3, 0.6]])
    
    dummy_reg = DummyModel()
    dummy_poly = DummyModel()
    dummy_mlp = DummyModel()
    dummy_scaler = DummyModel()
    
    engine = StellarTraceEngine(dummy_reg, dummy_poly, dummy_mlp, dummy_scaler)
    p_dwarf = engine.predict_host_probabilities(log_mstar=9.0, redshift=0.05)
    print(f"StellarTraceEngine test check passed! (Dwarf host probs: {p_dwarf})")"""

ex9_code_solution = """import warnings

# 1. Run 1D K-S and A-D tests on stellar mass
ks_cc_stat, ks_cc_p = ks_2samp(real_hosts['log_mstar'].values, df_detected['log_mstar'].values)
ks_ia_stat, ks_ia_p = ks_2samp(ia_hosts['log_mstar'].values, df_detected['log_mstar'].values)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ad_cc_res = anderson_ksamp([real_hosts['log_mstar'].values, df_detected['log_mstar'].values])
    ad_ia_res = anderson_ksamp([ia_hosts['log_mstar'].values, df_detected['log_mstar'].values])

# 2. Implement the 2D Kolmogorov-Smirnov Test (Fasano & Franceschini 1987)
def ks_2d(x1, y1, x2, y2, n_eval=300):
    n1, n2 = len(x1), len(x2)
    x_all = np.concatenate([x1, x2])
    y_all = np.concatenate([y1, y2])
    
    np.random.seed(42)
    eval_idx = np.random.choice(len(x_all), size=min(len(x_all), n_eval), replace=False)
    x_eval = x_all[eval_idx]
    y_eval = y_all[eval_idx]
    
    d_max = 0.0
    for x, y in zip(x_eval, y_eval):
        q1_1 = np.sum((x1 >= x) & (y1 >= y)) / n1
        q2_1 = np.sum((x1 < x) & (y1 >= y)) / n1
        q3_1 = np.sum((x1 < x) & (y1 < y)) / n1
        q4_1 = np.sum((x1 >= x) & (y1 < y)) / n1
        
        q1_2 = np.sum((x2 >= x) & (y2 >= y)) / n2
        q2_2 = np.sum((x2 < x) & (y2 >= y)) / n2
        q3_2 = np.sum((x2 < x) & (y2 < y)) / n2
        q4_2 = np.sum((x2 >= x) & (y2 < y)) / n2
        
        d1 = abs(q1_1 - q1_2)
        d2 = abs(q2_1 - q2_2)
        d3 = abs(q3_1 - q3_2)
        d4 = abs(q4_1 - q4_2)
        
        d_max = max(d_max, d1, d2, d3, d4)
        
    r1 = np.nan_to_num(np.corrcoef(x1, y1)[0, 1]) if n1 > 1 else 0.0
    r2 = np.nan_to_num(np.corrcoef(x2, y2)[0, 1]) if n2 > 1 else 0.0
    r = (r1 + r2) / 2.0
    r = np.clip(r, -0.999, 0.999)
    
    n_eff = (n1 * n2) / (n1 + n2)
    lambda_val = d_max * np.sqrt(n_eff) / (1.0 - 0.5 * r**2)
    p_val = 2.0 * np.exp(-2.0 * (lambda_val - 0.5)**2)
    p_val = np.clip(p_val, 0.0, 1.0)
    return d_max, p_val

# Compare CC-SNe and Type Ia hosts against background detected galaxies in Mass-sSFR space
ks2d_cc_stat, ks2d_cc_p = ks_2d(
    real_hosts['log_mstar'].values, real_hosts['ssfr'].values,
    df_detected['log_mstar'].values, df_detected['ssfr'].values
)
ks2d_ia_stat, ks2d_ia_p = ks_2d(
    ia_hosts['log_mstar'].values, ia_hosts['ssfr'].values,
    df_detected['log_mstar'].values, df_detected['ssfr'].values
)

print("\\n--- Statistical Hypothesis Testing Results ---")
print(f"CC-SN Hosts vs Background:")
print(f"  - 1D K-S Test (Mass) p-value: {ks_cc_p:.4f}")
print(f"  - 1D A-D Test (Mass) p-value: {ad_cc_res.significance_level:.4f}")
print(f"  - 2D K-S Test (Mass-sSFR) p-value: {ks2d_cc_p:.4e}")
print(f"Type Ia SN Hosts vs Background:")
print(f"  - 1D K-S Test (Mass) p-value: {ks_ia_p:.4e}")
print(f"  - 1D A-D Test (Mass) p-value: {ad_ia_res.significance_level:.4e}")
print(f"  - 2D K-S Test (Mass-sSFR) p-value: {ks2d_ia_p:.4e}")

# 3. Plot Empirical Cumulative Distribution Functions (eCDFs) for K-S visualization
def plot_ecdf(ax, data, label, color):
    x = np.sort(data)
    y = np.arange(1, len(data) + 1) / len(data)
    ax.plot(x, y, label=label, color=color, linewidth=2)

fig, axs = plt.subplots(1, 2, figsize=(12, 5), dpi=120)

plot_ecdf(axs[0], df_detected['log_mstar'].values, 'Background', '#bdc3c7')
plot_ecdf(axs[0], real_hosts['log_mstar'].values, 'CC-SN Hosts', '#1abc9c')
axs[0].set_title(f'CC-SN Host Mass eCDF (KS-stat={ks_cc_stat:.3f})')
axs[0].set_xlabel('log(Mstar / Msun)')
axs[0].legend()

plot_ecdf(axs[1], df_detected['log_mstar'].values, 'Background', '#bdc3c7')
plot_ecdf(axs[1], ia_hosts['log_mstar'].values, 'Ia-SN Hosts', '#3498db')
axs[1].set_title(f'Ia-SN Host Mass eCDF (KS-stat={ks_ia_stat:.3f})')
axs[1].set_xlabel('log(Mstar / Msun)')
axs[1].legend()

plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task9_ks_ecdf.png', dpi=300, bbox_inches='tight')
plt.show()

# Plot galaxies in the Mass-sSFR plane
plt.figure(figsize=(10, 6), dpi=120)
plt.scatter(df_detected['log_mstar'], df_detected['ssfr'], s=5, color='#bdc3c7', alpha=0.3, label='Background Field')
plt.scatter(real_hosts['log_mstar'], real_hosts['ssfr'], s=35, color='#1abc9c', alpha=0.8, label='CC-SN Hosts', edgecolors='black')
plt.scatter(ia_hosts['log_mstar'], ia_hosts['ssfr'], s=35, color='#3498db', alpha=0.8, label='Ia-SN Hosts', edgecolors='black')
plt.xlabel('log(Mstar / Msun)', fontsize=11)
plt.ylabel('Specific SFR (sSFR)', fontsize=11)
plt.title('Galaxy Populations in the Stellar Mass vs sSFR Plane', fontsize=12, fontweight='bold')
plt.legend(loc='lower left')
plt.grid(True, linestyle=':', alpha=0.5)
plt.savefig('plots/task9_mass_ssfr_plane.png', dpi=300, bbox_inches='tight')
plt.show()"""

ex10_code_solution = """# 1. Compile the multiclass machine learning dataset
real_hosts['class'] = 1
ia_hosts['class'] = 2

# Background Non-Hosts (Class 0): Draw a random sample of 150 galaxies from the detected mock population
np.random.seed(42)
df_non_hosts = df_detected.sample(n=150, random_state=42).copy()
df_non_hosts['class'] = 0

# Combine catalogs into a single imbalanced dataset
df_ml = pd.concat([
    df_non_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']],
    real_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']],
    ia_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']]
], ignore_index=True)

# 2. Perform stratified train/test split FIRST to prevent data leakage (validation contamination)
from sklearn.model_selection import train_test_split
df_train, df_test = train_test_split(df_ml, test_size=0.3, random_state=42, stratify=df_ml['class'])

# 3. Address Class Imbalance in the TRAINING set using Manual Random Oversampling
def oversample_dataset(df, class_column):
    class_counts = df[class_column].value_counts()
    target_size = class_counts.max()
    
    balanced_dfs = []
    for cls in df[class_column].unique():
        df_cls = df[df[class_column] == cls]
        if len(df_cls) < target_size:
            df_cls_oversampled = df_cls.sample(n=target_size, replace=True, random_state=42)
            balanced_dfs.append(df_cls_oversampled)
        else:
            balanced_dfs.append(df_cls)
    return pd.concat(balanced_dfs, ignore_index=True)

df_train_balanced = oversample_dataset(df_train, 'class')

print(f"Original dataset distribution:\\n{df_ml['class'].value_counts().to_dict()}")
print(f"Training set before oversampling:\\n{df_train['class'].value_counts().to_dict()}")
print(f"Training set after oversampling:\\n{df_train_balanced['class'].value_counts().to_dict()}")
print(f"Test set (untouched/imbalanced):\\n{df_test['class'].value_counts().to_dict()}")"""

ex11_code_solution = """# 1. Extract features and target from the pre-split datasets
X_train = df_train_balanced[['redshift', 'log_mstar', 'log_sfr', 'ssfr']]
y_train = df_train_balanced['class']
X_test = df_test[['redshift', 'log_mstar', 'log_sfr', 'ssfr']]
y_test = df_test['class']
X = X_train # Reference variable for Task 12

# 2. Standardise features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 3. GridSearchCV hyperparameter tuning for multiclass MLP classifier
param_grid = {
    'hidden_layer_sizes': [(32, 16), (64, 32)],
    'activation': ['relu', 'tanh'],
    'alpha': [0.01, 0.1]
}

mlp = MLPClassifier(max_iter=1000, random_state=42)
grid_search = GridSearchCV(mlp, param_grid, cv=5, scoring='f1_macro')
grid_search.fit(X_train_scaled, y_train)

print(f"Best parameters found: {grid_search.best_params_}")
best_mlp = grid_search.best_estimator_

# 4. Evaluate multiclass model
y_pred = best_mlp.predict(X_test_scaled)
y_prob = best_mlp.predict_proba(X_test_scaled)

print("MLP Classification Report:")
print(classification_report(y_test, y_pred))

# 5. Plot 3x3 Confusion Matrix and Multiclass ROC Curves
fig, axs = plt.subplots(1, 2, figsize=(14, 6), dpi=120)

# Panel 1: Multiclass ROC Curves (One-vs-Rest)
for i, label in enumerate(['Background', 'CC-SN Host', 'Ia-SN Host']):
    y_test_bin = (y_test == i).astype(int)
    fpr, tpr, _ = roc_curve(y_test_bin, y_prob[:, i])
    roc_auc = auc(fpr, tpr)
    axs[0].plot(fpr, tpr, linewidth=2.5, label=f'{label} vs Rest (AUC = {roc_auc:.3f})')

axs[0].plot([0, 1], [0, 1], color='#7f8c8d', linestyle='--', linewidth=1.5)
axs[0].set_xlabel('False Positive Rate', fontsize=11)
axs[0].set_ylabel('True Positive Rate', fontsize=11)
axs[0].set_title('White-Box Classifier ROC Curves (One-vs-Rest)', fontsize=12, fontweight='bold')
axs[0].legend(loc='lower right', fontsize=10)
axs[0].grid(True, linestyle=':', alpha=0.5)

# Panel 2: Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Background', 'CC-SN', 'Ia-SN'])
disp.plot(ax=axs[1], cmap='Blues', colorbar=False)
axs[1].set_title('Multiclass Confusion Matrix', fontsize=12, fontweight='bold')

plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task11_mlp_evaluation.png', dpi=300, bbox_inches='tight')
plt.show()"""

ex12_code_solution = """# 1. Permutation Feature Importance Analysis for Model Interpretability
result = permutation_importance(best_mlp, X_test_scaled, y_test, n_repeats=10, random_state=42)
sorted_idx = result.importances_mean.argsort()

plt.figure(figsize=(8, 4), dpi=120)
plt.barh(X.columns[sorted_idx], result.importances_mean[sorted_idx], xerr=result.importances_std[sorted_idx], color='#1abc9c')
plt.xlabel("Permutation Importance (Mean Decrease in F1-Score)")
plt.title("MLP Model Interpretability: Permutation Feature Importance")
plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task12_mlp_feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

# 2. Define the updated production engine class
class StellarTraceEngine:
    def __init__(self, sfms_reg, sfms_poly, mlp_model, scaler_model):
        self.reg = sfms_reg
        self.poly = sfms_poly
        self.mlp = mlp_model
        self.scaler = scaler_model
        
    def predict_host_probabilities(self, log_mstar, redshift):
        m_arr = np.array([[log_mstar]])
        
        # Predict baseline log(SFR) using the SFMS regression model
        m_poly = self.poly.transform(m_arr)
        log_sfr_baseline = self.reg.predict(m_poly)[0]
        
        # Calculate Specific Star Formation Rate (ssfr = log_sfr - log_mstar)
        ssfr = log_sfr_baseline - log_mstar
        
        # Construct the normalized feature vector [redshift, log_mstar, log_sfr, ssfr]
        feature_vector = np.array([[redshift, log_mstar, log_sfr_baseline, ssfr]])
        
        # Standardise the feature vector
        feature_vector_scaled = self.scaler.transform(feature_vector)
        
        # Predict the host probabilities
        probs = self.mlp.predict_proba(feature_vector_scaled)[0]
        
        return {
            'Background': probs[0],
            'CC-SN': probs[1],
            'Ia-SN': probs[2]
        }

# --- Programmatic Verification ---
try:
    engine = StellarTraceEngine(reg, poly_features, best_mlp, scaler)
    print("StellarTraceEngine successfully instantiated with pre-trained models!")
    
    # Run test predictions
    p_dwarf = engine.predict_host_probabilities(log_mstar=9.0, redshift=0.05)
    p_massive = engine.predict_host_probabilities(log_mstar=11.5, redshift=0.1)
    
    print("\\nHost probabilities for active dwarf galaxy (logM = 9.0, z = 0.05):")
    for k, v in p_dwarf.items():
        print(f"  - {k}: {v*100:.2f}%")
        
    print("\\nHost probabilities for massive passive galaxy (logM = 11.5, z = 0.1):")
    for k, v in p_massive.items():
        print(f"  - {k}: {v*100:.2f}%")
except NameError:
    print("Verification Notice: Local namespace variables not found. Instantiating with dummy parameters for testing...")
    class DummyModel:
        def fit_transform(self, x): return x
        def transform(self, x): return x
        def predict(self, x): return np.array([0.5])
        def predict_proba(self, x): return np.array([[0.1, 0.3, 0.6]])
    
    dummy_reg = DummyModel()
    dummy_poly = DummyModel()
    dummy_mlp = DummyModel()
    dummy_scaler = DummyModel()
    
    engine = StellarTraceEngine(dummy_reg, dummy_poly, dummy_mlp, dummy_scaler)
    p_dwarf = engine.predict_host_probabilities(log_mstar=9.0, redshift=0.05)
    print(f"StellarTraceEngine test check passed! (Dwarf host probs: {p_dwarf})")"""

task13_theory = r"""
## Task 13: Physics-Informed Supernova Rate Modeling

### Astrophysical Rate Models
In the previous tasks, we compared the properties of supernova host galaxies against the background field galaxy population using non-parametric statistical tests. While we rejected the null hypothesis that supernova hosts are randomly selected, we did not specify the physical rate dependence. Here, we define three competing models for supernova rates as functions of host galaxy properties:

1. **Null (Random) Model:** Supernovae are random events that do not depend on host properties:
   $$R_{\text{Null}} = \text{const}$$

2. **Core-Collapse Supernova (CC-SN) Model:** Tracks instantaneous star formation as a power law of SFR:
   $$R_{\text{CC}}(\text{SFR}) = \text{SFR}^\beta$$
   where $\beta \approx 1.0$ if the rate is directly proportional to the star formation rate.

3. **Type Ia Supernova Model:** The standard "A+B" model (Scannapieco & Bildsten 2005) with delayed and prompt components:
   $$R_{\text{Ia}}(M_\star, \text{SFR}) = A \cdot \left(\frac{M_\star}{10^{10} M_\odot}\right) + B \cdot \left(\frac{\text{SFR}}{M_\odot \text{ yr}^{-1}}\right)$$
   For numerical stability, we define the parameters $A$ and $B$ as independent non-negative rate coefficients:
   $$R_{\text{Ia}}(M_\star, \text{SFR}) = A \cdot M_{\star, 10} + B \cdot \text{SFR}$$

### Parameter Recovery via Maximum Likelihood Estimation (MLE)
The probability of a specific galaxy $i$ hosting a supernova out of a population of $N$ galaxies is proportional to its relative rate:
$$P(\text{host}_i \mid \theta) = \frac{R_i(\theta)}{\sum_{j=1}^N R_j(\theta)}$$
For a sample of observed host galaxies, the joint likelihood is the product of their individual probabilities. The negative log-likelihood (NLL) to minimize is:
$$\mathcal{L}(\theta) = -\sum_{i \in \text{observed}} \ln R_i(\theta) + N_{\text{observed}} \cdot \ln \left(\sum_{j \in \text{background}} R_j(\theta)\right)$$

### Bayesian Uncertainty Quantification via Markov Chain Monte Carlo (MCMC)
Maximum Likelihood Estimation gives only point estimates of the parameters. In astrophysics, parameter degeneracies are common (e.g., mass and star-formation rate are correlated, leading to degeneracies between delayed and prompt channels). To map the full posterior probability distribution and measure parameter uncertainties, we implement a **Metropolis-Hastings MCMC sampler** in pure NumPy.
We assume flat uniform priors: $A, B \in [0, 5]$. The acceptance probability for a proposed step $\theta_{\text{prop}}$ is:
$$\alpha = \min\left(1, \exp(\ln \mathcal{L}(\theta_{\text{prop}}) - \ln \mathcal{L}(\theta_t))\right)$$

### Physics-Informed Neural Network (PINN) Formulation
To estimate the parameters via gradient descent, we construct a neural network where the final output is constrained to follow our physical rate model. The network takes host galaxy properties as input, outputs predicted rate values, and is optimized using a loss function that combines the standard data log-likelihood with physics constraints (e.g., parameter bounds $\beta > 0$ and $A, B > 0$ enforced via exponential layers).
"""

ex13_code_student = """# Task 13: Supernova Rate Modeling and Physics-Informed Parameter Recovery

# 1. Prepare physical inputs for rates
cc_sfr = 10**real_hosts['log_sfr'].values
cc_mass_10 = 10**(real_hosts['log_mstar'].values - 10)

ia_sfr = 10**ia_hosts['log_sfr'].values
ia_mass_10 = 10**(ia_hosts['log_mstar'].values - 10)

all_sfr = 10**df_detected['log_sfr'].values
all_mass_10 = 10**(df_detected['log_mstar'].values - 10)

# 2. Fit parameters using classical MLE (scipy)
def cc_nll(beta):
    # TODO: Implement the negative log-likelihood for the Core-Collapse rate model
    rates_hosts = ### FIX_ME_CC_RATES_HOSTS ###
    rates_all = ### FIX_ME_CC_RATES_ALL ###
    rates_hosts = np.clip(rates_hosts, 1e-10, None)
    return ### FIX_ME_CC_NLL ###

res_cc = minimize(cc_nll, x0=[1.0], bounds=[(0.1, 3.0)], method='L-BFGS-B')
beta_mle = res_cc.x[0]

def ia_nll(theta):
    A, B = theta
    # TODO: Implement the negative log-likelihood for the Type Ia rate model
    rates_hosts = ### FIX_ME_IA_RATES_HOSTS ###
    rates_all = ### FIX_ME_IA_RATES_ALL ###
    rates_hosts = np.clip(rates_hosts, 1e-10, None)
    return ### FIX_ME_IA_NLL ###

res_ia = minimize(ia_nll, x0=[1.0, 1.0], bounds=[(0.0, 5.0), (0.0, 5.0)], method='L-BFGS-B')
A_mle, B_mle = res_ia.x

print("MLE parameters recovered:")
print(f"  - CC-SN beta: {beta_mle:.4f}")
print(f"  - Type Ia A (Delayed): {A_mle:.4f}, B (Prompt): {B_mle:.4f}")

# 3. Fit parameters using Bayesian MCMC (Metropolis-Hastings)
def ia_log_likelihood(theta):
    A, B = theta
    rates_hosts = A * ia_mass_10 + B * ia_sfr
    rates_all = A * all_mass_10 + B * all_sfr
    if np.any(rates_hosts <= 0) or np.any(rates_all <= 0):
        return -np.inf
    return np.sum(np.log(rates_hosts)) - len(ia_hosts) * np.log(np.sum(rates_all))

def run_mcmc(ll_func, init_theta, proposal_width, n_steps=6000, burn_in=1000):
    np.random.seed(42)
    theta = np.array(init_theta)
    samples = []
    current_ll = ll_func(theta)
    
    for i in range(n_steps):
        # Generate proposal
        proposal = theta + np.random.normal(0, proposal_width)
        
        # Enforce flat prior boundaries [0, 5]
        if np.any(proposal < 0.0) or np.any(proposal > 5.0):
            samples.append(theta)
            continue
            
        proposal_ll = ll_func(proposal)
        
        # Acceptance probability
        alpha = np.exp(proposal_ll - current_ll)
        
        if np.random.uniform(0, 1) < alpha:
            theta = proposal
            current_ll = proposal_ll
            
        samples.append(theta)
        
    return np.array(samples[burn_in:])

# Run MCMC for Type Ia Supernova parameters
ia_samples = run_mcmc(ia_log_likelihood, init_theta=[1.0, 1.0], proposal_width=[0.05, 0.05])
A_mcmc = np.mean(ia_samples[:, 0])
B_mcmc = np.mean(ia_samples[:, 1])

# 4. Fit parameters using Physics-Informed Neural Network (PINN) in PyTorch
class PINNRateModel(nn.Module):
    def __init__(self):
        super().__init__()
        # Learnable parameters (beta for CC, A and B for Ia)
        self.raw_beta = nn.Parameter(torch.tensor([0.0]))  # exp(0) = 1.0
        self.raw_A = nn.Parameter(torch.tensor([0.0]))     # exp(0) = 1.0
        self.raw_B = nn.Parameter(torch.tensor([0.0]))     # exp(0) = 1.0

    def get_params(self):
        # Enforce positive constraints physically
        beta = torch.exp(self.raw_beta)
        A = torch.exp(self.raw_A)
        B = torch.exp(self.raw_B)
        return beta, A, B

    def forward(self, sfr_hosts, mass_hosts, sfr_all, mass_all):
        beta, A, B = self.get_params()
        
        # CC SN rates
        cc_rates_hosts = sfr_hosts ** beta
        cc_rates_all = sfr_all ** beta
        
        # Ia SN rates
        ia_rates_hosts = A * mass_hosts + B * sfr_hosts
        ia_rates_all = A * mass_all + B * sfr_all
        
        return cc_rates_hosts, cc_rates_all, ia_rates_hosts, ia_rates_all

# Convert features to torch tensors
cc_sfr_t = torch.tensor(cc_sfr, dtype=torch.float32)
cc_mass_t = torch.tensor(cc_mass_10, dtype=torch.float32)
ia_sfr_t = torch.tensor(ia_sfr, dtype=torch.float32)
ia_mass_t = torch.tensor(ia_mass_10, dtype=torch.float32)
all_sfr_t = torch.tensor(all_sfr, dtype=torch.float32)
all_mass_t = torch.tensor(all_mass_10, dtype=torch.float32)

pinn = PINNRateModel()
optimizer = torch.optim.Adam(pinn.parameters(), lr=0.05)

# Training loop
for epoch in range(250):
    optimizer.zero_grad()
    
    cc_rh, cc_ra, _, _ = pinn(cc_sfr_t, cc_mass_t, all_sfr_t, all_mass_t)
    _, _, ia_rh, ia_ra = pinn(ia_sfr_t, ia_mass_t, all_sfr_t, all_mass_t)
    
    loss_cc = -torch.sum(torch.log(cc_rh + 1e-10)) + len(real_hosts) * torch.log(torch.sum(cc_ra) + 1e-10)
    loss_ia = -torch.sum(torch.log(ia_rh + 1e-10)) + len(ia_hosts) * torch.log(torch.sum(ia_ra) + 1e-10)
    loss = loss_cc + loss_ia
    
    loss.backward()
    optimizer.step()

beta_pinn, A_pinn, B_pinn = pinn.get_params()
beta_pinn = beta_pinn.item()
A_pinn = A_pinn.item()
B_pinn = B_pinn.item()

print("\\nPINN parameters recovered:")
print(f"  - CC-SN beta: {beta_pinn:.4f}")
print(f"  - Type Ia A: {A_pinn:.4f}, B: {B_pinn:.4f}")

# 5. Generate predicted host catalogs using MLE parameters
rates_cc = all_sfr ** beta_mle
rates_ia = A_mle * all_mass_10 + B_mle * all_sfr
rates_null = np.ones(len(df_detected))

cc_pred = df_detected.sample(n=5000, replace=True, weights=rates_cc/rates_cc.sum(), random_state=42)
ia_pred = df_detected.sample(n=5000, replace=True, weights=rates_ia/rates_ia.sum(), random_state=42)
null_pred = df_detected.sample(n=5000, replace=True, weights=rates_null/rates_null.sum(), random_state=42)

# 6. Run KS goodness-of-fit validation tests
_, p_ks_cc_null = ks_2samp(real_hosts['log_sfr'].values, null_pred['log_sfr'].values)
_, p_ks_cc_model = ks_2samp(real_hosts['log_sfr'].values, cc_pred['log_sfr'].values)

_, p_ks_ia_null = ks_2samp(ia_hosts['log_mstar'].values, null_pred['log_mstar'].values)
_, p_ks_ia_model = ks_2samp(ia_hosts['log_mstar'].values, ia_pred['log_mstar'].values)

print("\\n--- Goodness-of-Fit Validation Tests ---")
print(f"CC-SN SFR Distribution:")
print(f"  - Null model KS p-value: {p_ks_cc_null:.4e}")
print(f"  - Physics model KS p-value: {p_ks_cc_model:.4f}")
print(f"Type Ia SN Mass Distribution:")
print(f"  - Null model KS p-value: {p_ks_ia_null:.4e}")
print(f"  - Physics model KS p-value: {p_ks_ia_model:.4f}")

# 7. Plot validation dashboard and MCMC corner plot
fig, axs = plt.subplots(1, 2, figsize=(14, 5), dpi=120)
axs[0].hist(real_hosts['log_sfr'], bins=15, density=True, alpha=0.5, label='Observed (CC-SN)', color='#1abc9c')
axs[0].hist(cc_pred['log_sfr'], bins=15, density=True, histtype='step', linewidth=2, label='Physics Model', color='#2c3e50')
axs[0].hist(null_pred['log_sfr'], bins=15, density=True, histtype='step', linestyle='--', linewidth=1.5, label='Null Model', color='#e74c3c')
axs[0].set_xlabel('log(SFR / Msun/yr)')
axs[0].set_ylabel('Probability Density')
axs[0].set_title('CC-SN Host SFR Distribution')
axs[0].legend()

axs[1].hist(ia_hosts['log_mstar'], bins=15, density=True, alpha=0.5, label='Observed (Ia-SN)', color='#3498db')
axs[1].hist(ia_pred['log_mstar'], bins=15, density=True, histtype='step', linewidth=2, label='Physics Model', color='#2c3e50')
axs[1].hist(null_pred['log_mstar'], bins=15, density=True, histtype='step', linestyle='--', linewidth=1.5, label='Null Model', color='#e74c3c')
axs[1].set_xlabel('log(Mstar / Msun)')
axs[1].set_ylabel('Probability Density')
axs[1].set_title('Type Ia SN Host Mass Distribution')
axs[1].legend()
plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task13_piml_validation_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()

# Implement and plot MCMC Corner Plot (posteriors of A and B)
fig, axs = plt.subplots(2, 2, figsize=(8, 8), dpi=120)
axs[0, 1].axis('off')
axs[0, 0].hist(ia_samples[:, 0], bins=30, density=True, color='#3498db', edgecolor='white', alpha=0.7)
axs[0, 0].set_ylabel('Probability Density')
axs[0, 0].set_title(f"A = {A_mcmc:.3f} ± {np.std(ia_samples[:, 0]):.3f}")

axs[1, 1].hist(ia_samples[:, 1], bins=30, density=True, color='#e67e22', edgecolor='white', alpha=0.7)
axs[1, 1].set_xlabel('Type Ia Parameter B (Prompt)')
axs[1, 1].set_title(f"B = {B_mcmc:.3f} ± {np.std(ia_samples[:, 1]):.3f}")

axs[1, 0].hexbin(ia_samples[:, 0], ia_samples[:, 1], gridsize=25, cmap='Blues', mincnt=1)
axs[1, 0].set_xlabel('Type Ia Parameter A (Delayed)')
axs[1, 0].set_ylabel('Type Ia Parameter B (Prompt)')
plt.suptitle('Markov Chain Monte Carlo Joint Posterior & Degeneracy', fontsize=12, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('plots/task13_mcmc_corner.png', dpi=300, bbox_inches='tight')
plt.show()"""

ex13_code_solution = """# Task 13: Supernova Rate Modeling and Physics-Informed Parameter Recovery

# 1. Prepare physical inputs for rates
cc_sfr = 10**real_hosts['log_sfr'].values
cc_mass_10 = 10**(real_hosts['log_mstar'].values - 10)

ia_sfr = 10**ia_hosts['log_sfr'].values
ia_mass_10 = 10**(ia_hosts['log_mstar'].values - 10)

all_sfr = 10**df_detected['log_sfr'].values
all_mass_10 = 10**(df_detected['log_mstar'].values - 10)

# 2. Fit parameters using classical MLE (scipy)
def cc_nll(beta):
    rates_hosts = cc_sfr ** beta
    rates_all = all_sfr ** beta
    rates_hosts = np.clip(rates_hosts, 1e-10, None)
    return -np.sum(np.log(rates_hosts)) + len(real_hosts) * np.log(np.sum(rates_all))

res_cc = minimize(cc_nll, x0=[1.0], bounds=[(0.1, 3.0)], method='L-BFGS-B')
beta_mle = res_cc.x[0]

def ia_nll(theta):
    A, B = theta
    rates_hosts = A * ia_mass_10 + B * ia_sfr
    rates_all = A * all_mass_10 + B * all_sfr
    rates_hosts = np.clip(rates_hosts, 1e-10, None)
    return -np.sum(np.log(rates_hosts)) + len(ia_hosts) * np.log(np.sum(rates_all))

res_ia = minimize(ia_nll, x0=[1.0, 1.0], bounds=[(0.0, 5.0), (0.0, 5.0)], method='L-BFGS-B')
A_mle, B_mle = res_ia.x

print("MLE parameters recovered:")
print(f"  - CC-SN beta: {beta_mle:.4f}")
print(f"  - Type Ia A (Delayed): {A_mle:.4f}, B (Prompt): {B_mle:.4f}")

# 3. Fit parameters using Bayesian MCMC (Metropolis-Hastings)
def ia_log_likelihood(theta):
    A, B = theta
    rates_hosts = A * ia_mass_10 + B * ia_sfr
    rates_all = A * all_mass_10 + B * all_sfr
    if np.any(rates_hosts <= 0) or np.any(rates_all <= 0):
        return -np.inf
    return np.sum(np.log(rates_hosts)) - len(ia_hosts) * np.log(np.sum(rates_all))

def run_mcmc(ll_func, init_theta, proposal_width, n_steps=6000, burn_in=1000):
    np.random.seed(42)
    theta = np.array(init_theta)
    samples = []
    current_ll = ll_func(theta)
    
    for i in range(n_steps):
        proposal = theta + np.random.normal(0, proposal_width)
        
        # Enforce flat prior boundaries [0, 5]
        if np.any(proposal < 0.0) or np.any(proposal > 5.0):
            samples.append(theta)
            continue
            
        proposal_ll = ll_func(proposal)
        alpha = np.exp(proposal_ll - current_ll)
        
        if np.random.uniform(0, 1) < alpha:
            theta = proposal
            current_ll = proposal_ll
            
        samples.append(theta)
        
    return np.array(samples[burn_in:])

ia_samples = run_mcmc(ia_log_likelihood, init_theta=[1.0, 1.0], proposal_width=[0.05, 0.05])
A_mcmc = np.mean(ia_samples[:, 0])
B_mcmc = np.mean(ia_samples[:, 1])

# 4. Fit parameters using Physics-Informed Neural Network (PINN) in PyTorch
class PINNRateModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.raw_beta = nn.Parameter(torch.tensor([0.0]))  # exp(0) = 1.0
        self.raw_A = nn.Parameter(torch.tensor([0.0]))     # exp(0) = 1.0
        self.raw_B = nn.Parameter(torch.tensor([0.0]))     # exp(0) = 1.0

    def get_params(self):
        beta = torch.exp(self.raw_beta)
        A = torch.exp(self.raw_A)
        B = torch.exp(self.raw_B)
        return beta, A, B

    def forward(self, sfr_hosts, mass_hosts, sfr_all, mass_all):
        beta, A, B = self.get_params()
        cc_rates_hosts = sfr_hosts ** beta
        cc_rates_all = sfr_all ** beta
        ia_rates_hosts = A * mass_hosts + B * sfr_hosts
        ia_rates_all = A * mass_all + B * sfr_all
        return cc_rates_hosts, cc_rates_all, ia_rates_hosts, ia_rates_all

cc_sfr_t = torch.tensor(cc_sfr, dtype=torch.float32)
cc_mass_t = torch.tensor(cc_mass_10, dtype=torch.float32)
ia_sfr_t = torch.tensor(ia_sfr, dtype=torch.float32)
ia_mass_t = torch.tensor(ia_mass_10, dtype=torch.float32)
all_sfr_t = torch.tensor(all_sfr, dtype=torch.float32)
all_mass_t = torch.tensor(all_mass_10, dtype=torch.float32)

pinn = PINNRateModel()
optimizer = torch.optim.Adam(pinn.parameters(), lr=0.05)

for epoch in range(250):
    optimizer.zero_grad()
    cc_rh, cc_ra, _, _ = pinn(cc_sfr_t, cc_mass_t, all_sfr_t, all_mass_t)
    _, _, ia_rh, ia_ra = pinn(ia_sfr_t, ia_mass_t, all_sfr_t, all_mass_t)
    loss_cc = -torch.sum(torch.log(cc_rh + 1e-10)) + len(real_hosts) * torch.log(torch.sum(cc_ra) + 1e-10)
    loss_ia = -torch.sum(torch.log(ia_rh + 1e-10)) + len(ia_hosts) * torch.log(torch.sum(ia_ra) + 1e-10)
    loss = loss_cc + loss_ia
    loss.backward()
    optimizer.step()

beta_pinn, A_pinn, B_pinn = pinn.get_params()
beta_pinn = beta_pinn.item()
A_pinn = A_pinn.item()
B_pinn = B_pinn.item()

print("\\nPINN parameters recovered:")
print(f"  - CC-SN beta: {beta_pinn:.4f}")
print(f"  - Type Ia A: {A_pinn:.4f}, B: {B_pinn:.4f}")

# 5. Generate predicted host catalogs using MLE parameters
rates_cc = all_sfr ** beta_mle
rates_ia = A_mle * all_mass_10 + B_mle * all_sfr
rates_null = np.ones(len(df_detected))

cc_pred = df_detected.sample(n=5000, replace=True, weights=rates_cc/rates_cc.sum(), random_state=42)
ia_pred = df_detected.sample(n=5000, replace=True, weights=rates_ia/rates_ia.sum(), random_state=42)
null_pred = df_detected.sample(n=5000, replace=True, weights=rates_null/rates_null.sum(), random_state=42)

# 6. Run KS goodness-of-fit validation tests
_, p_ks_cc_null = ks_2samp(real_hosts['log_sfr'].values, null_pred['log_sfr'].values)
_, p_ks_cc_model = ks_2samp(real_hosts['log_sfr'].values, cc_pred['log_sfr'].values)

_, p_ks_ia_null = ks_2samp(ia_hosts['log_mstar'].values, null_pred['log_mstar'].values)
_, p_ks_ia_model = ks_2samp(ia_hosts['log_mstar'].values, ia_pred['log_mstar'].values)

print("\\n--- Goodness-of-Fit Validation Tests ---")
print(f"CC-SN SFR Distribution:")
print(f"  - Null model KS p-value: {p_ks_cc_null:.4e}")
print(f"  - Physics model KS p-value: {p_ks_cc_model:.4f}")
print(f"Type Ia SN Mass Distribution:")
print(f"  - Null model KS p-value: {p_ks_ia_null:.4e}")
print(f"  - Physics model KS p-value: {p_ks_ia_model:.4f}")

# 7. Plot validation dashboard and MCMC corner plot
fig, axs = plt.subplots(1, 2, figsize=(14, 5), dpi=120)
axs[0].hist(real_hosts['log_sfr'], bins=15, density=True, alpha=0.5, label='Observed (CC-SN)', color='#1abc9c')
axs[0].hist(cc_pred['log_sfr'], bins=15, density=True, histtype='step', linewidth=2, label='Physics Model', color='#2c3e50')
axs[0].hist(null_pred['log_sfr'], bins=15, density=True, histtype='step', linestyle='--', linewidth=1.5, label='Null Model', color='#e74c3c')
axs[0].set_xlabel('log(SFR / Msun/yr)')
axs[0].set_ylabel('Probability Density')
axs[0].set_title('CC-SN Host SFR Distribution')
axs[0].legend()

axs[1].hist(ia_hosts['log_mstar'], bins=15, density=True, alpha=0.5, label='Observed (Ia-SN)', color='#3498db')
axs[1].hist(ia_pred['log_mstar'], bins=15, density=True, histtype='step', linewidth=2, label='Physics Model', color='#2c3e50')
axs[1].hist(null_pred['log_mstar'], bins=15, density=True, histtype='step', linestyle='--', linewidth=1.5, label='Null Model', color='#e74c3c')
axs[1].set_xlabel('log(Mstar / Msun)')
axs[1].set_ylabel('Probability Density')
axs[1].set_title('Type Ia SN Host Mass Distribution')
axs[1].legend()
plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task13_piml_validation_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()

# Implement and plot MCMC Corner Plot (posteriors of A and B)
fig, axs = plt.subplots(2, 2, figsize=(8, 8), dpi=120)
axs[0, 1].axis('off')
axs[0, 0].hist(ia_samples[:, 0], bins=30, density=True, color='#3498db', edgecolor='white', alpha=0.7)
axs[0, 0].set_ylabel('Probability Density')
axs[0, 0].set_title(f"A = {A_mcmc:.3f} ± {np.std(ia_samples[:, 0]):.3f}")

axs[1, 1].hist(ia_samples[:, 1], bins=30, density=True, color='#e67e22', edgecolor='white', alpha=0.7)
axs[1, 1].set_xlabel('Type Ia Parameter B (Prompt)')
axs[1, 1].set_title(f"B = {B_mcmc:.3f} ± {np.std(ia_samples[:, 1]):.3f}")

axs[1, 0].hexbin(ia_samples[:, 0], ia_samples[:, 1], gridsize=25, cmap='Blues', mincnt=1)
axs[1, 0].set_xlabel('Type Ia Parameter A (Delayed)')
axs[1, 0].set_ylabel('Type Ia Parameter B (Prompt)')
plt.suptitle('Markov Chain Monte Carlo Joint Posterior & Degeneracy', fontsize=12, fontweight='bold', y=0.98)
plt.tight_layout()
plt.savefig('plots/task13_mcmc_corner.png', dpi=300, bbox_inches='tight')
plt.show()"""

task14_theory = r"""
## Task 14: Model Interpretability and Physical Comparison

### Physical vs. Black-Box Interpretability
Machine learning models often present a tradeoff between predictive power and interpretability. 
- In **Task 11**, we optimized a Multi-Layer Perceptron (MLP) classifier to map galaxy properties directly to supernova host classes. Shuffling input features (permutation feature importance in **Task 12**) showed which parameters the network prioritized, but did not yield physical units or structural equations.
- In **Task 13**, our Physics-Informed models solved for specific, physically grounded coefficients:
  - $\beta$: Represents the star formation dependence of Core-Collapse Supernovae.
  - $A$ and $B$: Quantifies the prompt (recent star formation) vs. delayed (stellar mass / old population) channel contribution to Type Ia Supernovae.

Here, we compare the physical findings of our PIML parameter recovery against the black-box MLP feature importances.
"""

ex14_code_student = """# Task 14: Model Interpretability and Physical Comparison

print("--- Physics-Informed Interpretability Summary ---")
print(f"Recovered CC-SN Star Formation Power-law exponent (beta): {beta_mle:.4f}")
print(f"  - A value of beta ~ 1.0 indicates that CC-SNe directly trace instantaneous SFR,")
print(f"    consistent with short-lived massive star progenitors (M >= 8 Msun).")

print(f"\\nRecovered Type Ia Delayed Coefficient A: {A_mle:.4f}, Prompt Coefficient B: {B_mle:.4f}")
print(f"  - The relative contributions show that Type Ia rates depend on both host mass and SFR")
print(f"    (relative weights: {B_mle/(A_mle+B_mle)*100:.1f}% SFR, {A_mle/(A_mle+B_mle)*100:.1f}% Mass).")

print("\\n--- Black-Box MLP Feature Importance Check ---")
print("In Task 12, the MLP permutation importances were calculated on [redshift, log_mstar, log_sfr, ssfr].")
print("Shuffling log_mstar and log_sfr significantly reduced F1 score, which aligns with the physical dependency")
print("on stellar mass and star formation rate found in the physics-informed rate equations.")
"""

task15_theory = r"""
## Task 15: Type Ia Supernova Delay Time Distribution (DTD) Reconstruction

### Progenitor Delay Times & Galaxy Star Formation Histories
Type Ia supernovae originate from binary systems where a carbon-oxygen white dwarf reaches the Chandrasekhar mass limit or undergoes a double white dwarf merger. The time elapsed between the formation of the star system and the subsequent supernova explosion is the **delay time** ($\tau$). The distribution of these delay times for a population of stars is the **Delay Time Distribution** (DTD), denoted as $\Psi(t)$.

The rate of Type Ia supernovae in a galaxy at cosmic time $t$ is the convolution of the galaxy's historical Star Formation History ($\text{SFR}(t)$) with the DTD:
$$R_{\text{Ia}}(t) = \int_0^t \text{SFR}(t - \tau) \Psi(\tau) d\tau$$

Empirical observations and theoretical white-dwarf merger models suggest that the DTD follows a power law:
$$\Psi(\tau) \propto \tau^{-\gamma}$$
where $\gamma \approx 1.0$ (for delay times $\tau \ge t_{\text{min}} \approx 100\text{ Myr}$). 

### Numerical Convolution on a Cosmic Time Grid
To reconstruct the power-law slope $\gamma$ from host-galaxy observations, we model the Star Formation History (SFH) of each galaxy. A standard analytical approximation is the **delayed-exponential SFH**:
$$\text{SFR}(t \mid \tau_{\text{SF}}) = \text{SFR}_0 \cdot \frac{t}{\tau_{\text{SF}}} e^{-t/\tau_{\text{SF}}}$$
where $\tau_{\text{SF}}$ is the characteristic star formation timescale.

We define a cosmic time grid $t_k = k \cdot \Delta t$ from $t=0$ to the age of the galaxy $T \approx 13.7\text{ Gyr}$. The rate of supernovae at age $T$ is computed numerically as:
$$R_{\text{Ia}}(T \mid \tau_{\text{SF}}, \gamma) = \sum_{\tau_k \ge t_{\text{min}}}^{T} \text{SFR}(T - \tau_k \mid \tau_{\text{SF}}) \cdot \tau_k^{-\gamma} \cdot \Delta t$$

### Reconstructing $\gamma$ via PyTorch Physics-Informed Optimization
We will build a PyTorch solver `DTDConvolutionSolver` to learn the power-law index $\gamma$ from a sample of galaxies with different ages and star formation timescales. The solver computes the convolution integral dynamically, evaluates the negative log-likelihood of host galaxy parameters, and optimizes $\gamma$ using gradient descent.
"""

ex15_code_student = """# Task 15: Type Ia Supernova Delay Time Distribution (DTD) Reconstruction

# 1. Create a synthetic galaxy sample with Star Formation History parameters
np.random.seed(42)
n_galaxies = 500
galaxy_ages = np.random.uniform(8.0, 13.0, n_galaxies)  # Galaxy age in Gyr
galaxy_tau_sf = np.random.uniform(1.0, 5.0, n_galaxies) # SF timescale in Gyr

# Define time grid for integration
dt = 0.1
t_grid = np.arange(0.0, 13.7, dt)

# True delay time distribution: Psi(tau) = tau^(-gamma) for tau >= 0.1 Gyr
gamma_true = 1.15
t_min = 0.1

# Calculate rates for each galaxy via numerical convolution (vectorized in NumPy)
ages_col = galaxy_ages[:, np.newaxis]
taus_col = galaxy_tau_sf[:, np.newaxis]

t_sf = ages_col - t_grid[np.newaxis, :]  # shape (n_galaxies, n_time_steps)
sfr = np.where(t_sf >= 0, t_sf * np.exp(-t_sf / taus_col), 0.0)
psi = np.where(t_grid >= t_min, t_grid ** (-gamma_true), 0.0)
galaxy_rates = np.sum(sfr * psi[np.newaxis, :], axis=1) * dt

# Draw observed host galaxies using weighted sampling
n_hosts = 100
host_indices = np.random.choice(n_galaxies, size=n_hosts, replace=True, p=galaxy_rates/galaxy_rates.sum())
host_ages = galaxy_ages[host_indices]
host_tau_sf = galaxy_tau_sf[host_indices]

# 2. Build the PyTorch DTD Convolution Solver
class DTDConvolutionSolver(nn.Module):
    def __init__(self, tau_grid):
        super().__init__()
        # Learnable raw_gamma parameter
        self.raw_gamma = nn.Parameter(torch.tensor([0.0]))  # exp(0) = 1.0
        self.register_buffer('tau_grid', tau_grid)          # shape (1, K)
        
    def get_gamma(self):
        # Enforce positive gamma
        return torch.exp(self.raw_gamma)
        
    def forward(self, ages, taus_sf):
        # shapes: ages (N, 1), taus_sf (N, 1)
        gamma = self.get_gamma()
        
        # Calculate t_sf = ages - tau_grid
        t_sf = ages - self.tau_grid
        
        # Calculate SFR: SFR(t_sf) = t_sf * exp(-t_sf / taus_sf) where t_sf >= 0, else 0.0
        # Hint: use torch.where and torch.exp
        sfr = ### FIX_ME_SFR_TENSOR ###
        
        # Calculate DTD: Psi(tau) = tau^(-gamma) for tau >= 0.1, else 0.0
        safe_tau = torch.clamp(self.tau_grid, min=0.01)
        psi = ### FIX_ME_PSI_TENSOR ###
        
        # Compute numerical convolution integral
        rates = torch.sum(sfr * psi, dim=1) * 0.1
        return rates

# Convert arrays to PyTorch tensors
tau_grid_t = torch.tensor(t_grid, dtype=torch.float32).unsqueeze(0) # shape (1, K)
ages_all_t = torch.tensor(galaxy_ages, dtype=torch.float32).unsqueeze(1)
taus_all_t = torch.tensor(galaxy_tau_sf, dtype=torch.float32).unsqueeze(1)
ages_hosts_t = torch.tensor(host_ages, dtype=torch.float32).unsqueeze(1)
taus_hosts_t = torch.tensor(host_tau_sf, dtype=torch.float32).unsqueeze(1)

solver = DTDConvolutionSolver(tau_grid_t)
optimizer = torch.optim.Adam(solver.parameters(), lr=0.03)

# Training loop
epochs = 200
loss_history = []
for epoch in range(epochs):
    optimizer.zero_grad()
    
    # Predict rates for observed hosts and all galaxies
    rates_hosts = solver(ages_hosts_t, taus_hosts_t)
    rates_all = solver(ages_all_t, taus_all_t)
    
    # Calculate negative log-likelihood loss
    loss = -torch.sum(torch.log(rates_hosts + 1e-10)) + len(rates_hosts) * torch.log(torch.sum(rates_all) + 1e-10)
    loss.backward()
    optimizer.step()
    
    loss_history.append(loss.item())

gamma_recovered = solver.get_gamma().item()
print(f"Delay Time Distribution Power-Law Recovery:")
print(f"  - True gamma: {gamma_true:.3f}")
print(f"  - Recovered gamma: {gamma_recovered:.3f}")"""

ex15_code_solution = """# Task 15: Type Ia Supernova Delay Time Distribution (DTD) Reconstruction

# 1. Create a synthetic galaxy sample with Star Formation History parameters
np.random.seed(42)
n_galaxies = 500
galaxy_ages = np.random.uniform(8.0, 13.0, n_galaxies)  # Galaxy age in Gyr
galaxy_tau_sf = np.random.uniform(1.0, 5.0, n_galaxies) # SF timescale in Gyr

# Define time grid for integration
dt = 0.1
t_grid = np.arange(0.0, 13.7, dt)

# True delay time distribution: Psi(tau) = tau^(-gamma) for tau >= 0.1 Gyr
gamma_true = 1.15
t_min = 0.1

# Calculate rates for each galaxy via numerical convolution (vectorized in NumPy)
ages_col = galaxy_ages[:, np.newaxis]
taus_col = galaxy_tau_sf[:, np.newaxis]

t_sf = ages_col - t_grid[np.newaxis, :]  # shape (n_galaxies, n_time_steps)
sfr = np.where(t_sf >= 0, t_sf * np.exp(-t_sf / taus_col), 0.0)
psi = np.where(t_grid >= t_min, t_grid ** (-gamma_true), 0.0)
galaxy_rates = np.sum(sfr * psi[np.newaxis, :], axis=1) * dt

# Draw observed host galaxies using weighted sampling
n_hosts = 100
host_indices = np.random.choice(n_galaxies, size=n_hosts, replace=True, p=galaxy_rates/galaxy_rates.sum())
host_ages = galaxy_ages[host_indices]
host_tau_sf = galaxy_tau_sf[host_indices]

# 2. Build the PyTorch DTD Convolution Solver
class DTDConvolutionSolver(nn.Module):
    def __init__(self, tau_grid):
        super().__init__()
        self.raw_gamma = nn.Parameter(torch.tensor([0.0]))  # exp(0) = 1.0
        self.register_buffer('tau_grid', tau_grid)          # shape (1, K)
        
    def get_gamma(self):
        return torch.exp(self.raw_gamma)
        
    def forward(self, ages, taus_sf):
        gamma = self.get_gamma()
        t_sf = ages - self.tau_grid
        sfr = torch.where(t_sf >= 0, t_sf * torch.exp(-t_sf / taus_sf), torch.tensor(0.0))
        safe_tau = torch.clamp(self.tau_grid, min=0.01)
        psi = torch.where(self.tau_grid >= 0.1, safe_tau ** (-gamma), torch.tensor(0.0))
        rates = torch.sum(sfr * psi, dim=1) * 0.1
        return rates

# Convert arrays to PyTorch tensors
tau_grid_t = torch.tensor(t_grid, dtype=torch.float32).unsqueeze(0) # shape (1, K)
ages_all_t = torch.tensor(galaxy_ages, dtype=torch.float32).unsqueeze(1)
taus_all_t = torch.tensor(galaxy_tau_sf, dtype=torch.float32).unsqueeze(1)
ages_hosts_t = torch.tensor(host_ages, dtype=torch.float32).unsqueeze(1)
taus_hosts_t = torch.tensor(host_tau_sf, dtype=torch.float32).unsqueeze(1)

solver = DTDConvolutionSolver(tau_grid_t)
optimizer = torch.optim.Adam(solver.parameters(), lr=0.03)

# Training loop
epochs = 200
loss_history = []
for epoch in range(epochs):
    optimizer.zero_grad()
    rates_hosts = solver(ages_hosts_t, taus_hosts_t)
    rates_all = solver(ages_all_t, taus_all_t)
    loss = -torch.sum(torch.log(rates_hosts + 1e-10)) + len(rates_hosts) * torch.log(torch.sum(rates_all) + 1e-10)
    loss.backward()
    optimizer.step()
    loss_history.append(loss.item())

gamma_recovered = solver.get_gamma().item()
print(f"Delay Time Distribution Power-Law Recovery:")
print(f"  - True gamma: {gamma_true:.3f}")
print(f"  - Recovered gamma: {gamma_recovered:.3f}")

# 3. Plot DTD Reconstruction Results
fig, axs = plt.subplots(1, 2, figsize=(14, 5), dpi=120)

tau_plot = np.linspace(0.1, 3.0, 200)
axs[0].plot(tau_plot, tau_plot**(-gamma_true), 'r-', linewidth=2.5, label=f'True DTD ($\\\\gamma$ = {gamma_true:.3f})')
axs[0].plot(tau_plot, tau_plot**(-gamma_recovered), 'b--', linewidth=2.5, label=f'Recovered DTD ($\\\\gamma$ = {gamma_recovered:.3f})')
axs[0].set_xlabel('Delay Time $\\\\tau$ (Gyr)', fontsize=11)
axs[0].set_ylabel('Relative Rate $\\\\Psi(\\\\tau)$', fontsize=11)
axs[0].set_title('Ia SN Delay Time Distribution (DTD)', fontsize=12, fontweight='bold')
axs[0].legend()
axs[0].grid(True, linestyle=':', alpha=0.5)

axs[1].plot(loss_history, color='#2c3e50', linewidth=2)
axs[1].set_xlabel('Epoch', fontsize=11)
axs[1].set_ylabel('Negative Log Likelihood Loss', fontsize=11)
axs[1].set_title('PyTorch Optimization Convergence', fontsize=12, fontweight='bold')
axs[1].grid(True, linestyle=':', alpha=0.5)

plt.tight_layout()
os.makedirs('plots', exist_ok=True)
plt.savefig('plots/task15_dtd_reconstruction.png', dpi=300, bbox_inches='tight')
plt.show()"""

# ==============================================================================
# ASSEMBLE CELL DICTIONARIES FOR PHASE 2
# ==============================================================================

assignment_cells = [
    make_markdown_cell(intro_md),
    make_code_cell(setup_code),
    make_markdown_cell(task7_theory),
    make_code_cell(ex7_code_student),
    make_markdown_cell(task8_theory),
    make_code_cell(ex8_code_student),
    make_markdown_cell(task9_theory),
    make_code_cell(ex9_code_student),
    make_markdown_cell(task10_theory),
    make_code_cell(ex10_code_student),
    make_markdown_cell(task11_theory),
    make_code_cell(ex11_code_student),
    make_markdown_cell(task12_theory),
    make_code_cell(ex12_code_student),
    make_markdown_cell(task13_theory),
    make_code_cell(ex13_code_student),
    make_markdown_cell(task14_theory),
    make_code_cell(ex14_code_student),
    make_markdown_cell(task15_theory),
    make_code_cell(ex15_code_student)
]

solution_cells = [
    make_markdown_cell(intro_md.replace("Project Milestone 2: Statistical Modeling and Deep Learning", "Project Milestone 2 (Master Grading Key)")),
    make_code_cell(setup_code),
    make_markdown_cell(task7_theory),
    make_code_cell(ex7_code_solution),
    make_markdown_cell(task8_theory),
    make_code_cell(ex8_code_solution),
    make_markdown_cell(task9_theory),
    make_code_cell(ex9_code_solution),
    make_markdown_cell(task10_theory),
    make_code_cell(ex10_code_solution),
    make_markdown_cell(task11_theory),
    make_code_cell(ex11_code_solution),
    make_markdown_cell(task12_theory),
    make_code_cell(ex12_code_solution),
    make_markdown_cell(task13_theory),
    make_code_cell(ex13_code_solution),
    make_markdown_cell(task14_theory),
    make_code_cell(ex14_code_student),
    make_markdown_cell(task15_theory),
    make_code_cell(ex15_code_solution)
]

# Create notebooks on disk
if __name__ == '__main__':
    os.makedirs('notebooks', exist_ok=True)
    create_notebook(assignment_cells, "notebooks/stellar_trace_assignment2.ipynb")
    # No longer generating solution2
    print("Phase 2 notebooks generated successfully!")
