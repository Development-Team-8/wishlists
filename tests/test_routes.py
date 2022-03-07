from unittest import TestCase
import logging
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
import os
from datetime import datetime

from service.models import Item, Wishlist
from service import routes, status
from pymodm.connection import connect
from service.models import Item, Wishlist, DataValidationError

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

    def test_get_wishlist_list(self):
        """Get a list of wishlists"""
        init_resp = self.app.get("/wishlists/all")
        self.assertEqual(init_resp.status_code, status.HTTP_200_OK)
        init_data = init_resp.get_json()

        wishlist_1 = Wishlist(name="fruits", customer_id="customer_a")
        wishlist_1.save()
        wishlist_2 = Wishlist(name="music", customer_id="customer_b")
        wishlist_2.save()
        resp = self.app.get("/wishlists/all")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        # logging.info(data)
        self.assertEqual(len(data), len(init_data))
        resp1 = self.app.get("/wishlists/all?name=fruits")
        self.assertEqual(resp1.status_code, status.HTTP_200_OK)
        data1 = resp1.get_json()
        print(data1)
        resp2 = self.app.get("/wishlists/all?customer_id=customer_a")
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        data2 = resp2.get_json()
        print(data2)
    
    
    def test_add_item_to_wishlist(self):
        """Add item to Wishlist"""

        # create a wishlist and an item
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, 1)
        item.save()
        
        test_wishlist = {"name":"123", "customer_id":"bar", "items":[]}
        resp = self.app.post(
            BASE_URL, json=test_wishlist, content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # add the item to the wishlist
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        resp = self.app.put(
            "{0}/{1}/{2}".format(BASE_URL, new_wishlist["_id"],"item=1"), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        updated_wishlist = Wishlist.find(new_wishlist["_id"])
        found=False
        for i in updated_wishlist.items:
            if i.item_id==1:
                found=True
        self.assertEqual(found, True)


    def test_delete_single_item_from_wishlist(self):
        """Delete item from Wishlist"""

        # create a wishlist and an item
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, 1)
        item.save()
        
        test_wishlist = {"name":"123", "customer_id":"bar", "items":[item.serialize()]}
        resp = self.app.post(
            BASE_URL, json=test_wishlist, content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # delete the item from the wishlist
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        resp = self.app.delete(
            "{0}/{1}/{2}".format(BASE_URL, new_wishlist["_id"],"item=1"), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        updated_wishlist = Wishlist.find(new_wishlist["_id"])
        found=False
        for i in updated_wishlist.items:
            if i.item_id==1:
                found=True
        self.assertEqual(found, False)

    def test_delete_item_from_wishlist(self):
        """Delete item from Wishlist"""

        # create a wishlist and an item
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        item.save()
        item1 = Item(item_id=2, item_name='test1', price=100, discount=2, description="test", date_added=datetime.now())
        item1.save()
        
        test_wishlist = {"name":"123", "customer_id":"bar", "items":[item.serialize(),item1.serialize()]}
        resp = self.app.post(
            BASE_URL, json=test_wishlist, content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # delete the item from the wishlist
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        resp = self.app.delete(
            "{0}/{1}/{2}".format(BASE_URL, new_wishlist["_id"],"item=1"), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        updated_wishlist = Wishlist.find(new_wishlist["_id"])
        found=False
        for i in updated_wishlist.items:
            if i.item_id==1:
                found=True
        self.assertEqual(found, False)

    def test_delete_wrong_item_from_wishlist(self):
        """Delete wrong item from Wishlist"""

        # create a wishlist and an item
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, 1)
        item.save()
        
        test_wishlist = {"name":"123", "customer_id":"bar", "items":[item.serialize()]}
        resp = self.app.post(
            BASE_URL, json=test_wishlist, content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # delete the item from the wishlist
        new_wishlist = resp.get_json()
        logging.debug(new_wishlist)
        resp = self.app.delete(
            "{0}/{1}/{2}".format(BASE_URL, new_wishlist["_id"],"item=2"), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
