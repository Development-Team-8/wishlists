import os
import unittest
from datetime import datetime
from service.models import Item, Wishlist, DataValidationError
from pymodm.connection import connect
from pymodm.errors import ValidationError
from bson import ObjectId



# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://root:root@localhost:27017/wishlists?authSource=admin")

# pylint: disable=too-many-public-methods
class TestItemModel(unittest.TestCase):

    def setUp(self):
        connect(DATABASE_URI.replace('wishlists?','test?'))
    def test_create_an_item(self):
        """Create an item and assert that it exists"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, 1)
        self.assertEqual(item.item_name, "test")
        self.assertEqual(item.price, 100)
        self.assertEqual(item.discount, 2)
        self.assertEqual(item.description, "test")
        self.assertTrue(item.date_added is not None)

    def test_add_an_item(self):
        """Create an item and add it to the database"""
        test_items = Item.objects.raw({'item_name':'test'})
        test_items.delete()
        items = Item.objects.all()
        self.assertEqual(items.count(), 0)
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        self.assertTrue(item is not None)
        self.assertEqual(item.item_id, 1)
        item.save()
        items = Item.objects.all()
        self.assertEqual(items.count(), 1)
        test_items.delete()

    def test_update_an_item(self):
        """Update an Item"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        self.assertTrue(item is not None)
        self.assertEqual(item.item_name, "test")
        item.save()

        item.item_name = "test_new"
        prev_item_id = item.item_id
        item.save()
        
        self.assertEqual(item.item_id, prev_item_id)
        self.assertEqual(item.item_name, "test_new")
        test_item = Item.objects.raw({'item_name':'test_new'})
        self.assertEqual(test_item.count(), 1)
        test_items = Item.objects.raw({'item_name':'test'})
        test_items.delete()
        test_items = Item.objects.raw({'item_name':'test_new'})
        test_items.delete()

    def test_delete_an_item(self):
        """Delete an Item"""
        test_items = Item.objects.raw({'item_name':'test'})
        test_items.delete()
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        item.save()
        test_items = Item.objects.raw({'item_name':'test'})
        self.assertEqual(test_items.count(), 1)
        test_items.delete()
        self.assertEqual(test_items.count(), 0)


    def test_serialize_an_item(self):
        """Serialize an Item"""
        date = datetime.now()
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=date)
        data = item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("item_id", data)
        self.assertEqual(data["item_id"], 1)
        self.assertIn("item_name", data)
        self.assertEqual(data["item_name"], 'test')
        self.assertIn("price", data)
        self.assertEqual(data["price"], 100)
        self.assertIn("discount", data)
        self.assertEqual(data["discount"], 2)
        self.assertIn("description", data)
        self.assertEqual(data["description"], "test")
        self.assertIn("date_added", data)
        self.assertEqual(data["date_added"], date.strftime("%m/%d/%Y, %H:%M:%S"))

    def test_deserialize_an_item(self):
        """Deserialize an Item"""
        date = datetime.now()
        date = date.replace(microsecond=0)
        data = {"item_id": 1,
                "item_name": 'test',
                "price": 100,
                "discount": 2,
                "description": "test",
                "date_added": date.strftime("%m/%d/%Y, %H:%M:%S")}
        item = Item()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.item_id, 1)
        self.assertEqual(item.item_name, 'test')
        self.assertEqual(item.price, 100)
        self.assertEqual(item.discount, 2)
        self.assertEqual(item.description, "test")
        self.assertEqual(item.date_added, date)

    def test_deserialize_with_no_id(self):
        """Deserialize an Item that has no id"""
        date = datetime.now()
        data = {"item_name": 'test',
                "price": 100,
                "discount": 2,
                "description": "test",
                "date_added": date.strftime("%m/%d/%Y, %H:%M:%S")}
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_with_invalid(self):
        """Deserialize an Item with invalid date"""
        date = datetime.now()
        data = {"item_id": 1,
                "item_name": 'test',
                "price": 100,
                "discount": 2,
                "description": "test",
                "date_added": "invalid"}
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_with_no_data(self):
        """Deserialize an Item that has no data"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """Deserialize an Item that has bad data"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, "string data")

