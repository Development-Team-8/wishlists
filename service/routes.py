import json
from flask import jsonify, request, url_for,json,  abort, make_response
from pymongo import MongoClient
from pymodm.connection import connect
import os
from datetime import datetime
from service.models import Item, Wishlist
from service import status
from . import app



# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://root:root@localhost:27017/wishlists?authSource=admin")

client = MongoClient(DATABASE_URI) 
connect(DATABASE_URI)


@app.route("/")
def index():
    """Returns information about the service"""
    app.logger.info("Request for Base URL")
    return jsonify(
        status=status.HTTP_200_OK,
        message="Wishlist Service",
        version="1.0.0"
        #TODO: Add resource URL once implemented using url_for
    )


@app.route("/mongodb/stats")
def mongodb_status():
    """Returns basic stats about mongodb"""
    db = client.admin
    serverStatusResult = db.command("serverStatus")
    return jsonify(
        version=serverStatusResult["version"],
        uptime=serverStatusResult["uptime"],
        message="MongoDB Stats"
    )

@app.route('/wishlists', methods=['POST'])
def create_wishlist():
    """creates a wishlist """
    db_obj = client.wishlist_database
    db_wishlist_obj = db_obj.wishlists

    data = {}
    # Check for form submission data
    if request.headers.get("Content-Type") == "application/x-www-form-urlencoded":
        app.logger.info("Getting data from form submit")
        data = {
            "name": request.form["name"],
            "customer_id": request.form["customer_id"],
            "items": [],
        }
    else:
        check_content_type("application/json")
        app.logger.info("Getting json data from API call")
        data = request.get_json()

    newWishList = db_wishlist_obj.insert_one(data)

    location_url="location_url"

    return make_response(
        jsonify(
            id=str(newWishList.inserted_id),
            name=data['name'],
            customer_id=data['customer_id']
        ), status.HTTP_201_CREATED, {"Location": location_url}
    )



def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            "Content-Type must be {}".format(content_type),
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(content_type),
    )

