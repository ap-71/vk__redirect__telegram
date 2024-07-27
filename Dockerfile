FROM python:3.11-slim as base
WORKDIR /app
COPY requirements.txt /app
RUN pip install —trusted-host pypi.python.org -r requirements.txt

FROM base
COPY . .
