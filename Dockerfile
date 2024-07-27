FROM python:3.11-slim as base
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt

FROM base
COPY . .
