# syntax=docker/dockerfile:1

FROM python:3.13.3-bullseye

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      make \
      build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /work

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["make", "deploy"]
