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

## 📝 Mentee Submission Guide (For Beginners)

If you have never used Git or GitHub before, don't worry! Follow these step-by-step instructions carefully to submit your assignments.

### 1. Set Up GitHub & Git
If you haven't already:
1. **Create an account** on [GitHub](https://github.com/).
2. **Install Git** on your computer from [git-scm.com](https://git-scm.com/).
3. **Configure Git in your terminal:** Open your terminal (Command Prompt, PowerShell, or Git Bash) and run these commands to tell Git who you are:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### 2. Fork the Repository
A "Fork" is your own personal copy of the StellarTrace project.
1. Scroll to the top of this page on GitHub.
2. Click the **Fork** button (top right corner).
3. Confirm by clicking **Create fork**. This will create a copy under your account (`https://github.com/YourUsername/StellarTrace`).

### 3. Clone Your Fork to Your Computer
Now, download your fork to your computer:
1. On your forked repository page, click the green **<> Code** button and copy the HTTPS URL.
2. Open your terminal and run:
   ```bash
   git clone https://github.com/YourUsername/StellarTrace.git
   cd StellarTrace
   ```

### 4. Complete Your Assignments
1. Complete the code exercises in `notebooks/stellar_trace_assignment1.ipynb` and `notebooks/stellar_trace_assignment2.ipynb`.
2. Copy your completed notebooks into your dedicated folder inside `submissions/` (e.g., `submissions/Aryan_Trivedi/stellar_trace_assignment1.ipynb`). If your folder doesn't exist, create it!

### 5. Save and Push Your Changes
Once you are done, save your work back to GitHub:
1. **Add your changes** to the "staging area":
   ```bash
   git add submissions/Your_Name/
   ```
2. **Commit (save)** your changes with a descriptive message:
   ```bash
   git commit -m "Submit assignment - Your Name"
   ```
3. **Push (upload)** the changes to your fork on GitHub:
   ```bash
   git push origin main
   ```
   *(If prompted, log in with your GitHub account credentials or Personal Access Token in the browser window that pops up).*

### 6. Open a Pull Request (PR)
A Pull Request tells the mentors that your code is ready to be reviewed!
1. Go to your forked repository page on GitHub.
2. You should see a banner saying "This branch is 1 commit ahead of amanpal27:main". Click **Contribute**, then **Open pull request**.
3. Add a brief title (e.g., "Assignment Submission - Your Name") and click **Create pull request**.

Congratulations! You have successfully submitted your work! 🎉
