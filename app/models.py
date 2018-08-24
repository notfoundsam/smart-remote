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

class Rc(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    public = db.Column(db.Boolean)
    order = db.Column(db.Integer)
    icon = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime)
    buttons = db.relationship('Button', backref = 'rc', lazy = 'dynamic')

    def __repr__(self):
        return '<Rc %r>' % (self.id)

class Button(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    rc_id = db.Column(db.Integer, db.ForeignKey('rc.id'))
    arduino_id = db.Column(db.Integer, db.ForeignKey('arduino.id'))
    radio_id = db.Column(db.Integer, db.ForeignKey('radio.id'))
    name = db.Column(db.String(200))
    order_hor = db.Column(db.Integer)
    order_ver = db.Column(db.Integer)
    color = db.Column(db.String(10))
    type = db.Column(db.String(20))
    execute = db.Column(db.Text)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Button %r>' % (self.id)

class Node(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200))
    host_name = db.Column(db.String(200))
    order = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    arduinos = db.relationship('Arduino', backref = 'node', lazy = 'dynamic')

    def __repr__(self):
        return '<Node %r>' % (self.id)

class Arduino(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    node_id = db.Column(db.Integer, db.ForeignKey('node.id'))
    usb = db.Column(db.String(200))
    name = db.Column(db.String(200))
    order = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    radios = db.relationship('Radio', backref = 'arduino', lazy = 'dynamic')

    def __repr__(self):
        return '<Arduino %r>' % (self.id)

class Radio(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    arduino_id = db.Column(db.Integer, db.ForeignKey('arduino.id'))
    pipe = db.Column(db.String(12))
    name = db.Column(db.String(200))
    enabled = db.Column(db.Boolean(True))
    order = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime)
    buttons = db.relationship('Button', backref = 'radio', lazy = 'dynamic')

    def __repr__(self):
        return '<Radio %r>' % (self.id)
