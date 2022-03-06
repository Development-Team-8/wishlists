import json
from flask import jsonify, request, url_for, abort
from pymongo import MongoClient
from pymodm.connection import connect
import os
from datetime import datetime
from service.models import Item
from . import app



# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://root:root@localhost:27017/wishlists?authSource=admin")

client = MongoClient(DATABASE_URI) 
connect(DATABASE_URI)

# HTTP RETURN CODES
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

@app.route("/")
def index():
    """Returns information about the service"""
    app.logger.info("Request for Base URL")
    return jsonify(
        status=HTTP_200_OK,
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
    db_obj = client.wishlist_database
    db_wishlist_obj = db_obj.wishlists

    new_wishlist_name = request.form.get('name')
    customer_id = request.form.get('customer_id')
    newWishList = db_wishlist_obj.insert_one({'name' : new_wishlist_name,'customer_id': customer_id, 'items' : [] })
    if newWishList.acknowledged== False:
        return jsonify(
            message="Internal server error"
        ) 

    return jsonify(
        id=str(newWishList.inserted_id),
        name=new_wishlist_name,
        customer_id=customer_id     
    )