# CS_490_Mediline_Backend

### Tech stack
- gunicorn for WSGI server production deployment
- Google Cloud Build for automated deployment through Google Cloud Run
- SQLAlchemy ORM
- WTForms
- Alembic (through flask-migrate)
- Flasgger for Swagger/OpenAPI documentation
- Celery as a task queue

### TO USE CELERY
1) ensure python virtual env is used
2) from CLI run `$ celery -A make_celery worker --loglevel INFO`