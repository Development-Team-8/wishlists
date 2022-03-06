import os
import logging
import unittest

import os
import logging
import unittest
from datetime import datetime
from service.models import Item, Wishlist, DataValidationError
from pymodm.connection import connect
from pymodm.errors import ValidationError
from bson import ObjectId

# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://root:root@localhost:27017/wishlists?authSource=admin")

BASE_URL = "/wishlists"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistServer(unittest.TestCase):
    """Wishlist Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        connect(DATABASE_URI.replace('wishlists','test'))
        Wishlist.objects.all().delete()
        Item.objects.all().delete()

    def test_update_wishlist(self):
        """Update an existing Wishlist"""
        # create wishlists "foo", "foo 2", "xxx", then rename "xxx" with "foo". The new name should be "foo 3"
        test_item = {"item_id"=1, "item_name"='test', "price"=100, "discount"=2, "description"="test", "date_added"=datetime.now())}
        test_wishlist = {"name"="foo", "customer_id"="bar", "items"=[item]}
        resp = self.app.post(
            BASE_URL, json=test_wishlist.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create wishlist "foo 2"
        test_item["item_id"]=2
        test_wishlist["name"]="foo 2"
        resp = self.app.post(
            BASE_URL, json=test_wishlist.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create wishlist "xxx"
        test_item["item_id"]=3
        test_wishlist["name"]="xxx"
        resp = self.app.post(
            BASE_URL, json=test_wishlist.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # rename wishlist "xxx" with "foo", the new name should be "foo 3"
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        new_wishlist["name"] = "foo"
        resp = self.app.put(
            "/wishlists/{}".format(new_wishlist["id"]),
            json=new_wishlist,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], "foo 3")

    def test_delete_wishlist(self):
        """Delete a Wishlist"""

        # create a wishlist
        test_item = {"item_id"=1, "item_name"='test', "price"=100, "discount"=2, "description"="test", "date_added"=datetime.now())}
        test_wishlist = {"name"="foo", "customer_id"="bar", "items"=[item]}
        resp = self.app.post(
            BASE_URL, json=test_wishlist.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # delete the wishlist
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, new_wishlist.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, new_wishlist.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
