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

from werkzeug.datastructures import ImmutableOrderedMultiDict



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







@main.route("/search")
def search():
    #posts = Posts.query.whoosh_search(request.args.get('query')).all()
    return render_template("archive.html", posts=posts)





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
                # Redirect user to Admin panel
                return redirect("/admin")
            return ("invalid username and/or password")

    else:
        form = AdminLogin()
        return render_template("admin_login.html", form=form)




        

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
        

        payment = Payment(payer_email=payer_email, unix=unix, payment_date=payment_date, username=username, last_name=last_name, payment_gross=payment_gross, payment_fee=payment_fee, payment_net=payment_net, payment_status=payment_status, txn_id=txn_id, author=current_user._get_current_object())
        db.session.add(payment)
        db.session.commit()

        
        send_email("Order Summary Txn: "+str(txn_id), ['mekalissa68@gmail.com', 'divaexplorer58@gmail.com'],

         """
Divaexplorer Order Summary

Dear %s,

Thank you for choosing Divaexplorer. Here's a summary of your order.

Order Details

Order Date: %s                                       Payment Source: Paypal
Transaction ID: %s                                     Initial Charge: %s

Final Cost: %s


TOTAL:	%s

For any concern. Please Contact us via divaexplorer@divaexplorer-tvj.co.uk.


Regards,
Team Divaexplorer
http://www.divaexplorer-tvj.co.uk/

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