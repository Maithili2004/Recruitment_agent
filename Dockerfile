FROM python:3.11-slim

WORKDIR /app

# Install build dependencies, then clean up in the same layer to reduce image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && pip install --upgrade pip setuptools wheel --no-cache-dir

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && rm -rf ~/.cache/pip \
    && find /usr/local -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local -type d -name "test" -exec rm -rf {} + 2>/dev/null || true

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]