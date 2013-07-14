# manage.py

from flask.ext.script import Manager
from flask.ext.assets import ManageAssets

from app import app
from app import assets as assets_env

manager = Manager(app)

manager.add_command("assets", ManageAssets(assets_env))

if __name__ == "__main__":
    manager.run()
