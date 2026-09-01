# 🚀 Scheduled Daily Computer Science Research Papers Agent

An automated, intelligent pair-programming workflow that discovers **5 newly published Computer Science research papers every day at 7:00 AM IST**, performs a structured multi-point technical synthesis, and delivers a clean, responsive HTML email digest to your inbox.

> **Key Feature:** Powered by **GitHub Actions Cloud Scheduling**, this workflow executes reliably at **7:00 AM IST every single day even when your laptop is completely powered off**!

---

## 📋 Features

- 🔍 **Dual-Source Paper Discovery:** Primary Google Scholar scraper with automatic, seamless fallback to the official arXiv CS API (`cat:cs.*` encompassing AI, ML, NLP, Vision, Security, Robotics, Systems) and Semantic Scholar.
- 🗄️ **Zero Duplicate Guarantee:** Persistent SQLite database (`data/papers_history.db`) indexes paper IDs, URLs, and normalized title hashes so you never receive the same paper twice.
- 🧠 **6-Point Structured Technical Synthesis:**
  1. **Metadata:** Paper title, authors, venue, publication date, and direct PDF link.
  2. **One-Line Summary:** Exactly 1 compressed sentence capturing core technical innovation.
  3. **Real-World Relevance:** 1–2 practical sentences explaining direct application.
  4. **Prior Tech vs. Proposed:** 3–5 bullet points comparing prior technology against proposed solutions (factual differences only, zero marketing hype).
  5. **Critical Motivation:** Core bottleneck, challenge, or gap the authors set out to solve.
  6. **Business & Industry Impact:** Practical implications for engineering teams and tech companies.
- 📧 **Clean HTML & Plain-Text Email:** Clean, responsive design optimized to be skimmed in under 2 minutes.
- ☁️ **Dual Execution Architecture:**
  - **Cloud (Primary):** GitHub Actions cron running at `01:30 UTC` (**7:00 AM IST**) with zero laptop dependency.
  - **Local (Secondary):** Windows Scheduled Task with missed-start catch-up (`StartWhenAvailable`).

---

## 📂 Project Structure

```
d:\Agents\
├── .github/
│   └── workflows/
│       └── daily_cs_papers.yml      # Cloud scheduler (Runs daily at 7:00 AM IST)
├── data/
│   └── papers_history.db            # SQLite database for deduplication & audit logs
├── logs/
│   └── workflow.log                 # Execution logs
├── .env.example                     # Environment template
├── .env                             # Local secrets (ignored by Git)
├── .gitignore                       # Protects credentials from being pushed
├── config.py                        # Centralized settings loader
├── database.py                      # SQLite database operations
├── fetcher.py                       # Scholar / arXiv paper retrieval
├── summarizer.py                    # 6-point structured analysis engine
├── email_builder.py                 # Responsive HTML and plain-text email compiler
├── email_sender.py                  # Gmail SMTP dispatcher
├── main.py                          # CLI & workflow controller
├── test_run.py                      # End-to-end testing suite
├── setup_windows_task.ps1           # Windows Task Scheduler installer
├── run_workflow.bat                 # 1-click batch runner
├── sample_email.html                # Generated sample preview
└── requirements.txt                 # Python dependencies
```

---

## 🛠️ Step-by-Step Guide: Activate on GitHub (Runs Even When Laptop is Off)

Follow these steps to deploy and activate the daily 7:00 AM IST automated cloud workflow:

