# temp stage
FROM python:3.9-slim as builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt


# final stage
FROM python:3.9-slim

COPY --from=builder /app/venv /app/venv

WORKDIR /app

ENV PATH="/app/venv/bin:$PATH"

# copy entrypoint.sh
COPY ./entrypoint.sh /entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
