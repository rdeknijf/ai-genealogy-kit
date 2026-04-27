FROM ghcr.io/astral-sh/uv:0.11.8 AS uv

FROM mcr.microsoft.com/playwright:v1.59.1-noble

COPY --from=uv /uv /usr/local/bin/uv

RUN apt-get update && apt-get install -y --no-install-recommends \
        bc \
        jq \
        sqlite3 \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code@2.1.119

# Playwright base image has uid 1000 as 'ubuntu' with home /home/ubuntu
USER 1000:1000
WORKDIR /workspace

ENTRYPOINT ["bash"]
