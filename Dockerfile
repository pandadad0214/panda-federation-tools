# Runs the MCP server over stdio:
#   docker build -t panda-federation-tools .
#   docker run -i --rm -e APIFY_TOKEN panda-federation-tools
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install . && useradd --create-home --uid 10001 mcp
USER mcp

ENTRYPOINT ["panda-federation-tools"]
