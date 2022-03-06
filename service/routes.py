import json
from flask import jsonify, request, url_for,json,  abort, make_response
from pymongo import MongoClient
from pymodm.connection import connect
import os
from datetime import datetime
from service.models import Item, Wishlist
from service import status
from . import app
from werkzeug.exceptions import NotFound



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
    
    if data["items"]==[]:
        data = Wishlist(name=data["name"], customer_id=data["customer_id"])
    else:
        wishlist = Wishlist()
        data = wishlist.deserialize(data)
    data.save()

    location_url="location_url"

    return make_response(
        jsonify(data.serialize()), status.HTTP_201_CREATED, {"Location": location_url}
    )



######################################################################
# UPDATE AN EXISTING WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>", methods=["PUT"])
def update_wishlists(wishlist_id):
    """
    Update a Wishlist
    This endpoint will update a Wishlist based the body that is posted
    """
    app.logger.info("Request to update wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    
    old_name=wishlist.name

    # new name
    content = request.get_json()
    wishlist.name = content["name"]

    # Rename if the new name is different
    if old_name!=wishlist.name:
        wishlists = Wishlist.objects.all()
        exist = False
        wishlists_name = []
        for i in wishlists:
            wishlists_name.append(i.name)
            if i.name==wishlist.name:
                exist = True
        if exist:
            next = 2
            while 1:
                if (wishlist.name + " {}".format(next)) in wishlists_name:
                    next+=1
                else: break
            wishlist.name = wishlist.name + " {}".format(next)

    wishlist.save()

    app.logger.info("Wishlist with ID [%s] updated.", wishlist._id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist
    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    app.logger.info("Wishlist with ID [%s] delete complete.", wishlist_id)
    return make_response("", status.HTTP_204_NO_CONTENT)



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

