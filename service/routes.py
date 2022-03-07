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

@app.route('/wishlists/all', methods=['GET'])
def list_wishlists():
    """list all wishlist """
    db_obj = client.wishlist_database
    db_wishlist_obj = db_obj.wishlists
 
    app.logger.info("Request for wishlist list")
    wishlist_array = []
    customer_id = request.args.get("customer_id")
    name = request.args.get("name")
    if customer_id:
        wishlist_array = db_wishlist_obj.find({"customer_id":customer_id})
    elif name:
        wishlist_array = db_wishlist_obj.find({"name":name})
    else:
        wishlist_array = db_wishlist_obj.find()
 
    results = []
    for document in wishlist_array:
        document['_id']=str(document['_id'])
        results.append(document)
 
 
    app.logger.info("Returning %d wishlist_array", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK,{})


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


######################################################################
# ADD AN ITEM TO WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>/item=<int:item_id>", methods=["PUT"])
def add_item_from_wishlist(wishlist_id, item_id):
    """
    Add an item to a Wishlist
    """
    app.logger.info("Request to add the item with id %s to the wishlist with id: %s", item_id, wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))

    item = Item.find(item_id)
    if not item:
        raise NotFound("Item with id '{}' was not found.".format(item_id))

    wishlist.items.append(item)

    wishlist.save()

    app.logger.info("Item with ID [%s] has been added to wishlist with ID [%s].", item_id, wishlist_id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)

######################################################################
# REMOVE AN ITEM FROM WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>/item=<int:item_id>", methods=["DELETE"])
def delete_item_from_wishlist(wishlist_id, item_id):
    """
    Remove an item from a Wishlist
    """
    app.logger.info("Request to remove the item with id %s from the wishlist with id: %s", item_id, wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))

    item = Item.find(item_id)
    if not item:
        raise NotFound("Item with id '{}' was not found.".format(item_id))

    found=False
    target = Item()
    len = 0

    for i in wishlist.items:
        len+=1
        if i.item_id==item_id:
            found=True
            target=i

    if not found:
        raise NotFound("Item with id '{}' was not found from wishlist with id '{}'.".format(item_id, wishlist_id))
    
    if len==1:
        wishlist=Wishlist(_id=wishlist._id, name=wishlist.name, customer_id=wishlist.customer_id)
    else:
        wishlist.items.remove(target)
    
    wishlist.save()

    app.logger.info("Item with ID [%s] has been removed from wishlist with ID [%s].", item_id, wishlist_id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_204_NO_CONTENT)


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