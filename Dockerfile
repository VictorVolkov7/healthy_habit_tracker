FROM python:3.11

WORKDIR /code

RUN pip install "poetry==1.5.1"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-root

COPY . .