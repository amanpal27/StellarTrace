# Beginner's Guide: Building and Deploying the Stellar Trace Website

Welcome! Even if you have zero knowledge of web development, this guide will walk you through building and deploying the Stellar Trace website from scratch. We will build a beautiful website (Frontend) and then deploy it online for the world to see!

---

## Part 1: Setting up your Computer (The Prerequisites)

Before we write any code, we need to install a few tools on your computer.

1. **Install Node.js**: This is required to run our website. 
   - Go to [nodejs.org](https://nodejs.org/) and download the "LTS" (Long Term Support) version. 
   - Run the installer and keep clicking "Next" until it's finished.
2. **Install VS Code**: This is the text editor where we will write our code.
   - Go to [code.visualstudio.com](https://code.visualstudio.com/) and download/install it.

---

## Part 2: Building the Website (Frontend)

We will build the website using a popular tool called React.

### Step 1: Create the Project
1. Open your computer's Terminal (Command Prompt on Windows, Terminal on Mac).
2. Type the following command and press Enter:
   ```bash
   npm create vite@latest frontend -- --template react
   ```
3. Move into your new project folder by typing:
   ```bash
   cd frontend
   ```
4. Install the necessary files by typing:
   ```bash
   npm install
   ```

### Step 2: Run the Website Locally
To see your website working on your own computer:
1. In the terminal, type:
   ```bash
   npm run dev
   ```
2. Open your web browser (like Chrome or Safari) and go to the link shown in your terminal (usually `http://localhost:5173`). You'll see a starter website!

### Step 3: Add the Stellar Trace Code
1. Open the `frontend` folder in VS Code.
2. Open the `src/App.jsx` file. This is the main file for your website. 
3. You can replace the code in this file with your own text, images, and layout to match the Stellar Trace design. 

---

## Part 3: Deploying the Website to Vercel

Now let's put your website on the internet so anyone can see it! We'll use a free service called Vercel.

### Step 1: Create a Vercel Account
1. Go to [vercel.com](https://vercel.com/) and sign up for a free account.

### Step 2: Install Vercel on your computer
1. Open your terminal (make sure you are inside the `frontend` folder).
2. Install the Vercel tool by typing:
   ```bash
   npm i -g vercel
   ```

### Step 3: Deploy!
1. Log in to Vercel from your terminal by typing:
   ```bash
   vercel login
   ```
   Follow the instructions to log in using your browser.
2. Once logged in, type the deployment command:
   ```bash
   vercel --prod
   ```
3. It will ask you a few setup questions:
   - "Set up and deploy?" -> Press **Y** (Yes)
   - "Which scope?" -> Press Enter
   - "Link to existing project?" -> Press **N** (No)
   - "What's your project's name?" -> Press Enter (or type a name)
   - "In which directory is your code located?" -> Press Enter
   - "Want to modify these settings?" -> Press **N** (No)
4. Wait a minute or two. Vercel will give you a "Production URL". Click that link, and you will see your website live on the internet!

