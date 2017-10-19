from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
remote = Table('remote', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('identificator', String(length=200)),
    Column('name', String(length=200)),
    Column('public', Boolean),
    Column('remote_type', String(length=20)),
    Column('order', Integer),
    Column('icon', String(length=200)),
    Column('timestamp', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['remote'].columns['icon'].create()
    post_meta.tables['remote'].columns['order'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['remote'].columns['icon'].drop()
    post_meta.tables['remote'].columns['order'].drop()
