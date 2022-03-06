from unittest import TestCase
import logging
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
import os
from datetime import datetime

from service.models import Item, Wishlist
from service import routes, status
from pymodm.connection import connect
logging.disable(logging.CRITICAL)

# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://root:root@localhost:27017/wishlists?authSource=admin")

BASE_URL = "/wishlists"
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_FORM="application/x-www-form-urlencoded"

class TestWishlistServer(TestCase):
    """Wishlist Server Tests"""

    @classmethod
    def setUp(self):
        self.app = routes.app.test_client()
        connect(DATABASE_URI.replace('wishlists','testwishlist'))
        Wishlist.objects.all().delete()
        Item.objects.all().delete()

    def test_create_wishlist(self):
        """Create a new Wishlist"""
        new_wishlist = {"name": "books", "customer_id": "customer_1", "items": []}
        resp = self.app.post("/wishlists", json=new_wishlist, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        new_json = resp.get_json()
        self.assertEqual(new_json["name"], "books")
        

    def test_create_wishlist_from_formdata(self):
        wishlist_data = MultiDict()
        wishlist_data.add("name", "Planes")
        wishlist_data.add("customer_id", "user123")
        data = ImmutableMultiDict(wishlist_data)
        resp = self.app.post(
            "/wishlists", data=data, content_type=CONTENT_TYPE_FORM
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        logging.debug("data = %s", data)
        self.assertEqual(data["name"], "Planes")


    def test_create_wishlist_no_content_type(self):
        """Create a wishlist with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_wishlist_wrong_content_type(self):
        """Create a wishlist with wrong Content-Type"""
        data = "jimmy the fish"
        resp = self.app.post("/wishlists", data = data, content_type="plain/text")
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    

    def test_update_wishlist(self):
        """Update an existing Wishlist"""

        # create wishlists "foo"
        new_wishlist = {"name": "foo", "customer_id": "customer_1", "items": []}
        resp = self.app.post("/wishlists", json=new_wishlist, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create wishlist "foo 2"
        new_wishlist = {"name": "foo 2", "customer_id": "customer_1", "items": []}
        resp = self.app.post("/wishlists", json=new_wishlist, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # create wishlist "xxx"
        new_wishlist = {"name": "xxx", "customer_id": "customer_1", "items": []}
        resp = self.app.post("/wishlists", json=new_wishlist, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # rename "xxx" with "foo", the new name should be "foo 3"
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        new_wishlist["name"] = "foo"

        # update
        resp = self.app.put(
            "/wishlists/{}".format(new_wishlist["_id"]),
            json=new_wishlist,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], "foo 3")

    def test_delete_wishlist(self):
        """Delete a Wishlist"""

        # create a wishlist
        test_item = {"item_id":1, "item_name":'test', "price":100, "discount":2, "description":"test", "date_added":datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
        test_wishlist = {"name":"123", "customer_id":"bar", "items":[test_item]}
        resp = self.app.post(
            BASE_URL, json=test_wishlist, content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # delete the wishlist
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, new_wishlist["_id"]), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)

        # make sure they are deleted
        self.assertEqual(Wishlist.find(new_wishlist["_id"]), None)