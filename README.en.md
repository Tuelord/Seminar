# Software Architecture Report — MLOps

> 🇻🇳 **[Phiên bản tiếng Việt](README.md)**  
> **Course:** Software Architecture  
> **Team:** 7 members  
> **Report:** MLOps Architecture: Design, Rationale, and Layered Model

[![Build LaTeX PDF](../../actions/workflows/build-pdf.yml/badge.svg)](../../actions/workflows/build-pdf.yml)

---

## Table of Contents

- [Repository Structure](#repository-structure)
- [File Ownership](#file-ownership)
- [Repository Setup](#repository-setup)
- [Commit & Branch Rules](#commit--branch-rules)
- [Build PDF Locally](#build-pdf-locally)
- [Check PDF via GitHub Actions](#check-pdf-via-github-actions)
- [Quick Guide: Clone → Edit → Push](#quick-guide-clone--edit--push)
- [MLOps Demo](#mlops-demo)
- [Team Members & Contact](#team-members--contact)

---

## Repository Structure

```
SoftwareArchitectureReport/
├── main.tex                        ← Entry point (ONLY Member A edits this)
├── references.bib                  ← References (everyone may ADD entries)
├── hcmut-report.cls                ← HCMUT LaTeX class (do not edit)
├── codespace.sty                   ← Style configuration (do not edit)
├── sections/
│   ├── 01-introduction.tex         ← Member B
│   ├── 02-mlops-concepts.tex       ← Member C
│   ├── 03-design-rationale.tex     ← Member D
│   ├── 04-pros-cons.tex            ← Member E
│   ├── 05-layered-architecture.tex ← Member F
│   └── 06-conclusion.tex           ← Member A
├── figures/                        ← Images (PNG/PDF/SVG) — everyone may add
├── graphics/
│   └── hcmut.png                   ← HCMUT logo (do not edit)
├── demo/                           ← MLOps demo stack (Member G manages)
│   ├── README.md
│   ├── docker-compose.yml
│   ├── train_demo.py
│   └── serve_demo.py
└── .github/
    └── workflows/
        └── build-pdf.yml           ← GitHub Actions — auto-build PDF
```

---

## File Ownership

| File | Owner | Notes |
|---|---|---|
| `main.tex` | **Member A** | Team lead — NO ONE else edits this |
| `sections/01-introduction.tex` | **Member B** | Introduction |
| `sections/02-mlops-concepts.tex` | **Member C** | MLOps Concepts |
| `sections/03-design-rationale.tex` | **Member D** | Design Rationale |
| `sections/04-pros-cons.tex` | **Member E** | Evaluation (Pros & Cons) |
| `sections/05-layered-architecture.tex` | **Member F** | Layered Architecture |
| `sections/06-conclusion.tex` | **Member A** | Conclusion |
| `demo/` | **Member G** | Demo MLOps stack |
| `references.bib` | **Everyone** | Only ADD new entries, never delete |
| `figures/` | **Everyone** | Use clear naming: `memberX-diagram-name.png` |

> ⚠️ **Golden Rule:** Each member **only edits their assigned file**.  
> If you need changes in someone else's file, open a **GitHub Issue** and discuss first.

---

## Repository Setup

### Protect the `main` branch (recommended)

1. Go to **Settings** → **Branches** → **Add branch protection rule**
2. Branch name pattern: `main`
3. ✅ **Require a pull request before merging**
4. ✅ **Require status checks to pass** → select `build-pdf`
5. Click **Create**

---

## Commit & Branch Rules

### Commit message format

```
<type>(<file or section>): <short description>
```

**Valid examples:**
```
feat(02-mlops-concepts): add maturity levels table
fix(03-design-rationale): fix compile error missing end{table}
fig(figures): add layered architecture diagram for section 05
ref(references): add Google MLOps whitepaper 2023
demo(demo): update docker-compose to add PostgreSQL
```

**Commit types:**

| Type | When to use |
|---|---|
| `feat` | Add new content |
| `fix` | Fix content or LaTeX compilation error |
| `fig` | Add or update figures |
| `ref` | Add references |
| `demo` | Changes in `demo/` directory |
| `style` | Formatting only, no content change |
| `docs` | Documentation & README updates |

### Branch naming

```
<member-name>/<short-description>
```

**Examples:**
```
memberB/introduction-draft
memberC/mlops-concepts-tables
memberG/demo-docker-setup
```

**Workflow:**

1. Create a branch from `main`
2. Commit and push to your branch
3. Open a **Pull Request** targeting `main`
4. Wait for **at least 1 approval** before merging

---

## Build PDF Locally

### Prerequisites

Install one of the following LaTeX distributions:

**Option A — TeX Live (recommended)**
```bash
# Linux / Ubuntu / Debian
sudo apt install texlive-full

# macOS
brew install --cask mactex

# Windows: download TeX Live at https://tug.org/texlive/
```

**Option B — MiKTeX**
- Download at: https://miktex.org/download
- On first build, MiKTeX will automatically download any missing packages.

### Build command

```bash
# From the repo root:
latexmk -pdf -interaction=nonstopmode main.tex
```

The output PDF will be generated at `main.pdf`.

```bash
# Clean temporary files:
latexmk -c

# Full clean (including PDF):
latexmk -CA
```

### Using VS Code + LaTeX Workshop

1. Install the extension: **LaTeX Workshop** (`james-yu.latex-workshop`)
2. Open `main.tex`
3. Press `Ctrl+Alt+B` to build &nbsp;|&nbsp; Press `Ctrl+Alt+V` to preview PDF

---

## Check PDF via GitHub Actions

Every push or Pull Request triggers GitHub Actions to **automatically build the PDF**.

**How to check results:**

1. Navigate to the **Actions** tab of the repository
2. Click on the latest workflow run
3. ✅ **Build succeeded** → download PDF from **Artifacts** > `report-pdf`
4. ❌ **Build failed** → inspect the error logs in the "Compile LaTeX document" step

> 💡 **Tip:** Before pushing, run `latexmk -pdf main.tex` locally to catch errors early.

---

## Quick Guide: Clone → Edit → Push

### First time (clone repository)

```bash
# 1. Clone the repository
git clone https://github.com/Tuelord/Seminar.git
cd Seminar

# 2. Create your feature branch
git checkout -b memberX/your-task-name
# Example: git checkout -b memberB/introduction-draft
```

### Each working session

```bash
# 1. Pull latest changes from main
git fetch origin
git rebase origin/main

# 2. Edit your assigned file
#    (e.g., sections/01-introduction.tex)

# 3. Verify build locally
latexmk -pdf -interaction=nonstopmode main.tex

# 4. Stage and commit changes
git add sections/01-introduction.tex
git commit -m "feat(01-introduction): add motivation subsection"

# 5. Push to GitHub
git push origin memberX/your-task-name

# 6. Open a Pull Request on GitHub
```

### Adding figures

```bash
# Place figure in figures/
cp my-diagram.png figures/memberX-diagram-name.png
git add figures/memberX-diagram-name.png
git commit -m "fig(figures): add layered architecture diagram"
git push
```

**Insert figure in `.tex` file:**
```latex
\begin{figure}[ht]
  \centering
  \includegraphics[width=0.8\linewidth]{memberX-diagram-name}
  \caption{Figure caption here.}
  \label{fig:your-label}
\end{figure}
```

### Adding references

**Step 1: Add entry to `references.bib`:**
```bibtex
@article{authorkey2024,
  author  = {Author, Name},
  title   = {Title of the Paper},
  journal = {Journal Name},
  year    = {2024},
  volume  = {1},
  pages   = {1--10}
}
```

**Step 2: Cite in `.tex` file:**
```latex
According to \cite{authorkey2024}, ...
```

---

## MLOps Demo

See [`demo/README.md`](demo/README.md) for detailed instructions on running the demo stack.

**Requirements:** Docker Desktop, Python 3.10+

```bash
cd demo

# Start the stack
docker compose up -d

# Run demo training
python train_demo.py
# → MLflow UI at: http://localhost:5000

# Start serving API
python serve_demo.py
# → API Swagger Docs at: http://localhost:8000/docs
```

---

## Team Members & Contact

| Member | Role | File Ownership |
|---|---|---|
| Member A | Team Lead | `main.tex`, `06-conclusion.tex` |
| Member B | Member | `01-introduction.tex` |
| Member C | Member | `02-mlops-concepts.tex` |
| Member D | Member | `03-design-rationale.tex` |
| Member E | Member | `04-pros-cons.tex` |
| Member F | Member | `05-layered-architecture.tex` |
| Member G | Technical | `demo/`, GitHub setup |

---

*Last updated: 24/10/2026*
