from app.glogin import client, get_google_provider_cfg
from app.models import Posts, Author, Comment, Replies
from flask import redirect, render_template, session, Blueprint, current_app, request, url_for
from flask_login import current_user, login_user

from app.extensions import db
from app.extensions import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL, POSTS_PER_PAGE



import requests


import json



blog = Blueprint('blog', __name__)






@blog.route("/blog")
def blogs():
    page = request.args.get('page', 1, type=int)
    posts = Posts.query.paginate(
        page, POSTS_PER_PAGE, False)

    next_url = url_for('blog.blogs', page=posts.next_num) \
        if posts.has_next else None

    prev_url = url_for('blog.blogs', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template("blog.html", posts=posts.items, prev_url=prev_url, next_url=next_url)




@blog.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Posts.query.filter_by(id=post_id).one()
    
    comments = post.comments

    session['POST_ID'] = post.id

    if post == None:
        return ('Error')
    
    return render_template("post.html", post=post, comments=comments, current_user=current_user)







@blog.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)




@blog.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400


    # Create a user in our db with the information provided
    # by Google
    author = Author(
        google_id=unique_id, user_name=users_name, user_email=users_email, user_photo=picture
    )


    user = Author.query.filter_by(google_id=unique_id).first()
    # Doesn't exist? Add to database
    if user:
        # Begin user session by logging the user in
        login_user(user)
        

    else:
        db.session.add(author)
        db.session.commit()
        login_user(author)
        


    # Send user back to homepage
    
    

    return redirect(url_for('blog.post', post_id=session['POST_ID']))








    # Adding new comment
@blog.route('/add_comment', methods=["GET", "POST"])
def add_comment():
    if request.method == "POST":
        post_id = request.form.get('post_id')
        posts = Posts.query.get(post_id)
        comment = Comment(content=request.form.get('input_comment'), parent_id=post_id, author=current_user)
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('blog.post', post_id=post_id))



# Adding new reply
@blog.route('/add_replay', methods=["GET", "POST"])
def add_replay():
    if request.method == "POST":
        post_id = request.form.get('post_id')
        comment_id = request.form.get('comment_id')
        
        reply = Replies(content=request.form.get('input_reply'), parent_id=comment_id, author=current_user)
        
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('blog.post', post_id=post_id))