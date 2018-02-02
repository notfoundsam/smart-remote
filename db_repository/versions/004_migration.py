from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
button = Table('button', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('identificator', String(length=200)),
    Column('name', String(length=200)),
    Column('order_hor', Integer),
    Column('order_ver', Integer),
    Column('color', String(length=10)),
    Column('timestamp', DateTime),
    Column('signal', Text),
    Column('remote_id', Integer),
    Column('radio', Integer),
    Column('type', String(length=20)),
)

remote = Table('remote', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('identificator', VARCHAR(length=200)),
    Column('name', VARCHAR(length=200)),
    Column('public', BOOLEAN),
    Column('remote_type', VARCHAR(length=20)),
    Column('order', INTEGER),
    Column('icon', VARCHAR(length=200)),
    Column('timestamp', DATETIME),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['button'].columns['type'].create()
    pre_meta.tables['remote'].columns['remote_type'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['button'].columns['type'].drop()
    pre_meta.tables['remote'].columns['remote_type'].create()
