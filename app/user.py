from app import app
import flask_login

app.secret_key = 'super secret string'  # Change this!
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self, name, id, active=True):
        self.id = id
        self.name = name
        self.active = active

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.active


notch = User(u'Notch', 1)
steve = User(u'Steve', 2)
creeper = User(u'Creeper', 3, False)

# users = {1: notch, 2: steve, 3: creeper}

@login_manager.user_loader
def user_loader(email):
    if email == 'aaa':
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email != 'aaa':
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == "aaa"

    return user

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'
