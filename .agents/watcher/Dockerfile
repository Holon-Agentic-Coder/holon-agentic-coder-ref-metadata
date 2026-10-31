# Holon harness GitHub event watcher (Bean 0182). Build context: the harness `.agents/` directory.
FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends gh \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 watcher
WORKDIR /app
COPY scripts/wait_for.py scripts/event_watcher.py /app/

# The token arrives only as GH_TOKEN in the environment at `docker run` / `compose up` time; nothing is baked in.
ENV HOLON_EVENTS_DIR=/data \
    GH_CONFIG_DIR=/tmp/gh \
    GH_PROMPT_DISABLED=1 \
    GH_NO_UPDATE_NOTIFIER=1 \
    PYTHONUNBUFFERED=1
USER watcher
VOLUME ["/data"]
ENTRYPOINT ["python", "/app/event_watcher.py"]
CMD ["watch", "--interval", "60"]
