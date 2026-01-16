FROM python:3.11.5

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DOCKER_CONTAINER=true


COPY . .

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv .venv
RUN .venv/bin/python3 -m pip install --upgrade pip
RUN .venv/bin/python3 -m pip install poetry
RUN .venv/bin/poetry --version
ENV PATH="/code/.venv/bin:$PATH"
RUN .venv/bin/poetry install --only main

RUN apt-get purge -y --auto-remove gcc python3-dev

CMD ["python3", "-O", "-m", "src"]
