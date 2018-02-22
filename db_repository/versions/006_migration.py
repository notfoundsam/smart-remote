from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
radio = Table('radio', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=200)),
    Column('enabled', Boolean),
    Column('battery', Boolean(create_constraint=False)),
    Column('dht', Boolean(create_constraint=False)),
    Column('timestamp', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['radio'].columns['timestamp'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['radio'].columns['timestamp'].drop()
