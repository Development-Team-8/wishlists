from pymodm import MongoModel, fields

class Item(MongoModel):
    item_id = fields.IntegerField(mongo_name='item_id')
    item_name = fields.CharField(mongo_name='item_name')
    price = fields.IntegerField(mongo_name='price')
    discount = fields.IntegerField(mongo_name='discount', min_value=0, max_value=100)
    description = fields.CharField(mongo_name='description')
    date_added = fields.DateTimeField(mongo_name='date_added')
