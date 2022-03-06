from flask import jsonify, url_for, abort
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



######################################################################
# UPDATE AN EXISTING WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
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
    wishlist.deserialize(request.get_json())

    # Rename if the new name is different
    if old_name!=wishlist.name:
        wishlists = Wishlist.all()
        exist = False
        wishlists_name = []
        for i in wishlists:
            wishlists_name.append(i.name)
            if i.name==wishlist.name:
                exist = True
        if exist:
            next = 2
            while 1:
                if (wishlist.name + " {}".format(next)) in wishlists_name:  next++
                else: break
            wishlist.name = wishlist.name + " {}".format(next)
    
    wishlist.id = wishlist_id
    wishlist.update()

    app.logger.info("Wishlist with ID [%s] updated.", wishlist.id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE A WISHLIST
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist
    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
    wishlist = Wishlist.find(pet_id)
    if wishlist:
        wishlist.delete()

    app.logger.info("Wishlist with ID [%s] delete complete.", wishlist_id)
    return make_response("", status.HTTP_204_NO_CONTENT)

