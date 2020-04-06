from app.glogin import client, get_google_provider_cfg
from app.models import Author, Consultation, Payment
from flask import redirect, render_template, session, Blueprint, current_app, request, url_for
from flask_login import current_user, login_user

from app.extensions import db
from app.extensions import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL, PAYPAL_ACCOUNT, PAYMENT_SUCCESS, IPN_LINK, HOME_PAGE

from werkzeug.datastructures import ImmutableOrderedMultiDict

import requests

from time import ctime

import json

from flask_login import current_user

from app.email import send_email


import os


purchase = Blueprint('purchase', __name__)



@purchase.route("/consultation_room")
def pricing():

    consultations = Consultation.query.all()

    return render_template("consultation_room.html", consultations=consultations)




@purchase.route("/consultation_checkout/<int:consultation_id>")
def checkout(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id).one()

    session['CON_ID'] = consultation_id

    if consultation == None:
        return ("Error")
    return render_template('checkout.html', consultation=consultation, current_user=current_user, paypal_account=PAYPAL_ACCOUNT, payment_success=PAYMENT_SUCCESS, ipn_link=IPN_LINK, home_page=HOME_PAGE)






@purchase.route("/plogin")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/payment_callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)




@purchase.route("/plogin/payment_callback")
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
    
    

    return redirect(url_for('purchase.checkout', consultation_id=session['CON_ID']))




@purchase.route('/success/')
def success():
    try:
        return render_template('payment_success.html')
    except Exception as e:
        return(str(e))




@purchase.route('/ipn', methods=['GET','POST'])
def ipn():

    arg = ''
    request.parameter_storage_class = ImmutableOrderedMultiDict
    values = request.form


    for x, y in values.items():
        arg += "&{x}={y}".format(x=x,y=y)


    validate_url = 'https://www.paypal.com' \
					   '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
					   .format(arg=arg)

    r = requests.get(validate_url)

    if r.text == 'VERIFIED':

        payer_email =  request.form.get('payer_email')
        unix = ctime()
        payment_date = request.form.get('payment_date')
        item_type = request.form.get('item_name')
        item_count = request.form.get('item_count')
        username = request.form.get('first_name')
        last_name = request.form.get('last_name')
        payment_gross = request.form.get('mc_gross')
        payment_fee = request.form.get('mc_fee')
        payment_net = float(payment_gross) - float(payment_fee)
        payment_status = request.form.get('payment_status')
        txn_id = request.form.get('txn_id')
        

        payment = Payment(payer_email=payer_email, unix=unix, payment_date=payment_date, item_type=item_type, item_count=item_count, username=username, last_name=last_name, payment_gross=payment_gross, payment_fee=payment_fee, payment_net=payment_net, payment_status=payment_status, txn_id=txn_id)
        db.session.add(payment)
        db.session.commit()

        
        send_email("Order Summary Txn: "+str(txn_id), [payer_email, 'divaexplorer58@gmail.com'],

         """
Divaexplorer Order Summary

Dear %s,

Thank you for choosing Divaexplorer. Here's a summary of your order.

Order Details

Order Date: %s
Payment Source: Paypal
Transaction ID: %s
User Email: %s
Item name: %s




Initial Charge: %s

TOTAL:	%s

For any concern. Please Contact us via divaexplorer@divaexplorer-tvj.co.uk.


Regards,
Team Divaexplorer
http://www.divaexplorer-tvj.co.uk/

London, UK


""" % (username + " " + last_name, unix, txn_id, payer_email, item_type, "£"+payment_gross, "£"+payment_gross)
        
        )
        
        
    

        with open('/tmp/ipnout.txt','a') as f:
            data = 'SUCCESS\n'+str(values)+'\n'
            f.write(data)

        

        

    else:
        with open('/tmp/ipnout.txt','a') as f:
            data = 'FAILURE\n'+str(values)+'\n'
            f.write(data)

    return r.text