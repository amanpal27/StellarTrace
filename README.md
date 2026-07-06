# Stellar Trace

Stellar Trace is a summer project offered by the **Astronomy Club** focusing on modeling galaxy populations, observational selection effects, host galaxy classification, and transient rate calculations.

---

## 👥 The Team

### 🌟 Mentors
*   Aman Pal
*   Preet Varu
*   Aric Tirkey
*   Ujjwal Prakash

### 🚀 Mentees
*   Adit Bansal, Ankita Chatterjee, Aryan Trivedi, Chethana Kotla, Deeksha Badhan, Dhairya Garg, Gurmannat, Kanak, Kuldeep Turkar, Kushagra Rajput, Rajit Dhakad, Shriom Gupta, Sree Neha Reddy Gavva, Yash Kumar

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
│   ├── mock_universe_catalog.csv  # Simulated galaxy catalog
│   ├── sharma_hosts.dat           # Real CC-SN hosts data
│   └── sdss_data.dat              # SDSS query backup data
├── scripts/
│   ├── galfrb_project_pipeline.py # Computational pipelines
│   ├── generate_notebooks.py      # Notebook generator part 1
│   └── generate_notebooks_part2.py# Notebook generator part 2
├── slides/                        # LaTeX Beamer slide decks and tutorials
│   ├── meet1_tasks7_9.tex         # Meet 1 slides (Observational selection)
│   ├── meet1_stats_foundations.tex # Meet 1 statistics foundations tutorial
│   ├── meet2_tasks10_12.tex       # Meet 2 slides (ML Host classification)
│   ├── meet2_neural_networks.tex  # Meet 2 neural networks tutorial
│   ├── meet3_tasks13_15.tex       # Meet 3 slides (Tasks 13--15 roadmap)
│   └── meet3_bayesian_stats_and_pinn.tex # Comprehensive Bayesian Stats & PINN tutorial
├── quizzes/
│   ├── stellar_trace_mentee_quiz.md      # Written academic test
│   ├── stellar_trace_mentor_answer_key.md # Mentor evaluation key
│   └── ... (quiz templates)
├── frontend/                      # React/Vite interactive showcase site
│   ├── src/                       # Custom source code
│   └── package.json               # Frontend dependencies
├── submissions/                   # Assignment submissions folder
│   ├── [Mentee_Name]/             # Individual subfolders for each mentee
│   └── ...
└── README.md                      # Project documentation
```

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/amanpal27/StellarTrace.git
cd StellarTrace
```

### 2. Configure Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate

pip install -r dashboard/requirements.txt
```

### 3. Run the Streamlit Dashboard
```bash
streamlit run dashboard/app.py
```

### 4. Running the Jupyter Notebooks
```bash
pip install jupyter
jupyter notebook
```
Navigate to the `notebooks/` folder to open the assignments or solutions.

---

## 📝 Mentee Submission Guide

Mentees should submit their completed assignments using the following workflow:
1. **Fork** this repository to your personal GitHub account.
2. Complete the code exercises in `stellar_trace_assignment1.ipynb` and `stellar_trace_assignment2.ipynb`.
3. Copy your completed notebooks into your dedicated folder inside `submissions/` (e.g., `submissions/Aryan_Trivedi/stellar_trace_assignment1.ipynb`).
4. Commit your changes and push them to your fork:
   ```bash
   git add submissions/Aryan_Trivedi/
   git commit -m "Submit assignment - Aryan Trivedi"
   git push origin main
   ```
5. Open a **Pull Request** comparing your fork's submission folder against the main repository.
