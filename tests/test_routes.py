from unittest import TestCase
import logging
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
import os

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