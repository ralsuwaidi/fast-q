# Run both the CSS watcher and the FastAPI server
dev:
    @echo "Starting Development Environment..."
    PYTHONPATH=src uv run uvicorn src.main:app --host 0.0.0.0 --reload & \
    ./tailwindcss -i ./src/static/input.css -o ./src/static/output.css --watch

stop:
    @echo "Stopping Development Environment..."
    pkill -f uvicorn

# Format everything (Python and HTML)
format:
    @echo "Formatting Python..."
    uv tool run ruff format .
    uv tool run ruff check . --fix
    @echo "Formatting HTML/Jinja..."
    uv run djlint src/ --reformat

# Lint without modifying files (good for CI/CD pipelines)
lint:
    uv tool run ruff check .
    uv run djlint src/ --lint

# Seed the database with sample data
seed:
    @echo "Seeding the database..."
    PYTHONPATH=src uv run python scripts/seed.py

# Wipe the SQLite database and re-seed it from scratch
reset-db:
    @echo "Destroying current database..."
    rm -f database.db
    @echo "Rebuilding and seeding..."
    PYTHONPATH=src uv run python scripts/seed.py

# Inspect the current contents of the database
inspect:
	@echo "🔍 Inspecting Database..."
	PYTHONPATH=src uv run python scripts/inspect_db.py