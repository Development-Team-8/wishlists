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
        logger.info("deserialize(%s)", data)
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
        except ValueError as error:
            raise DataValidationError(
                "Invalid date {}: date should match format %m/%d/%Y, %H:%M:%S".format(data["date_added"])
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
    items = fields.ListField(fields.ReferenceField(model=Item), blank=True)

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def serialize(self) -> dict:
        """Serializes a Wishlist into a dictionary"""
        data = {
            "name": self.name,
            "customer_id": self.customer_id,
            "items": [x for x in map(lambda i: i.serialize() if i is not None else None, self.items) if x is not None]
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
            self.items = list(map(lambda i: Item().deserialize(i), data["items"] if "items" in data else []))
        except KeyError as error:
            raise DataValidationError("Invalid wishlist: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError(
                "Invalid wishlist: body of request contained bad or no data"
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


    @classmethod
    def find_all(cls):
        """Query that finds Wishlists by their id"""
        results = cls.objects.all()
        return results

    @classmethod
    def find_by_name(cls, name: str):
        """Query that finds Wishlists by their id"""
        results = cls.objects.raw({"name": name})
        return results

    @classmethod
    def find_by_customer_id(cls, customer_id: str):
        """Query that finds Wishlists by their id"""
        results = cls.objects.raw({"customer_id": customer_id})
        return results

    #Add any more find methods as needed: