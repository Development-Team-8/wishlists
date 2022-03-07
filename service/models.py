from pymodm import MongoModel, fields
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

import logging


logger = logging.getLogger("flask.app")

class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Item(MongoModel):
    item_id = fields.IntegerField(mongo_name='_id', primary_key=True)
    item_name = fields.CharField(mongo_name='item_name')
    price = fields.IntegerField(mongo_name='price')
    discount = fields.IntegerField(mongo_name='discount', min_value=0, max_value=100)
    description = fields.CharField(mongo_name='description')
    date_added = fields.DateTimeField(mongo_name='date_added')


    def serialize(self) -> dict:
        """Serializes an Item into a dictionary"""
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "price": self.price,
            "discount": self.discount,
            "description": self.description,
            "date_added": self.date_added.strftime("%m/%d/%Y, %H:%M:%S"),
        }

    def deserialize(self, data: dict):
        """deserializes an Item my marshalling the data.

        :param data: a Python dictionary representing an Item.
        """
        print("deserialize(%s)", data)
        try:
            self.item_id = data["item_id"]
            self.item_name = data["item_name"]
            self.price = data["price"]
            self.discount = data["discount"]
            self.description = data["description"]
            self.date_added = datetime.strptime(data["date_added"],"%m/%d/%Y, %H:%M:%S")
            
        except KeyError as error:
            raise DataValidationError("Invalid item: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid item: body of request contained bad or no data"
            )

        return self
    
    @classmethod
    def find(cls, item_id: int):
        """Query that finds Items by their id"""
        try:
            results = cls.objects.raw({"_id": item_id})
            if results.count():
                return results[0]
            else:
                return None
        except InvalidId:
            return None

class Wishlist(MongoModel):


    ##################################################
    # Document Schema
    ##################################################
    name = fields.CharField(required=True)
    customer_id = fields.CharField(required=True)
    items = fields.ListField(fields.ReferenceField(model=Item))

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def serialize(self) -> dict:
        """Serializes a Wishlist into a dictionary"""
        data = {
            "name": self.name,
            "customer_id": self.customer_id,
            "items": list(map(lambda i: i.serialize(), self.items))
        }

        if self._id:
            data["_id"] = str(self._id) 
        return data

    def deserialize(self, data: dict):
        """deserializes a Wishlist my marshalling the data.

        :param data: a Python dictionary representing a Wishlist.
        """
        logger.info("deserialize(%s)", data)
        try:
            self.name = data["name"]
            self.customer_id = data["customer_id"]
            self.items = list(map(lambda i: Item().deserialize(i), data["items"]))
        except KeyError as error:
            raise DataValidationError("Invalid wishlist: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid pet: body of request contained bad or no data"
            )

        # if there is no id and the data has one, assign it
        if not self._id and "_id" in data:
            self._id = ObjectId(data["_id"])

        return self

    ######################################################################
    #  F I N D E R   M E T H O D S
    ######################################################################
    @classmethod
    def find(cls, wishlist_id: str):
        """Query that finds Wishlists by their id"""
        try:
            results = cls.objects.raw({"_id": ObjectId(wishlist_id)})
            if results.count():
                return results[0]
            else:
                return None
        except InvalidId:
            return None

    #Add any more find methods as needed: