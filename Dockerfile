FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY model-manifest.json ./
RUN pip install --no-cache-dir .
EXPOSE 8000
CMD ["cortex-ai", "serve", "--host", "0.0.0.0"]
