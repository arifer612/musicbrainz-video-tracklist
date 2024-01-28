# syntax=docker/dockerfile:1
# Keep this syntax directive! It's used to enable Docker BuildKit

################################
# PYTHON-BASE
# Sets up all our shared environment variables
################################
FROM python:3.11-slim as python-base

    # Python
ENV PYTHONUNBUFFERED=1
    # pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_DEFAULT_TIMEOUT=100

    # Poetry
    # https://python-poetry.org/docs/configuration/#using-environment-variables
ENV POETRY_VERSION=1.3.2
    # make poetry install to this location
ENV POETRY_HOME="/opt/poetry"
    # do not ask any interactive question
ENV POETRY_NO_INTERACTION=1
    # never create virtual environment automatically, only use env we prepare
ENV POETRY_VIRTUALENVS_CREATE=false

    # this is where our requirements + virtual environment will live
ENV VIRTUAL_ENV="/venv"

# prepend poetry and venv to path
ENV PATH="$POETRY_HOME/bin:$VIRTUAL_ENV/bin:$PATH"

# prepare virtual env
RUN python -m venv $VIRTUAL_ENV

# working directory and Python path
WORKDIR /app
ENV PYTHONPATH="/app:$PYTHONPATH"

################################
# BUILDER-BASE
# Used to build deps + create our virtual environment
################################
FROM python-base as builder-base
RUN apt-get update && \
    apt-get install -y \
    apt-transport-https \
    gnupg \
    ca-certificates \
    build-essential \
    git \
    nano \
    curl

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
# The --mount will mount the buildx cache directory to where
# Poetry and Pip store their cache so that they can re-use it
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python -

# used to init dependencies
WORKDIR /app
COPY poetry.lock pyproject.toml ./
# install runtime deps to $VIRTUAL_ENV
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main

################################
# PRODUCTION
# Final image used for runtime
################################
FROM python-base as production

LABEL org.opencontainers.image.authors="Arif Er <arifer612@proton.me>"
LABEL description="Generate a tracklist of video recordings for MusicBrainz."
LABEL version="2.1.2"

RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y --no-install-recommends \
    ffmpeg && \
    apt-get clean

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $VIRTUAL_ENV $VIRTUAL_ENV

WORKDIR /app
COPY . ./
COPY generate-tracklist /usr/local/bin/generate-tracklist
ENTRYPOINT ["/usr/local/bin/generate-tracklist"]
