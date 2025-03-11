
FROM python:3.12-slim

WORKDIR /code

RUN curl -sSL https://install.python-poetry.org | python

# copy project requirement files here to ensure they will be cached.
WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

# install runtime deps - uses $POETRY_VIRTUALENVS_IN_PROJECT internally
RUN poetry install --only main

COPY . .

CMD ["fastapi", "run", "--port", "8080", "--host", "0.0.0.0"]
