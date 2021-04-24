"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table(
    'bird',
    ### TODO: define the fields that are in the json.
    Field('bird_name'),
    Field('bird_weight', 'integer', default=0),
    Field('bird_diet'),
    Field('bird_habitat'),
    Field('bird_count', 'integer', default=0),
    Field('user_email', default=get_user_email),
)
db.bird.bird_name.requires = IS_NOT_EMPTY() 
db.bird.bird_weight.requires=IS_INT_IN_RANGE(0,100)
db.bird.bird_count.requires=IS_INT_IN_RANGE(0,100)

db.bird.id.readable = False 
db.bird.user_email.readable = db.bird.user_email.writable = False #does not show email

# db.bird.bird_name.label = T('bird')
# db.bird.bird_weight.label = T('weight')
# db.bird.bird_diet.label = T('diet')
# db.bird.bird_habitat.label = T('habitat')
# db.bird.bird_count.label = T('n_sightings')

db.commit()
