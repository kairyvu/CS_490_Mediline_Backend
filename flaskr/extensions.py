import os
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

db = SQLAlchemy()
swag = Swagger(
    template_file=os.path.join(
        os.getcwd(), 'flaskr', 'docs', 'template.yml'
    ),
    parse=True
)