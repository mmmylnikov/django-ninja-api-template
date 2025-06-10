FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /install

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev


FROM python:3.13-slim-bookworm

RUN groupadd -g 800 -r unprivileged && \
    useradd -r -g unprivileged -u 800 -m unprivileged

RUN apt-get update && \
    apt-get install -y --no-install-recommends locales gosu && \
    sed -i 's/# ru_RU.UTF-8/ru_RU.UTF-8/' /etc/locale.gen && \
    locale-gen ru_RU.UTF-8 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV LANG=ru_RU.UTF-8 \
    LC_ALL=ru_RU.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt/app

WORKDIR /opt/app

COPY --chown=unprivileged:unprivileged backend /opt/app
COPY --chown=unprivileged:unprivileged entrypoint.sh /opt/app
RUN chmod +x entrypoint.sh && \
    chown -R unprivileged:unprivileged /opt/app 

COPY --from=builder /install /opt/app
ENV PATH="/opt/app/.venv/bin:$PATH"

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE 8000
ENTRYPOINT ["/opt/app/entrypoint.sh"]
CMD ["runserver"]
