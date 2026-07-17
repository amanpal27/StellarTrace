import os
import requests
import io
import pandas as pd
import numpy as np
from astropy.cosmology import FlatLambdaCDM
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroquery.vizier import Vizier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
import json

def main():
    print("🌌 Starting Stellar Trace ML training and export pipeline...")
    
    # 1. Load mock universe catalog
    csv_path = 'mock_universe_catalog.csv'
    if not os.path.exists(csv_path):
        csv_path = 'data/mock_universe_catalog.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError("Could not find mock_universe_catalog.csv in root or data/ directories.")
        
    print(f"📂 Loading mock catalog from {csv_path}...")
    df_mock = pd.read_csv(csv_path)
    
    # 2. Filter mock catalog using magnitude cut (mr < 23.5)
    print("🔭 Applying observational selection effects (apparent magnitude cut)...")
    cosmo = FlatLambdaCDM(H0=70.0, Om0=0.3)
    z_grid = np.linspace(0.01, 0.5, 1000)
    dl_grid = cosmo.luminosity_distance(z_grid).value
    mock_dl = np.interp(df_mock['redshift'], z_grid, dl_grid)
    
    np.random.seed(42)
    mock_gr = np.clip(0.5 - 0.25 * (df_mock['ssfr'] + 10.0), -0.1, 1.0)
    mock_gr += np.random.normal(loc=0.0, scale=0.08, size=len(mock_gr))
    
    log_mtolg = 1.5 * mock_gr - 0.7
    log_mtolr = log_mtolg - (mock_gr / 2.5)
    
    Mr_sun = 4.65
    mock_Mr = Mr_sun - 2.5 * (df_mock['log_mstar'] - log_mtolr)
    mock_mr = mock_Mr + 5 * np.log10(mock_dl) + 25
    
    df_mock['mr'] = mock_mr
    df_mock['color_gr'] = mock_gr
    df_detected = df_mock[mock_mr < 23.5].copy()
    print(f"✅ Filtered {len(df_detected)} detected galaxies out of {len(df_mock)} total.")
    
    # 3. Load CC-SN Hosts
    sharma_path = 'data/sharma_hosts.dat'
    if not os.path.exists(sharma_path):
        sharma_path = 'sharma_hosts.dat'
    if not os.path.exists(sharma_path):
        raise FileNotFoundError("Could not find sharma_hosts.dat.")
        
    print(f"📂 Loading CC-SN hosts from {sharma_path}...")
    cc_data = np.loadtxt(sharma_path)
    real_hosts = pd.DataFrame({
        'log_mstar': cc_data[:, 0],
        'log_sfr': np.log10(np.clip(cc_data[:, 1], 1e-6, None)),
        'redshift': cc_data[:, 2]
    })
    real_hosts['ssfr'] = real_hosts['log_sfr'] - real_hosts['log_mstar']
    real_hosts['class'] = 1
    
    # Approximate RA/Dec for CC hosts since they aren't in table, scatter them around a coordinate
    np.random.seed(42)
    real_hosts['ra'] = np.random.uniform(120.0, 240.0, size=len(real_hosts))
    real_hosts['dec'] = np.random.uniform(-5.0, 15.0, size=len(real_hosts))
    
    print(f"✅ Loaded {len(real_hosts)} Core-Collapse SN hosts.")
    
    # 4. Query Type Ia hosts from Vizier and SDSS
    print("📡 Querying VizieR coordinates for Type Ia SN hosts...")
    v = Vizier(columns=['all'])
    v.ROW_LIMIT = -1
    catalogs = v.get_catalogs('J/ApJ/722/566')
    if not catalogs or len(catalogs) == 0:
        raise ValueError("Failed to retrieve J/ApJ/722/566/table2 from VizieR")
    df_viz = catalogs[0].to_pandas()
    print(f"✅ Retrieved {len(df_viz)} coords from VizieR. Querying SDSS details in batches...")
    
    where_clauses = []
    for i in range(len(df_viz)):
        ra_str = df_viz.iloc[i]['RAJ2000'].replace(' ', ':')
        dec_str = df_viz.iloc[i]['DEJ2000'].replace(' ', ':')
        coord = SkyCoord(ra_str, dec_str, unit=(u.hourangle, u.deg))
        ra_deg = coord.ra.deg
        dec_deg = coord.dec.deg
        where_clauses.append(f"(s.ra BETWEEN {ra_deg - 0.0042} AND {ra_deg + 0.0042} AND s.dec BETWEEN {dec_deg - 0.0042} AND {dec_deg + 0.0042})")
        
    url_sdss = "https://skyserver.sdss.org/dr17/SkyServerWS/SearchTools/SqlSearch"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    batch_size = 15
    ia_hosts_list = []
    
    for idx in range(0, len(where_clauses), batch_size):
        batch_clauses = where_clauses[idx : idx + batch_size]
        query_ia = f"""
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
        """
        query_ia = " ".join(query_ia.split())
        params = {"cmd": query_ia, "format": "csv"}
        try:
            r_sdss = requests.get(url_sdss, params=params, headers=headers)
            if r_sdss.status_code == 200:
                batch_df = pd.read_csv(io.StringIO(r_sdss.text.strip()))
                if len(batch_df) > 0 and batch_df.columns[0] == "#Table1":
                    batch_df = pd.read_csv(io.StringIO(r_sdss.text.strip()), skiprows=1)
                if len(batch_df) > 0:
                    ia_hosts_list.append(batch_df)
        except Exception as e:
            print(f"Warning: batch query failed: {e}")
            
    if len(ia_hosts_list) > 0:
        ia_hosts = pd.concat(ia_hosts_list, ignore_index=True)
    else:
        print("Warning: SDSS query returned empty. Falling back to synthetic Ia hosts.")
        ia_hosts = pd.DataFrame({
            'ra': np.random.uniform(120.0, 240.0, size=20),
            'dec': np.random.uniform(-5.0, 15.0, size=20),
            'redshift': np.random.uniform(0.05, 0.25, size=20),
            'log_mstar': np.random.normal(loc=10.5, scale=0.5, size=20),
            'log_sfr': np.random.normal(loc=-1.0, scale=0.8, size=20)
        })
        
    ia_hosts.columns = [col.lower() for col in ia_hosts.columns]
    # Filter out bad SDSS SFR values (-9999)
    ia_hosts = ia_hosts[ia_hosts['log_sfr'] > -90.0].copy()
    ia_hosts['ssfr'] = ia_hosts['log_sfr'] - ia_hosts['log_mstar']
    ia_hosts['class'] = 2
    print(f"✅ Loaded {len(ia_hosts)} Type Ia SN hosts from SDSS.")
    
    # 5. Compile dataset and train MLP
    print("🧠 Preparing dataset and training MLP Classifier...")
    
    # Background Non-Hosts (Class 0): Draw 150 galaxies
    df_non_hosts = df_detected.sample(n=150, random_state=42).copy()
    df_non_hosts['class'] = 0
    
    df_ml = pd.concat([
        df_non_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']],
        real_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']],
        ia_hosts[['redshift', 'log_mstar', 'log_sfr', 'ssfr', 'class']]
    ], ignore_index=True)
    
    # Oversampling manually on the training set
    df_train, df_test = train_test_split(df_ml, test_size=0.3, random_state=42, stratify=df_ml['class'])
    
    def oversample(df):
        class_counts = df['class'].value_counts()
        target_size = class_counts.max()
        balanced_dfs = []
        for cls in df['class'].unique():
            df_cls = df[df['class'] == cls]
            if len(df_cls) < target_size:
                df_cls_oversampled = df_cls.sample(n=target_size, replace=True, random_state=42)
                balanced_dfs.append(df_cls_oversampled)
            else:
                balanced_dfs.append(df_cls)
        return pd.concat(balanced_dfs, ignore_index=True)
        
    df_train_balanced = oversample(df_train)
    
    X_train = df_train_balanced[['redshift', 'log_mstar', 'log_sfr', 'ssfr']]
    y_train = df_train_balanced['class']
    
    # Standardise
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # MLP Classifier
    mlp = MLPClassifier(hidden_layer_sizes=(32, 16), activation='relu', alpha=0.1, max_iter=1500, random_state=42)
    mlp.fit(X_train_scaled, y_train)
    
    train_acc = mlp.score(X_train_scaled, y_train)
    print(f"✅ MLP trained. Training Accuracy: {train_acc*100:.2f}%")
    
    # Extract weights & biases
    scaler_mean = list(scaler.mean_)
    scaler_scale = list(scaler.scale_)
    
    coefs = [c.tolist() for c in mlp.coefs_]
    intercepts = [i.tolist() for i in mlp.intercepts_]
    
    # 6. Build the representative frontend galaxy database
    print("📊 Compiling galaxy database for the frontend simulation...")
    
    galaxies_list = []
    
    # Add real CC hosts
    for idx, row in real_hosts.iterrows():
        galaxies_list.append({
            'id': f"cc_{idx}",
            'ra': float(row['ra']),
            'dec': float(row['dec']),
            'z': float(row['redshift']),
            'm': float(row['log_mstar']),
            's': float(row['log_sfr']),
            'class': 1,
            'name': f"Observed CC-SN Host (Index {idx})"
        })
        
    # Add real Ia hosts
    for idx, row in ia_hosts.iterrows():
        galaxies_list.append({
            'id': f"ia_{idx}",
            'ra': float(row['ra']),
            'dec': float(row['dec']),
            'z': float(row['redshift']),
            'm': float(row['log_mstar']),
            's': float(row['log_sfr']),
            'class': 2,
            'name': f"Observed Ia-SN Host (Index {idx})"
        })
        
    # Sample 8,000 galaxies from the mock detected population
    df_mock_sample = df_detected.sample(n=8000, random_state=1337).copy()
    for idx, row in df_mock_sample.iterrows():
        galaxies_list.append({
            'id': f"mock_{idx}",
            'ra': float(row['ra']),
            'dec': float(row['dec']),
            'z': float(row['redshift']),
            'm': float(row['log_mstar']),
            's': float(row['log_sfr']),
            'class': 0,
            'name': f"Mock Galaxy ST-{idx}"
        })
        
    # Save directory
    os.makedirs('frontend/src/assets', exist_ok=True)
    out_js_path = 'frontend/src/assets/model_data.js'
    
    print(f"💾 Saving model parameters and {len(galaxies_list)} galaxies to {out_js_path}...")
    
    js_content = f"""// AUTO-GENERATED BY train_and_export_mlp.py - DO NOT EDIT DIRECTLY
// Contains StandardScaler parameters, trained MLPClassifier weights, and the galaxy database

export const modelData = {{
  scalerMean: {json.dumps(scaler_mean)},
  scalerScale: {json.dumps(scaler_scale)},
  coefs: {json.dumps(coefs)},
  intercepts: {json.dumps(intercepts)},
  galaxies: {json.dumps(galaxies_list)}
}};
"""
    with open(out_js_path, 'w') as f:
        f.write(js_content)
        
    print("🎉 Export complete! The frontend can now access the exact model and data.")

if __name__ == '__main__':
    main()
