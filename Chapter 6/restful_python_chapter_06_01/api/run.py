"""
Book: Building RESTful Python Web Services
Chapter 6: Working with models, SQLAlchemy, and hyperlinked APIs in Flask
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
from app import create_app


app = create_app('config')


if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
