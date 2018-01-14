from app import db

ROLE_USER = 0
ROLE_ADMIN = 1

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique = True)
    password = db.Column(db.String(255))
    role = db.Column(db.SmallInteger, default = ROLE_ADMIN)
    email = db.Column(db.String(120), unique = True)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3

    def __repr__(self):
        return '<User %r>' % (self.username)

class Remote(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    identificator = db.Column(db.String(200))
    name = db.Column(db.String(200))
    public = db.Column(db.Boolean)
    remote_type = db.Column(db.String(20))
    order = db.Column(db.Integer)
    icon = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
    buttons = db.relationship('Button', backref = 'remote', lazy = 'dynamic')

    def __repr__(self):
        return '<Remote %r>' % (self.identificator)

class Button(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    identificator = db.Column(db.String(200))
    name = db.Column(db.String(200))
    order_hor = db.Column(db.Integer)
    order_ver = db.Column(db.Integer)
    color = db.Column(db.String(10))
    timestamp = db.Column(db.DateTime)
    signal = db.Column(db.Text)
    remote_id = db.Column(db.Integer, db.ForeignKey('remote.id'))
    radio = db.Column(db.Integer)

    def __repr__(self):
        return '<Button %r>' % (self.identificator)
