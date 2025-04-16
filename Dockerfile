# syntax=docker/dockerfile:1

FROM python:3.13.3-bullseye

COPY . .
RUN pip3 install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--workers=2", "flaskr:create_app()", "-b", "0.0.0.0:5000"]
