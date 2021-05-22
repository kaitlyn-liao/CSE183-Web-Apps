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
from .models import get_user

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth.user, 'index.html')
def index():
    return dict(
        load_posts_url = URL('load_posts', signer=url_signer),
        add_post_url = URL('add_post', signer=url_signer),
        delete_post_url = URL('delete_post', signer=url_signer),

        set_thumbs_url = URL('set_thumbs', signer=url_signer),
        get_thumbs_url = URL('get_thumbs', signer=url_signer),
    )

@action('load_posts')
@action.uses(url_signer.verify(), db)
def load_posts():
    email = auth.current_user.get('email')
    rows = db(db.posts).select().as_list()
    return dict(
        rows=rows,
        email=email,
    )

@action('add_post', method="POST")
@action.uses(url_signer.verify(), db)
def add_post():
    #  get the name
    r = db(db.auth_user.email == get_user_email()).select().first()
    full_name = r.first_name + " " + r.last_name if r is not None else "Unknown" 
    id = db.posts.insert(
        # poster = r,
        post_content=request.json.get('post_content'),
        user_email = get_user_email(),
        name=full_name,
        like = False,
        dislike = False,
    )
    return dict(id=id)

@action('delete_post')
@action.uses(db, session, auth.user, url_signer.verify())
def delete_post():
    id = request.params.get('id')
    assert id is not None
    db(db.posts.id == id).delete()
    return "ok"

@action('get_thumbs')
@action.uses(url_signer.verify(), db, auth.user)
def get_thumbs():
    # Returns the rating for a user and an image
    posts_id = request.params.get('posts_id')
    row = db((db.thumbs.posts_id == posts_id) &
             (db.thumbs.rater == get_user())).select().first()
    list_of_like = db((db.thumbs.like == 1) & (db.thumbs.posts_id == posts_id)).select() # list of all post_id that hav been liked
    list_of_dislike = db((db.thumbs.dislike == 1) & (db.thumbs.posts_id == posts_id)).select()
    likers = ""
    dislikers = ""
    for user in list_of_like:
        name = user.rater.first_name + " " + user.rater.last_name + ", "
        likers = likers + name
    for user in list_of_dislike:
        name = user.rater.first_name + " " + user.rater.last_name + ", "
        dislikers = dislikers + name

    if row is not None:
        liked = row.like
    else:
        liked = 0
    if row is not None:
        disliked = row.dislike
    else:
        disliked = 0
    # print(liked)
    # print(disliked)
    return dict(
        like=liked, 
        dislike=disliked,
        likers=likers,
        dislikers=dislikers,
    )

@action('set_thumbs', method='POST')
@action.uses(url_signer.verify(), db, auth.user)
def set_thumbs():
    posts_id = request.json.get('posts_id')
    liked = request.json.get('like')
    disliked = request.json.get('dislike')
    assert posts_id is not None and liked is not None and disliked is not None
    print("before", posts_id)
    print(liked, disliked)
    # check if you need to update thumbs or initialize it in db
    user_post = db( (db.thumbs.posts_id == posts_id) &
                    (db.thumbs.rater == get_user()) ).select().first()

    print(user_post)
    if user_post is not None: 
        db((db.thumbs.posts_id == posts_id) & 
           (db.thumbs.rater == get_user())).update(
            posts_id=posts_id,
            rater=get_user(),
            like=liked,
            dislike=disliked,
        )
        print("after update", posts_id)
        print(liked, disliked)
    else:
        print("after insert", posts_id)
        print(liked, disliked)
        db.thumbs.insert(
            posts_id=posts_id,
            rater=get_user(),
            like=liked,
            dislike=disliked,
        )
    

    return "ok" # Just to have some confirmation in the Network tab.
