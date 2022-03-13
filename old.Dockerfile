# temp stage
FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh /entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
