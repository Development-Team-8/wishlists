import os
import json

from flask import abort, jsonify, make_response, request, url_for
from pymodm.connection import connect
from pymongo import MongoClient
from werkzeug.exceptions import NotFound

from service import status
from service.models import Item, Wishlist

from . import app

# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://root:root@localhost:27017/wishlists?authSource=admin")

if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap['user-provided'][0]['credentials']['url']

client = MongoClient(DATABASE_URI) 
connect(DATABASE_URI)


@app.route("/")
def index():
    """Base URL for our service"""
    app.logger.info("Request for Base URL")
    return app.send_static_file("index.html")

######################################################################
# CREATE A WISHLIST
######################################################################
@app.route('/wishlists', methods=['POST'])
def create_wishlist():
    """Creates a wishlist """
    check_content_type("application/json")
    app.logger.info("Getting json data from API call")
    data = request.get_json()
    
    wishlist = Wishlist()
    data = wishlist.deserialize(data)
    data.save()

    return make_response(
        jsonify(data.serialize()), status.HTTP_201_CREATED
    )

######################################################################
# CREATE AN ITEM
######################################################################
@app.route('/items', methods=['POST'])
def create_item():
    """Creates an item"""
    app.logger.info("Request for creating a new item")
    check_content_type("application/json")
    app.logger.info("Getting json data from API call")
    data = request.get_json()
    data = Item().deserialize(data)
    item_id = Item.find(data.item_id)
    if item_id is not None:
        return make_response(
            jsonify(status=status.HTTP_409_CONFLICT, error="Conflict", message="Item with id '{}' already exists".format(data.item_id)),
            status.HTTP_409_CONFLICT,
        )
    data.save()
    return make_response(
        jsonify(data.serialize()), status.HTTP_201_CREATED
    )

######################################################################
# LIST ALL WISHLIST
######################################################################
@app.route('/wishlists', methods=['GET'])
def list_wishlists():
    """list all wishlist """
    app.logger.info("Request for wishlist list")
    wishlist_array = []
    customer_id = request.args.get("customer_id")
    name = request.args.get("name")
    if customer_id:
        wishlist_array = Wishlist.find_by_customer_id(customer_id)
    elif name:
        wishlist_array = Wishlist.find_by_name(name)
    else:
        wishlist_array = Wishlist.find_all()

    results = []
    for document in wishlist_array:
        results.append(document.serialize())
    app.logger.info("Returning %d wishlist_array", wishlist_array.count())
    return make_response(jsonify(results), status.HTTP_200_OK,{})


######################################################################
# LIST ALL ITEMS
######################################################################
@app.route('/items', methods=['GET'])
def list_all_items():
    """list all items """
    app.logger.info("Request for item list")
    item_array = []
    item_array = Item.find_all()
    
    results = []
    for document in item_array:
        results.append(document.serialize())
    app.logger.info("Returning %d item_array", item_array.count())
    return make_response(jsonify(results), status.HTTP_200_OK,{})

######################################################################
# GETS AN ITEM FROM A WISHLIST
######################################################################
@app.route('/wishlists/<string:wishlist_id>/items/<int:item_id>', methods=['GET'])
def get_item_from_wishlist(wishlist_id, item_id):
    """
    Gets an item from the specified wishlist
    """
    app.logger.info("Request to get an item with id: {} from wishlist with id: {}".format(item_id, wishlist_id))
    
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        return make_response(
            jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message="Wishlist with id '{}' was not found.".format(wishlist_id)),
            status.HTTP_404_NOT_FOUND,
        )

    item_found = None

    for item in wishlist.items:
        if item.item_id == item_id:
            item_found = item;
            break

    if not item_found:
        return make_response(
            jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message="Item with id '{}' was not found in wishlist with id '{}'".format(item_id, wishlist_id)),
            status.HTTP_404_NOT_FOUND,
        )

    result = item_found.serialize()
    app.logger.info("Returning the found item %s", result["item_name"])
    return make_response(jsonify(result), status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>", methods=["PUT"])
def update_wishlists(wishlist_id):
    """
    Update a Wishlist
    This endpoint will update a Wishlist based on the body that is posted
    """
    app.logger.info("Request to update wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    
    old_name=wishlist.name

    # new name
    content = request.get_json()

    wishlist.deserialize(content)

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
# DELETE AN ITEM
######################################################################
@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    Delete an item
    This endpoint will delete an item based the id specified in the path
    """
    app.logger.info("Request to delete item with id: %s", item_id)
    item = Item.find(item_id)
    if item:
        item.delete()
    app.logger.info("Item with ID [%s] delete complete.", item_id)
    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# ACTION FOR PUBLIC/PRIVATE STATUS OF WISHLIST
######################################################################

@app.route("/wishlists/<string:wishlist_id>/public", methods=["PUT"])
def make_public(wishlist_id):
    """This action will make a wishlist public"""
    app.logger.info("Request to make wishlist public with id: %s", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)

    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    
    wishlist.isPublic = True
    wishlist.save()
    app.logger.info("Wishlist with ID [%s] is made public.", wishlist_id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


######################################################################
# ADD AN ITEM TO WISHLIST
######################################################################
@app.route("/wishlists/<string:wishlist_id>/items", methods=["POST"])
def add_item_to_wishlist(wishlist_id):
    """
    Add an item to a Wishlist
    """
    check_content_type("application/json")

    item_id = request.get_json()["item_id"]
    
    app.logger.info("Request to add the item with id %s to the wishlist with id: %s", item_id, wishlist_id)

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
@app.route("/wishlists/<string:wishlist_id>/items/<int:item_id>", methods=["DELETE"])
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


@app.route("/wishlists/<wishlists_id>", methods=["GET"])
def get_wishlist_details(wishlists_id):
    # db_obj = client.wishlists
    # db_wishlist_obj = db_obj.wishlist
    """
    Retrieve a single Pet
    This endpoint will return a Pet based on it's id
    """
    app.logger.info("Request to Retrieve a pet with id [%s]", wishlists_id)
    result = Wishlist.find(wishlists_id)
    
    if not result:
        # raise NotFound("Wishlist with id '{}' was not found.".format(wishlists_id))
        return make_response(
            jsonify(status=status.HTTP_404_NOT_FOUND, error="Not Found", message="Wishlist with id '{}' was not found.".format(wishlists_id)),
            status.HTTP_404_NOT_FOUND,
        )
    return make_response(jsonify(result.serialize()), status.HTTP_200_OK)

    
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



######################################################################
# LIST ITEMS OF AN EXISTING WISHLIST
######################################################################

@app.route('/wishlists/<string:wishlist_id>/items', methods=['GET'])
def list_items(wishlist_id):
    """list all items in wishlist """
    app.logger.info("Request for wishlist item list")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))

    results = [i.serialize() if i is not None else None for i in wishlist.items if i is not None]
    app.logger.info("Returning %d items", len(wishlist.items))
    return make_response(jsonify(results), status.HTTP_200_OK,{})

@app.route("/wishlists/<string:wishlist_id>/empty", methods=["PUT"])
def empty_wishlist(wishlist_id):
    """
    Remove an item from a Wishlist
    """
    app.logger.info("Request to empty the wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    
    else:
        wishlist=Wishlist(_id=wishlist._id, name=wishlist.name, customer_id=wishlist.customer_id)
    
    wishlist.save()

    app.logger.info("Wishlist with ID [%s] has been emptied", wishlist_id)
    return make_response(jsonify(wishlist.serialize()), status.HTTP_204_NO_CONTENT)

