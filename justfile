# Run both the CSS watcher and the FastAPI server
dev:
    @echo "Starting Development Environment..."
    uv run uvicorn src.main:app --reload & \
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
