import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask.ext.script import Server, Manager
from flask.ext.assets import ManageAssets

from webapp import app
from webapp import assets as assets_env
from webapp.tasks import celery

server = Server(host="0.0.0.0", port=5000)

manager = Manager(app)
manager.add_command("assets", ManageAssets(assets_env))
manager.add_command("runserver", Server(host="0.0.0.0",
                                        port=5000)
)

if __name__ == "__main__":
    manager.run()
