
FROM python:3.12-slim

WORKDIR /code


COPY ./requirements.txt /code/requirements.txt


RUN pip install --upgrade pip && pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["fastapi", "run", "--port", "8080", "--host", "0.0.0.0"]
