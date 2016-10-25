"""
Book: Building RESTful Python Web Services
Chapter 8: Testing and Ddeploying an API with Flask
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import db
from run import app


migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
