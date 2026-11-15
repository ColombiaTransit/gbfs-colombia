# SPDX-License-Identifier: AGPL-3.0-or-later
# GBFS API upstream uses SQLite 3.49.1 for its JSON queries.
FROM debian:bookworm-slim AS sqlite-build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /build/sqlite \
    && curl -fsSL https://www.sqlite.org/2025/sqlite-autoconf-3490100.tar.gz \
       | tar -xz -C /build/sqlite --strip-components=1 \
    && cd /build/sqlite \
    && ./configure --prefix=/usr/local \
    && make -j2 \
    && make install

FROM python:3.12-slim-bookworm AS python-build
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
# Pinned upstream revisions: update intentionally, then run image CI tests.
ARG PYBIKES_REF=b8681d2344d2ccc61d7b99b089a8cdba167a169e
ARG HYPER_REF=6f0674053582c91d3fbe91c4e05808c99a13fbaf
ARG GBFS_API_REF=28e1e5c9b7fb4e6d927a60699ae1679214d5be0f
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
       "git+https://github.com/eskerda/pybikes.git@$PYBIKES_REF" \
       "git+https://github.com/citybikes/hyper.git@$HYPER_REF" \
       "git+https://github.com/citybikes/gbfs-api.git@$GBFS_API_REF"

FROM python:3.12-slim-bookworm
COPY --from=sqlite-build /usr/local/lib/ /usr/local/lib/
COPY --from=python-build /opt/venv/ /opt/venv/
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LD_LIBRARY_PATH=/usr/local/lib
WORKDIR /app
COPY colombia_gbfs/ /app/colombia_gbfs/
COPY config/ /app/config/
COPY tests/ /app/tests/
RUN python -c "import sqlite3; assert sqlite3.sqlite_version_info >= (3, 49, 1), sqlite3.sqlite_version" \
    && python -m compileall -q colombia_gbfs \
    && python -m unittest discover -s tests -v \
    && mkdir -p /data \
    && chown -R 10001:10001 /app /data
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "colombia_gbfs.api:app", "--host", "0.0.0.0", "--port", "8000"]
