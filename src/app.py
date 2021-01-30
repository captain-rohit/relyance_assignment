from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_bcrypt import Bcrypt
import os



flask_app = Flask(__name__)

# flask_app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://user:secret@localhost:5432/mydatabase"

# flask_app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
# flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# flask_app.config["BCRYPT_LOG_ROUNDS"] = 5
# flask_app.config['TOKEN_EXPIRATION_DAYS'] = 10
# flask_app.config['TOKEN_EXPIRATION_SECONDS'] = 0
# flask_app.config['SECRET_KEY'] = 'secret'

app_settings = os.getenv('APP_SETTINGS')
flask_app.config.from_object(app_settings)

db = SQLAlchemy(flask_app)
migrate = Migrate(flask_app,db)
manager = Manager(flask_app)
bcrypt = Bcrypt(flask_app)


manager.add_command('db', MigrateCommand)



if __name__ == "__main__":
    manager.run()

from main.views import users_blueprint, banking_blueprint
flask_app.register_blueprint(users_blueprint)
flask_app.register_blueprint(banking_blueprint)

@flask_app.shell_context_processor
def ctx():
    return {'app': flask_app, 'db': db}