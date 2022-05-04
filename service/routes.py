import os
import json

from flask import abort, jsonify, make_response, request, url_for
from flask_restx import Api, Resource, fields, reqparse, inputs
from pymodm.connection import connect
from pymongo import MongoClient
from werkzeug.exceptions import NotFound

from service import status
from service.models import Item, Wishlist, DataValidationError, DatabaseConnectionError

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
# Configure Swagger before initializing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Wishlist REST API Service',
          description='This is a sample wishlist server.',
          default='wishlists',
          default_label='Wishlist operations',
          doc='/apidocs' # default also could use doc='/apidocs/'
         )



# Define the model so that the docs reflect what can be sent
create_model_item = api.model('Item', {
    'item_name': fields.String(
                          description='The name of the item'),
    'item_id': fields.Integer(
                              description='The ID of item'),
    'price': fields.Integer(
                        description='Price of the item'),
    'discount': fields.Integer(
                        description='Discount on the item'),
    'description': fields.String(
                          description='Description of the item'),
    'date_added': fields.String(
                        description='Date on which item is added')
})

create_model_wishlist = api.model('Wishlist', {
    'name': fields.String(required=True,
                          description='The name of the wishlist'),
    'customer_id': fields.String(required=True,
                              description='The ID of the customer to which the wishlist belongs'),
    'items': fields.List(fields.Nested(create_model_item), required=True,
                                description='Items in the wishlist', default=[]),
    'isPublic': fields.Boolean(required=False,
                        description='Is the wishlist public?')
})

wishlist_model = api.inherit(
    'WishlistModel', 
    create_model_wishlist,
    {
        '_id': fields.String(readOnly=True,
                            description='The unique id assigned internally by service'),
    }
)

######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE



######################################################################
#  PATH: /wishlists
######################################################################
@api.route('/wishlists', strict_slashes=False)
class WishlistBase(Resource):

    @api.doc('create_wishlist')
    @api.expect(create_model_wishlist)
    @api.response(400, 'The posted data was not valid')
    @api.marshal_with(wishlist_model, code=201)
    def post(self):
        """Creates a wishlist """
        check_content_type("application/json")
        app.logger.info("Getting json data from API call")
        data = request.get_json()
        
        wishlist = Wishlist()
        data = wishlist.deserialize(data)
        data.save()

        return data.serialize(), status.HTTP_201_CREATED
        

    @api.doc('list_wishlists')
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """List all wishlists """
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
        return results, status.HTTP_200_OK

######################################################################
#  PATH: /items
######################################################################
@api.route('/items', strict_slashes=False)
class ItemBase(Resource):

    @api.doc('create_item')
    @api.expect(create_model_item)
    @api.response(400, 'The posted data was not valid')
    @api.response(409, 'The item with given id already exists')
    @api.marshal_with(create_model_item, code=201)
    def post(self):
        """Creates an item"""
        app.logger.info("Request for creating a new item")
        check_content_type("application/json")
        app.logger.info("Getting json data from API call")
        data = request.get_json()
        data = Item().deserialize(data)
        item_id = Item.find(data.item_id)
        if item_id is not None:
            abort(status.HTTP_409_CONFLICT, "Item with id '{}' already exists".format(data.item_id))
            
        data.save()
        return data.serialize(), status.HTTP_201_CREATED

    @api.doc('list_items')
    @api.marshal_list_with(create_model_item)
    def get(self):
        """list all items """
        app.logger.info("Request for item list")
        item_array = []
        item_array = Item.find_all()
        
        results = []
        for document in item_array:
            results.append(document.serialize())
        app.logger.info("Returning %d item_array", item_array.count())
        return results, status.HTTP_200_OK

