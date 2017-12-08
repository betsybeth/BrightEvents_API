import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import db , models, create_app


app = create_app(config_name=os.getenv("APP_SETTINGS"))
migrate = Migrate(db, app)
manager = Manager(app)

manager.add_command("db", MigrateCommand )

if __name__ == '__main__':
    manage.run()
