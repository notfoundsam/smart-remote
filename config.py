import os

# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
if 'APP_DOCKER' in os.environ:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@db:3306/smart_remote'
else:
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:root@192.168.100.100:3390/smart_remote'

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_TRACK_MODIFICATIONS = False

# root = User(username = 'root', password = 'root', role = '1')

# db.session.add(root)
# db.session.commit()
