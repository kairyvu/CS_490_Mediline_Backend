# syntax=docker/dockerfile:1

FROM python:3.13.3-bullseye

COPY . .
RUN pip3 install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["./entrypoint.sh"]
