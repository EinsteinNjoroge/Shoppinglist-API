from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from app import db
from app import create_instance_of_flask_api
# Import models so that Flask-Migrate knows which models are being migrated
from app import models

app = create_instance_of_flask_api(config_mode="development")
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