### Step 1: Create a New GitHub Repository
1. Log in to [GitHub](https://github.com).
2. Click the **`+`** icon in the top right corner $\rightarrow$ **New repository**.
3. Repository name: `daily-cs-papers` (or any name you prefer).
4. Select **Private** (recommended to keep your paper history private).
5. **Do not** check "Add a README file", ".gitignore", or "license" (we already have them).
6. Click **Create repository**.

---

### Step 2: Push Your Code to GitHub
Open **PowerShell** or **Command Prompt** in `d:\Agents` and run:

```powershell
# 1. Navigate to the project directory
cd d:\Agents

# 2. Initialize git (if not already initialized)
git init

# 3. Add and commit all project files (.env is automatically ignored)
git add .
git commit -m "Initial commit: Daily CS Papers Agent Workflow"

# 4. Set the main branch
git branch -M main

# 5. Link your GitHub remote repository (replace with your GitHub username/repo URL)
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/daily-cs-papers.git

# 6. Push to GitHub
git push -u origin main
```

> 🔒 **Security Note:** Your local `.env` file is protected by `.gitignore` and will **never** be pushed to GitHub.

---

### Step 3: Add Your Repository Secrets
GitHub Actions uses encrypted secrets to securely access Gmail and the Gemini API without exposing credentials in code:

1. Open your repository on GitHub.
2. Go to **Settings** (tab at the top) $\rightarrow$ **Secrets and variables** (left sidebar) $\rightarrow$ **Actions**.
3. Click the green **New repository secret** button.
4. Add the following secrets:

| Secret Name | Value | Required? |
| :--- | :--- | :--- |
| `GMAIL_USER` | `s.sindhu210506@gmail.com` | **Yes** |
| `GMAIL_APP_PASSWORD` | Your 16-character Google App Password (e.g. `abcd efgh ijkl mnop` spaces removed) | **Yes** |
| `RECIPIENT_EMAIL` | `s.sindhu210506@gmail.com` | Optional (defaults to `s.sindhu210506@gmail.com`) |
| `GEMINI_API_KEY` | Your Google AI Studio Gemini API Key | Optional (enables Gemini 2.5 Flash analysis) |

> 🔑 **How to get a Gmail App Password:**
> 1. Go to [myaccount.google.com/security](https://myaccount.google.com/security).
> 2. Ensure **2-Step Verification** is turned ON.
> 3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
> 4. Create an app named `CS Papers Agent` and copy the 16-character password.

---

### Step 4: Enable Workflow Read & Write Permissions
To allow GitHub Actions to commit and persist your SQLite deduplication database across daily runs:

1. In your GitHub repository, go to **Settings** $\rightarrow$ **Actions** $\rightarrow$ **General**.
2. Scroll down to **Workflow permissions**.
3. Select **Read and write permissions**.
4. Check the box **Allow GitHub Actions to create and approve pull requests**.
5. Click **Save**.

---

### Step 5: Test the Workflow Manually on GitHub
You do not have to wait until 7:00 AM to verify your setup:

1. In your GitHub repository, click the **Actions** tab at the top.
2. Under **Workflows** on the left, click **Daily CS Research Papers Digest**.
3. Click the **Run workflow** dropdown on the right and click the green **Run workflow** button.
4. Click on the running job to watch the live execution logs:
   - Fetches 5 fresh CS papers from arXiv / Scholar
   - Synthesizes 6 structured analysis points
   - Renders HTML email
   - Sends email to `s.sindhu210506@gmail.com`
   - Commits updated SQLite database
5. Check your Gmail inbox for your first live digest!

---

### Step 6: Daily Automatic Execution
The workflow is now fully active!
- **Schedule:** Triggers automatically every morning at **01:30 UTC** (**7:00 AM IST**).
- **Completion:** Delivers your daily digest well before **7:30 AM IST**.
- **Hardware Requirement:** **None!** Runs in GitHub's cloud environment even if your laptop is powered off, asleep, or disconnected from the internet.

---

## 💻 Local Usage & Commands

You can also run, test, and manage the agent locally on your computer.

### 1. Local Configuration
Edit `d:\Agents\.env` and provide your credentials:
```ini
GMAIL_USER=s.sindhu210506@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
RECIPIENT_EMAIL=s.sindhu210506@gmail.com
GEMINI_API_KEY=
PAPERS_PER_DAY=5
```

### 2. Available CLI Commands

- **Run full test suite (Database, Fetcher, Summarizer, HTML Preview):**
  ```powershell
  python test_run.py
  ```

- **Run dry-run without sending email or modifying DB:**
  ```powershell
  python main.py --dry-run
  ```

- **Send a quick test email to verify SMTP credentials:**
  ```powershell
  python main.py --test-email
  ```

- **Run daily workflow and send email:**
  ```powershell
  python main.py
  ```

- **Inspect past execution audit log and total sent papers:**
  ```powershell
  python main.py --history
  ```

---

## ⏰ Local Windows Task Scheduler (Catch-up Mode)

If you also want local automation with catch-up (so that if your laptop was off at 7:00 AM, it immediately runs when you turn it on):

1. Open PowerShell as **Administrator**.
2. Run:
   ```powershell
   cd d:\Agents
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\setup_windows_task.ps1
   ```
3. This creates a Windows task named `DailyCSPapersDigest` with `StartWhenAvailable` enabled.

---

## 🧪 Technical Specifications

- **Python Version:** 3.12+
- **Primary Scraper:** Requests + BeautifulSoup (mimicking desktop user-agent)
- **Fallback API:** arXiv Atom Feed (`export.arxiv.org/api/query`) & Semantic Scholar REST API
- **AI Model:** Gemini 2.5 Flash / Smart Extractive Heuristic Analyzer
- **Database:** SQLite 3 (ACID compliant, zero-configuration)
- **Delivery Protocol:** SMTP with STARTTLS (Port 587) or SSL (Port 465)
- **Email Formats:** Multipart MIME with HTML + Plain text fallback
