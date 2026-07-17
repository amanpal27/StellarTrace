# Stellar Trace Web Dashboard Architecture

The Stellar Trace web interface is a comprehensive platform built to showcase our astrophysics research project. It is composed of two distinct components designed for different use cases: a modern, static frontend landing application and a heavy-duty Python-based machine learning dashboard.

---

## 1. Frontend Application (React + Vite)

The frontend is a Single Page Application (SPA) located in the `frontend/` directory. It serves as the primary landing site, presenting the project's curriculum, team members, and interactive visualizations.

### Technology Stack
- **Build Tool**: Vite (Lightning fast HMR and optimized production builds)
- **Framework**: React 18
- **Styling**: Inline styles and CSS classes featuring modern glassmorphism UI, gradients, and dark mode aesthetic (`#090d16` background).
- **Deployment**: Configured for static hosting on Vercel.

### Core Features
- **Project Showcase (`App.jsx`)**: The main entry point featuring sticky navigation, a hero section, and responsive grids for the Curriculum and Cohort (Team) sections.
- **Scientific Diagnostics Gallery**: Displays high-quality matplotlib diagnostic plots from the Jupyter Notebook milestones, utilizing an interactive modal overlay (zoom-in) for detailed viewing.
- **Interactive Simulators**: The React app houses a tabbed interface for embedding client-side physics simulators:
  - 🌌 3D Galaxy Physics Simulator (`GalaxyCanvas`)
  - 🎲 MCMC Markov Walk (`McmcSim`)
  - 🧠 Host Classifier (`Classifier`)
  - 📐 Convolved DTD Solver (`DtdSim`)

---

## 2. Interactive ML Dashboard (Streamlit)

Located in the `dashboard/` directory, the Python-based dashboard provides a direct interface to the trained machine learning models and astrophysics hypothesis tests without requiring users to run Jupyter Notebooks.

### Technology Stack
- **Framework**: Streamlit
- **Data & Math**: Pandas, NumPy, Scikit-learn
- **Visualizations**: Plotly (Interactive charts)
- **UI Customization**: Custom CSS injection (Outfit & JetBrains Mono fonts, glassmorphism cards).

### Core Features
- **Machine Learning Inference**: Uses `@st.cache_resource` to load pre-trained models (e.g., standard scalers, polynomial features, regression, and MLP classifiers) for real-time predictions.
- **Host Probability Engine**: Users can input features like stellar mass and redshift, and the dashboard runs the prediction pipeline to classify the galaxy as Background, CC-SN Host, or Ia-SN Host.
- **Interactive Quizzes**: Presents educational quizzes using interactive Streamlit widgets to test mentee knowledge.

---

## Deployment Strategy

The two applications are decoupled for optimal deployment:
1. **Frontend Landing Page (Vercel)**: Deployed to Vercel via the `vercel deploy --prod` CLI. It builds the static React bundle using `npm run build` and serves it on a global CDN. This guarantees fast initial load times.
2. **Streamlit Dashboard (Cloud Hosting)**: The `app.py` script requires a persistent Python runtime (with heavy dependencies like `scikit-learn` and `streamlit`). It is deployed independently (typically on Streamlit Community Cloud or a dedicated container service) rather than Vercel, as Vercel is designed for serverless functions, not stateful WebSockets.
