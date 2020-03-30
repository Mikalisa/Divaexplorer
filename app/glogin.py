from .extensions import db
from .extensions import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL
from .models import Author

from flask import redirect, request
import requests

from oauthlib.oauth2 import WebApplicationClient







client = WebApplicationClient(GOOGLE_CLIENT_ID)




def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


