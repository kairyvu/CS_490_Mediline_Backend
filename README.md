# CS_490_Mediline_Backend

### Tech stack
- gunicorn for WSGI server production deployment
- Google Cloud Build for automated deployment through Google Cloud Run
- SQLAlchemy ORM
- WTForms
- Alembic (through flask-migrate)
- Flasgger for Swagger/OpenAPI documentation
- Celery as a task queue
### TO SET UP CELERY
1) install rabbit MQ on local machine and ensure it's running
2) `pip install -r requirements.txt` to install celery
3) Create a RabbitMQ user and virtual host: <br />
  a) `$ sudo rabbitmqctl add_user <myuser> <mypassword>` <br />
  b) `$ sudo rabbitmqctl add_vhost <myvhost>` <br />
  c) `$ sudo rabbitmqctl set_user_tags <myuser> <mytag>` <br />
  d) `$ sudo rabbitmqctl set_permissions -p <myvhost> <myuser> ".*" ".*" ".*"` \n
4) Add created RabbitMQ user and vhost to .env with variable names: <br />
  `RABBITMQ_USER` <br />
  `RABBITMQ_PASS` <br />
  `RABBITMQ_VHOST` <br />

### TO USE CELERY
1) ensure python virtual env is used
2) from CLI run <br />
`$ celery -A make_celery worker --loglevel INFO`

Test the sample route by POSTing json to localhost:8080/pharmacy/add with schema {"a": <int>, "b": <int>}, <br />
then get result at localhost:8080/pharmacy/result/<id>, where <id> is in the response from the POST
