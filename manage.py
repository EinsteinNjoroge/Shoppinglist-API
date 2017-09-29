from flask_script import Manager
from flask_migrate import Migrate
from flask_migrate import MigrateCommand
from app.models import db
from app import launch_app

app = launch_app(config_mode="development")
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
