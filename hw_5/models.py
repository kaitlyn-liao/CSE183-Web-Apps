"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_user():
    return auth.current_user.get('id') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later


db.define_table(
    'posts',
    # Field('poster', 'reference auth_user', ondelete="CASCADE"),
    Field('user_email', default = get_user_email),
    Field('name'),
    Field('post_content'),
)

db.define_table(
    'thumbs',
    Field('rater', 'reference auth_user', default=get_user),
    Field('posts_id', 'reference posts'),
    Field('like', 'integer', default=0),
    Field('dislike', 'integer', default=0),
)

db.commit()
