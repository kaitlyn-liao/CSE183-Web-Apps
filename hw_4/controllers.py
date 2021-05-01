"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from .common import Field

url_signer = URLSigner(session)

# /add_contact work, along with /edit_contact and /delete_contact.

@action('index')
@action.uses(db, auth.user, 'index.html')
def index():
    print("User:", get_user_email())
    rows = db(db.contact.user_email == get_user_email()).select()
    rows = rows.as_list() 
    # and then we iterate on each one, to add the phone numbers for the contact. 
    for row in rows:
    # Here we must fish out of the db the phone numbers attached to the contact, 
    # and produce a nice string like "354242 (Home), 34343423 (Vacation)" for the contact.  
        s = ""
        phone_row = db(db.phone.contact_id == row["id"]).select()

        for p in phone_row:
            s = s + p.phone_numb + ' (' + p.phone_name + '), '
        # and we can simply assign the nice string to a field of the row!  
        # No matter that the field did not originally exist in the database.    
        row['phone_numbers'] = s

    # So at the end, we can return "nice" rows, each one with our nice string. 
    # A row r will have fields r["first_name"], r["last_name"], r["phone_numbers"], ... 
    # You can pass these rows to the view, so you can display the table. 
    # for row in rows:
    #     print(row["first_name"] + row["last_name"])
    #     print(row["phone_numbers"])
    return dict(
        rows = rows,
        url_signer=url_signer,
    )

@action('edit_contact/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, url_signer.verify(), 'edit_contact.html')
def edit(contact_id=None):
    assert contact_id is not None
    p = db.contact[contact_id]
    print('hi edit contact')
    if p is None:
        # nothing found to be edited
        redirect(URL('index'))

    form = Form(db.contact, record=p, deletable=False, csrf_session=session, formstyle=FormStyleBulma)
    if form.accepted: 
        redirect(URL('index'))

    return dict(
        form = form
    )

@action('edit_phones/<contact_id:int>')
@action.uses(db, auth.user, 'edit_phones.html')
def edit_phones(contact_id=None):
    assert contact_id is not None
    contact = db.contact[contact_id]
    rows = db(db.phone.contact_id == contact.id).select()
    print('hi edit phone')
    return dict(
        rows = rows,
        url_signer=url_signer,
        contact = contact,
    )

@action('edit_phone/<contact_id:int>/<phone_id:int>', method=["GET", "POST"])
@action.uses(db, auth.user, 'edit_phone.html')
def edit_phone(contact_id=None, phone_id=None):
    assert contact_id is not None
    assert phone_id is not None
    c = db.contact[contact_id]
    p = db.phone[phone_id]
    
    print('hi edit singular phone')
    if p is None:
        # nothing found to be edited
        redirect(URL('edit_phones', contact_id))

    form = Form(
        [Field('phone_numb'), Field('phone_name')],
        record=dict(phone_numb=p.phone_numb, phone_name=p.phone_name), 
        deletable=False,
        csrf_session=session, 
        formstyle=FormStyleBulma
        )
    
    if form.accepted: 
        db(db.phone.id == phone_id).update(
            phone_numb=form.vars['phone_numb'],
            phone_name=form.vars['phone_name'],
            contact_id=contact_id,
        )
        redirect(URL('edit_phones', contact_id))

    return dict(
        form = form, contact = c
    )

@action('add_contact', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_contact.html')
def add():
    form = Form(db.contact, csrf_session=session, formstyle=FormStyleBulma)
    print('hi add contact')
    if form.accepted:
        redirect(URL('index'))

    return dict(
        form = form
    )

@action('add_phones/<contact_id:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'add_phones.html')
def add_phones(contact_id=None):
    assert contact_id is not None
    name = db.contact[contact_id]
    form = Form(
        [Field('phone_numb'), Field('phone_name')],
        csrf_session=session, formstyle=FormStyleBulma
    )
    print('hi add phone')
    if form.accepted:
        db.phone.insert(
            phone_numb=form.vars['phone_numb'],
            phone_name=form.vars['phone_name'],
            contact_id=contact_id,
        )
        redirect(URL('edit_phones', contact_id))
    return dict(
        form = form,
        contact_id = contact_id,
        name=name,
        # first = first,
        # last = last,
    )

@action('delete_contact/<contact_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete(contact_id=None):
    assert contact_id is not None
    db(db.contact.id == contact_id).delete()
    redirect(URL('index'))

@action('delete_phone/<contact_id:int>/<phone_id:int>')
@action.uses(db, session, auth.user, url_signer.verify())
def delete(contact_id=None, phone_id=None):
    assert contact_id is not None
    assert phone_id is not None
    db(db.phone.id == phone_id).delete()
    redirect(URL('edit_phones', contact_id))