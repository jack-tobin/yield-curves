FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN apt update && apt install build-essential -y

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md
COPY settings/ /app/settings
COPY scripts/ /app/scripts
COPY src /app/src
COPY uv.lock /app/uv.lock

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY --chmod=+x entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
