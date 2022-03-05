import os
import logging
import unittest
from datetime import datetime
from service.models import Item
from pymodm.connection import connect

# Get the database from the environment (12 factor)
DATABASE_URI = os.getenv("DATABASE_URI", "mongodb://root:root@localhost:27017/wishlists?authSource=admin")
connect(DATABASE_URI)

# pylint: disable=too-many-public-methods
class TestItemModel(unittest.TestCase):
    
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