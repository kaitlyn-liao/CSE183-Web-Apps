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
    'contact',
    ### TODO: define the fields that are in the json.
    Field('first_name', requires=IS_NOT_EMPTY()),
    Field('last_name', requires=IS_NOT_EMPTY()),
    Field('user_email', default=get_user_email),
)

db.contact.id.readable = db.contact.id.writable = False 
db.contact.user_email.readable = db.contact.user_email.writable = False #does not show email

db.define_table(
    'phone',
    ### TODO: define the fields that are in the json.
    Field('contact_id', 'reference contact'),
    Field('phone_numb', requires=IS_NOT_EMPTY()),
    Field('phone_name', requires=IS_NOT_EMPTY()),
)

db.phone.phone_numb.label = 'Number'
db.phone.phone_name.label = 'Kind'

db.commit()
