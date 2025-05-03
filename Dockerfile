# syntax=docker/dockerfile:1

FROM python:3.13.3-bullseye

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080
COPY . work/
WORKDIR /work/

CMD ["make", "deploy"]
