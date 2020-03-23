from flask import Flask, flash, redirect, render_template, request, session, url_for, g, jsonify, Blueprint, current_app
from flask_session import Session

from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.sqla import ModelView
from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin, login_required
from oauthlib.oauth2 import WebApplicationClient
import requests
import os
import json


from app.extensions import db, login_manager, GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, PAYPAL_ACCOUNT

from app.models import Posts, Comment, Replies, Author, Consultation, Payment, Admins

from time import ctime

from app.email import send_email

from app.forms import ContactForm, AdminLogin

from app.extensions import login_manager, db



main = Blueprint('main', __name__)


client = WebApplicationClient(GOOGLE_CLIENT_ID)





# Ensure responses aren't cached
@main.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



@main.route("/")
def index():
    posts = Posts.query.order_by('posted_time desc').limit(4)
    return render_template("index.html", posts=posts)



@main.route("/news")
def news():
    posts = Posts.query.all()
    return render_template("archive.html", posts=posts)



@main.route("/post/<int:post_id>", methods=["GET", "POST"])
def post(post_id):
    post = Posts.query.filter_by(id=post_id).one()
    comments = post.comments

    if post == None:
        return ('Error')
    elif current_user.is_authenticated:
        return render_template("show_post0.html", post=post, comments=comments, username=current_user.user_name, userimage=current_user.user_photo)

    return render_template("show_post_login.html", post=post, comments=comments)
    


@main.route("/search")
def search():
    #posts = Posts.query.whoosh_search(request.args.get('query')).all()
    return render_template("archive.html", posts=posts)


@main.route("/consultaion_room")
def pricing():

    consultations = Consultation.query.all()

    return render_template("consultaion_room.html", consultations=consultations)




@main.route("/consultaion_checkout/<int:consultation_id>")
def checkout(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id).one()
    if consultation == None:
        return ("Error")
    return render_template('checkout.html', consultation=consultation, current_user=current_user, paypal_account=PAYPAL_ACCOUNT)





@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/contact_us", methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('contact_us.html', form=form)

        else:

            send_email(form.subject.data, ['mekalissa68@gmail.com', 'divaexplorer58@gmail.com'], 
            """ From: %s <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data))

            
            return render_template('contact_us.html', success=True)
     

    
    return render_template("contact_us.html", form=form)

    

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return Author.query.get(user_id)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()



@main.route("/login")
def login():
    # Forget any user_id
    
    
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



# redirect to previous url
def redirect_url(default='post'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)




@main.route("/login/callback")
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


    # Doesn't exist? Add to database
    if not Author.query.filter_by(google_id=unique_id).one():
        db.session.add(author)
        db.session.commit()

 

    # Begin user session by logging the user in
    login_user(author)

   


    # Send user back to homepage
    return redirect(redirect_url())






@main.route("/admin_login", methods=["GET", "POST"])

def admin_login():
    """Log user in"""

    
    form = AdminLogin()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('admin_login.html', form=form)
        else:
            user = Admins.query.filter_by(username=form.email.data, password=form.password.data).first()
            if user:
                login_user(user)
                # Redirect user to home page
                return redirect("/admin")
            return ("invalid username and/or password")

    else:
        form = AdminLogin()
        return render_template("admin_login.html", form=form)






# Adding new comment
@main.route('/add_comment', methods=["GET", "POST"])
def add_comment():
    if request.method == "POST":
        post_id = request.form.get('post_id')
        posts = Posts.query.get(post_id)
        comment = Comment(content=request.form.get('input_comment'), parent_id=post_id, author=current_user)
        posts_db.session.add(comment)
        posts_db.session.commit()
        flash('Your comment is now live!')
        return redirect(url_for('post', post_id=post_id))



# Adding new reply
@main.route('/add_replay', methods=["GET", "POST"])
def add_replay():
    if request.method == "POST":
        post_id = request.form.get('post_id')
        comment_id = request.form.get('comment_id')
        
        reply = Replies(content=request.form.get('input_reply'), parent_id=comment_id, author=current_user)
        
        posts_db.session.add(reply)
        posts_db.session.commit()
        return redirect(url_for('post', post_id=post_id))




        

@main.route('/success/')
def success():
    try:
        return render_template('payment_success.html')
    except Exception as e:
        return(str(e))




@main.route('/ipn', methods=['GET','POST'])
def ipn():

    arg = ''
    request.parameter_storage_class = ImmutableOrderedMultiDict
    values = request.form


    for x, y in values.items():
        arg += "&{x}={y}".format(x=x,y=y)


    validate_url = 'https://www.sandbox.paypal.com' \
					   '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
					   .format(arg=arg)

    r = requests.get(validate_url)

    if r.text == 'VERIFIED':

        payer_email =  request.form.get('payer_email')
        unix = ctime()
        payment_date = request.form.get('payment_date')
        username = request.form.get('first_name')
        last_name = request.form.get('last_name')
        payment_gross = request.form.get('mc_gross')
        payment_fee = request.form.get('mc_fee')
        payment_net = float(payment_gross) - float(payment_fee)
        payment_status = request.form.get('payment_status')
        txn_id = request.form.get('txn_id')
        

        payment = Payment(payer_email=payer_email, unix=unix, payment_date=payment_date, username=username, last_name=last_name, payment_gross=payment_gross, payment_fee=payment_fee, payment_net=payment_net, payment_status=payment_status, txn_id=txn_id, author=current_user)
        db.session.add(payment)
        db.session.commit()

        
        send_email("Payment from the website", ['mekalissa68@gmail.com', 'divaexplorer58@gmail.com'],

         """
Divaexplorer Order Summary

Dear %s,

Thank you for choosing Divaexplorer. Here's a summary of your order.

Order Details

Order Date: %s                                       Payment Source: Paypal
Transaction ID: %s                                       Initial Charge: %s
                                                         Final Cost: %s
                                                         Item Type:

                                                         TOTAL:	%s

For any concern. Please Contact us via divaexplorer@divaexplorer-tvj.co.uk.


Regards,
Team Divaexplorer
https://www.divaexplorer-tvj.co.uk/

London, UK


""" % (username + " " + last_name, unix, txn_id, "£"+payment_gross, "£"+payment_gross, "£"+payment_gross)
        
        )
        
        
    

        with open('/tmp/ipnout.txt','a') as f:
            data = 'SUCCESS\n'+str(values)+'\n'
            f.write(data)

        

        

    else:
        with open('/tmp/ipnout.txt','a') as f:
            data = 'FAILURE\n'+str(values)+'\n'
            f.write(data)

    return r.text