import os
from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from app.models import db
from app import create_app
from instance.config import configure_env


configure_env()

app = create_app(config_mode=os.environ.get('FLASK_CONFIG'))
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