class TestWishlists(unittest.TestCase):
    """Test Cases for Wishlist Model"""

    def setUp(self):
        connect(DATABASE_URI.replace('wishlists','test'))
        Wishlist.objects.all().delete()
        Item.objects.all().delete()

    def test_create_a_wishlist(self):
        """Create a wishlist and assert that it exists"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        wishlist = Wishlist(name="foo", customer_id="bar", items=[item])
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist._id, None)
        self.assertEqual(wishlist.name, "foo")
        self.assertEqual(wishlist.customer_id, "bar")
        self.assertEqual(wishlist.items, [item])

    def test_add_a_wishlist(self):
        """Create a wishlist and add it to the database"""
        wishlists = Wishlist.objects.all()
        self.assertEqual(wishlists.count(), 0)
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        item.save()
        wishlist = Wishlist(name="foo", customer_id="bar", items=[item])
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist._id, None)
        wishlist.save()
        # Assert that it was assigned an id and shows up in the database
        self.assertNotEqual(wishlist._id, None)
        wishlists = Wishlist.objects.all()
        self.assertEqual(wishlists.count(), 1)
        self.assertEqual(wishlists[0].name, "foo")
        self.assertEqual(wishlists[0].customer_id, "bar")
        self.assertEqual(wishlists[0].items, [item])
    def test_update_a_wishlist(self):
        """Update a Wishlist"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        item.save()
        wishlist = Wishlist(name="foo", customer_id="bar", items=[item])
        wishlist.save()
        self.assertNotEqual(wishlist._id, None)
        # Change it an save it
        wishlist.name = "foo2"
        wishlist.save()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        wishlists = Wishlist.objects.all()
        self.assertEqual(wishlists.count(), 1)
        self.assertEqual(wishlists[0].name, "foo2")
        self.assertEqual(wishlists[0].customer_id, "bar")

    def test_delete_a_wishlist(self):
        """Delete a Wishlist"""
        wishlist = Wishlist(name="foo", customer_id="bar")
        wishlist.save()
        self.assertEqual(Wishlist.objects.all().count(), 1)
        # delete the wishlist and make sure it isn't in the database
        wishlist.delete()
        self.assertEqual(Wishlist.objects.all().count(), 0)

    def test_serialize_a_wishlist(self):
        """Serialize a Wishlist"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())

        wishlist = Wishlist(name="foo", customer_id="bar", items=[item])
        data = wishlist.serialize()
        self.assertNotEqual(data, None)
        self.assertNotIn("_id", data)
        self.assertIn("name", data)
        self.assertEqual(data["name"], "foo")
        self.assertIn("customer_id", data)
        self.assertEqual(data["customer_id"], "bar")
        self.assertIn("items", data)
        self.assertEqual(data["items"], [item.serialize()])

    def test_serialize_a_wishlist_with_id(self):
        """Serialize a Wishlist"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        id = ObjectId()
        wishlist = Wishlist(_id=id, name="foo", customer_id="bar", items=[item])
        data = wishlist.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("_id", data)
        self.assertEqual(data["_id"], str(id))
        self.assertIn("name", data)
        self.assertEqual(data["name"], "foo")
        self.assertIn("customer_id", data)
        self.assertEqual(data["customer_id"], "bar")
        self.assertIn("items", data)
        self.assertEqual(data["items"], [item.serialize()])

    def test_deserialize_a_wishlist(self):
        """Deserialize a Wishlist"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        data = {"name": "foo", "customer_id": "bar", "items": [item.serialize()]}
        wishlist = Wishlist()
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist._id, None)
        self.assertEqual(wishlist.name, "foo")
        self.assertEqual(wishlist.customer_id, "bar")
        self.assertEqual(wishlist.items, [item])


    def test_deserialize_a_wishlist_with_id(self):
        """Deserialize a Wishlist"""
        item = Item(item_id=1, item_name='test', price=100, discount=2, description="test", date_added=datetime.now())
        id = ObjectId()
        data = {"_id": id, "name": "foo", "customer_id": "bar", "items": [item.serialize()]}
        wishlist = Wishlist()
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist._id, id)
        self.assertEqual(wishlist.name, "foo")
        self.assertEqual(wishlist.customer_id, "bar")
        self.assertEqual(wishlist.items, [item])

    def test_deserialize_with_no_name(self):
        """Deserialize a Wishlist that has no name"""
        data = {"_id": "0", "customer_id": "foo"}
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_deserialize_with_no_data(self):
        """Deserialize a Wishlist that has no data"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """Deserialize a Wishlist that has bad data"""
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, "string data")

    def test_save_a_wishlist_with_no_name(self):
        """Save a Wishlist with no name"""
        wishlist = Wishlist(None, "cat")
        self.assertRaises(ValidationError, wishlist.save)

    def test_find_wishlist(self):
        """Find a Wishlist by id"""
        saved_wishlist = Wishlist("foo", "bar")
        saved_wishlist.save()
        wishlist = Wishlist.find(saved_wishlist._id)
        self.assertIsNot(wishlist, None)
        self.assertEqual(wishlist._id, saved_wishlist._id)
        self.assertEqual(wishlist.name, "foo")

    def test_find_with_no_wishlists(self):
        """Find a Wishlist with empty database"""
        wishlist = Wishlist.find(ObjectId())
        self.assertIs(wishlist, None)

    def test_find_all(self):
        """Find a Wishlist by id"""
        saved_wishlist = Wishlist("foo", "bar")
        saved_wishlist.save()
        saved_wishlist2 = Wishlist("foo", "bar")
        saved_wishlist2.save()
        wishlists = Wishlist.find_all()
        self.assertIsNot(wishlists, None)
        self.assertEqual(wishlists.count(), 2)

    def test_find_all_with_no_wishlists(self):
        """Find a Wishlist with empty database"""
        wishlists = Wishlist.find_all()
        self.assertIs(wishlists.count(),0)

    def test_find_by_name(self):
        """Find a Wishlist by name"""
        saved_wishlist = Wishlist("foo", "bar")
        saved_wishlist.save()
        wishlists = Wishlist.find_by_name(saved_wishlist.name)
        self.assertIsNot(wishlists, None)
        for wishlist in wishlists:
            self.assertEqual(wishlist.name, "foo")

    def test_find_by_name_with_no_wishlists(self):
        """Find a Wishlist with empty database"""
        wishlists = Wishlist.find_by_name("abc")
        self.assertIs(wishlists.count(), 0)

    def test_find_by_customer_id(self):
        """Find a Wishlist by customer_id"""
        saved_wishlist = Wishlist("foo", "bar")
        saved_wishlist.save()
        wishlists = Wishlist.find_by_customer_id(saved_wishlist.customer_id)
        self.assertIsNot(wishlists, None)
        for wishlist in wishlists:
            self.assertEqual(wishlist.customer_id, saved_wishlist.customer_id)

    def test_find_by_cutomer_id_with_no_wishlists(self):
        """Find a Wishlist with empty database"""
        wishlists = Wishlist.find_by_customer_id("bar")
        self.assertIs(wishlists.count(),0)

    def test_wishlist_invalid_id(self):
        """Find a Wishlist with invalid id"""
        wishlist = Wishlist.find("2")
        self.assertIs(wishlist, None)