######################################################################
#  PATH: /wishlists/{id}
######################################################################
@api.route('/wishlists/<wishlist_id>')
@api.param('wishlist_id', 'Wishlist identifier')
class WishlistResource(Resource):

    @api.doc('get_wishlist')
    @api.response(404, 'Wishlist not found')
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single wishlist
        This endpoint will return a wishlist based on it's id
        """
        app.logger.info("Request to Retrieve a wishlist with id [%s]", wishlist_id)
        result = Wishlist.find(wishlist_id)
        
        if not result:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))
            
        return result.serialize(), status.HTTP_200_OK

    @api.doc('update_wishlist')
    @api.response(404, 'Wishlist not found')
    @api.response(400, 'The posted wishlist data was not valid')
    @api.expect(create_model_wishlist)
    @api.marshal_with(wishlist_model)
    def put(self, wishlist_id):
        """
        Update a Wishlist
        This endpoint will update a Wishlist based on the body that is posted
        """
        app.logger.info("Request to update wishlist with id: %s", wishlist_id)
        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))
        
        old_name=wishlist.name

        # new name
        content = request.get_json()

        wishlist.deserialize(content)

        wishlist.save()

        app.logger.info("Wishlist with ID [%s] updated.", wishlist._id)
        return wishlist.serialize(), status.HTTP_200_OK

    @api.doc('delete_wishlist')
    @api.response(204, 'Wishlist deleted')
    def delete(self, wishlist_id):
        """
        Delete a Wishlist
        This endpoint will delete a Wishlist based the id specified in the path
        """
        app.logger.info("Request to delete wishlist with id: %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
            app.logger.info("Wishlist with ID [%s] delete complete.", wishlist_id)
        return "", status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /wishlists/{id}/items
######################################################################
@api.route('/wishlists/<wishlist_id>/items')
@api.param('wishlist_id', 'Wishlist identifier')
class WishlistItemsBase(Resource):

    @api.doc('wishlist_add_item') 
    @api.response(200, 'Item added to wishlist')
    @api.response(400, 'Invalid payload')
    @api.response(404, 'ID not found')
    @api.marshal_with(wishlist_model)
    def post(self, wishlist_id):
        """
        Add an item to a Wishlist
        """
        check_content_type("application/json")

        if "item_id" not in request.get_json():
            abort(status.HTTP_400_BAD_REQUEST, "The payload is missing item_id")

        item_id = request.get_json()["item_id"]
        
        app.logger.info("Request to add the item with id %s to the wishlist with id: %s", item_id, wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))

        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, "Item with id '{}' was not found.".format(item_id))

        wishlist.items.append(item)

        wishlist.save()

        app.logger.info("Item with ID [%s] has been added to wishlist with ID [%s].", item_id, wishlist_id)
        return wishlist.serialize(), status.HTTP_200_OK

    @api.doc('wishlist_list_all_items') 
    @api.response(200, 'Items returned')
    @api.response(404, 'ID not found')
    @api.marshal_list_with(create_model_item)
    def get(self, wishlist_id):
        """List all items in wishlist """
        app.logger.info("Request for wishlist item list")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))

        results = [i.serialize() if i is not None else None for i in wishlist.items if i is not None]
        app.logger.info("Returning %d items", len(wishlist.items))
        return results, status.HTTP_200_OK


######################################################################
#  PATH: /items/{id}
######################################################################
@api.route('/items/<int:item_id>')
@api.param('item_id', 'Item identifier')
class ItemResource(Resource):

    @api.doc('delete_item')
    @api.response(204, 'Item deleted')
    def delete(self, item_id):
        """
        Delete an item
        This endpoint will delete an item based the id specified in the path
        """
        app.logger.info("Request to delete item with id: %s", item_id)
        item = Item.find(item_id)
        if item:
            item.delete()
            app.logger.info("Item with ID [%s] delete complete.", item_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /wishlists/{wishlist_id}/items/{item_id}
######################################################################
@api.route('/wishlists/<string:wishlist_id>/items/<int:item_id>')
@api.param('wishlist_id', 'Wishlist identifier')
@api.param('item_id', 'Item identifier')
class ItemResource(Resource):

    @api.doc('delete_wishlist_item')
    @api.response(204, 'Item deleted from wishlist')
    @api.response(404, 'ID not found')
    def delete(self, wishlist_id, item_id):
        """
        Remove an item from a Wishlist
        """
        app.logger.info("Request to remove the item with id %s from the wishlist with id: %s", item_id, wishlist_id)
        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))

        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, "Item with id '{}' was not found.".format(item_id))

        found=False
        target = Item()
        len = 0

        for i in wishlist.items:
            len+=1
            if i.item_id==item_id:
                found=True
                target=i

        if not found:
            abort(status.HTTP_404_NOT_FOUND, "Item with id '{}' was not found from wishlist with id '{}'.".format(item_id, wishlist_id))
        
        if len==1:
            wishlist=Wishlist(_id=wishlist._id, name=wishlist.name, customer_id=wishlist.customer_id)
        else:
            wishlist.items.remove(target)
        
        wishlist.save()

        app.logger.info("Item with ID [%s] has been removed from wishlist with ID [%s].", item_id, wishlist_id)
        return "", status.HTTP_204_NO_CONTENT


    @api.doc('get_wishlist_item')
    @api.response(200, 'Item retrieved successfully')
    @api.response(404, 'ID not found')
    @api.marshal_with(create_model_item)
    def get(self, wishlist_id, item_id):
        """
        Gets an item from the specified wishlist
        """
        app.logger.info("Request to get an item with id: {} from wishlist with id: {}".format(item_id, wishlist_id))
        
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))

        item_found = None

        for item in wishlist.items:
            if item.item_id == item_id:
                item_found = item;
                break

        if not item_found:
            abort(status.HTTP_404_NOT_FOUND, "Item with id '{}' was not found from wishlist with id '{}'.".format(item_id, wishlist_id))

        result = item_found.serialize()
        app.logger.info("Returning the found item %s", result["item_name"])
        return result, status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/{wishlist_id}/public
######################################################################
@api.route('/wishlists/<string:wishlist_id>/public')
@api.param('wishlist_id', 'Wishlist identifier')
class WishlistPublic(Resource):
    
    @api.doc('toggle_wishlist_public')
    @api.response(200, 'Wishlist made public successfully')
    @api.response(404, 'ID not found')
    @api.marshal_with(create_model_wishlist)
    def put(self, wishlist_id):
        """This action will make a wishlist public"""
        app.logger.info("Request to make wishlist public with id: %s", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)

        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))
        
        wishlist.isPublic = True
        wishlist.save()
        app.logger.info("Wishlist with ID [%s] is made public.", wishlist_id)
        return wishlist.serialize(), status.HTTP_200_OK


######################################################################
#  PATH: /wishlists/{wishlist_id}/empty
######################################################################
@api.route('/wishlists/<string:wishlist_id>/empty')
@api.param('wishlist_id', 'Wishlist identifier')
class WishlistEmpty(Resource):

    @api.doc('empty_wishlist')
    @api.response(200, 'Wishlist emptied successfully')
    @api.response(404, 'ID not found')
    @api.marshal_with(create_model_wishlist)
    def put(self, wishlist_id):
        """
        Remove all items from a Wishlist
        """
        app.logger.info("Request to empty the wishlist with id: %s", wishlist_id)
        check_content_type("application/json")

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))        
        else:
            wishlist=Wishlist(_id=wishlist._id, name=wishlist.name, customer_id=wishlist.customer_id)
        
        wishlist.save()

        app.logger.info("Wishlist with ID [%s] has been emptied", wishlist_id)
        return wishlist.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)

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