"""
Book: Building RESTful Python Web Services
Chapter 8: Testing and Ddeploying an API with Flask
Author: Gaston C. Hillar - Twitter.com/gastonhillar
Publisher: Packt Publishing Ltd. - http://www.packtpub.com
"""
from app import create_app


app = create_app('config')


if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
