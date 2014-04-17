from flask.ext.script import Manager

from opented.views import app
from opented.generators import freezer


manager = Manager(app)


@manager.command
def freeze():
    """ Freeze the entire site to static HTML. """
    app.config['DEBUG'] = False
    app.config['ASSETS_DEBUG'] = False
    freezer.freeze()

if __name__ == '__main__':
    manager.run()

