FROM python:3.11-slim
WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN pip install --no-cache-dir uv && uv pip install --system --no-cache-dir -e .

COPY . .
CMD ["uv", "run", "app.py"]