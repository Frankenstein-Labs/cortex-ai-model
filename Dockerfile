FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY model-manifest.json ./
RUN pip install --no-cache-dir . && useradd --create-home --uid 10001 cortex
USER cortex
ENV CORTEX_MODEL_CACHE=/models
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["cortex-ai", "serve", "--host", "0.0.0.0"]
