# Fast-Q: Modern FastAPI & HTMX Starter

A high-performance, scalable web application template using **Vertical Slice Architecture**, **FastAPI**, and **HTMX**. Built with the next generation of Python and CSS tooling.



## 🚀 The Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance Python web framework. |
| **Database** | [SQLModel](https://sqlmodel.tiangolo.com/) | SQLAlchemy + Pydantic hybrid for modern data modeling. |
| **Frontend** | [HTMX](https://htmx.org/) | High-power interactivity via HTML attributes. |
| **Styling** | [Tailwind CSS v4](https://tailwindcss.com/blog/tailwindcss-v4-alpha) | The new zero-config, CSS-first engine. |
| **Templating** | [Jinja2](https://jinja.palletsprojects.com/) | Robust, industry-standard Python templating. |
| **Tooling** | [uv](https://github.com/astral-sh/uv) | Ultra-fast Python package and project manager. |
| **Task Runner** | [just](https://github.com/casey/just) | A modern command runner for development workflows. |

## 🏗️ Project Architecture: Vertical Slices

This project follows **Vertical Slice Architecture**. Instead of organizing by technical layers (controllers, models, views), we organize by **Features**.

Every feature lives in `src/features/<feature_name>/` and contains:
- **`router.py`**: The FastAPI entry points for the feature.
- **`models.py`**: SQLModel database definitions.
- **`templates/`**: Feature-specific Jinja2 HTML/HTMX fragments.
- **`use_cases/`**: The "Brain" of the feature. A folder where every file represents a single, testable business action (e.g., `create_task.py`).



## 🛠️ Getting Started

### 1. Prerequisites
- [uv](https://github.com/astral-sh/uv) installed.
- [just](https://github.com/casey/just) installed.

### 2. Initial Setup
Clone the repository and run the setup script:

```bash
# Install dependencies
uv sync

# Fix Tailwind binary permissions (macOS only)
chmod +x tailwindcss
xattr -c tailwindcss
```

### 3. Development Mode
Start the FastAPI server and the Tailwind CSS v4 watcher simultaneously:

```bash
just dev
```
The app will be available at `http://localhost:8000`.

## 🧹 Workflow Commands

Use `just` to maintain code quality across the project:

| Command | Action |
| :--- | :--- |
| `just dev` | Runs FastAPI (reload) + Tailwind CSS watcher. |
| `just format` | Formats Python (`ruff`) and HTML (`djlint`). |
| `just lint` | Runs linters to check for code smells. |

## 📂 Folder Structure

```text
.
├── src/
│   ├── core/               # Shared infrastructure (Database config, global types)
│   ├── features/           # Vertical Slices (The heart of the app)
│   │   └── home/
│   │       ├── use_cases/  # Granular business logic
│   │       ├── router.py   # Feature routes
│   │       └── templates/  # Feature UI
│   ├── static/             # Tailwind input/output CSS
│   └── main.py             # App entry point & Router registration
├── tailwindcss             # Standalone Tailwind CLI
├── justfile                # Project task orchestration
└── pyproject.toml          # uv-managed dependencies
```

## 🧠 Adding a New Feature

1. **Create the slice:** `mkdir -p src/features/my_feature/use_cases/`
2. **Define data:** Add `models.py` with your SQLModels.
3. **Write the brain:** Add a specific use case file (e.g., `src/features/my_feature/use_cases/process_data.py`).
4. **Build the face:** Add HTML/HTMX in `templates/`.
5. **Route it:** Create `router.py` and register it in `src/main.py`.

---

## 🔒 License
MIT