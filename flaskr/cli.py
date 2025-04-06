import click
from flask.cli import with_appcontext
from flaskr.seed_db import seed_all

@click.command('seed-db')
@with_appcontext
def seed_db():
    seed_all()
    print("Database has been seeded successfully.")

def register_commands(app):
    app.cli.add_command(seed_db)