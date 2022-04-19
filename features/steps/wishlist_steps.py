######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Wishlist Steps

Steps file for Wishlist.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect

@given('the following wishlists')
def step_impl(context):
    """ Delete all Wishlists and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the wishlists and delete them one by one
    context.resp = requests.get(context.base_url + '/wishlists', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for wishlist in context.resp.json():
        context.resp = requests.delete(context.base_url + '/wishlists/' + str(wishlist["_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new wishlists
    create_url = context.base_url + '/wishlists'
    for row in context.table:
        data = {
            "_id": row['_id'],
            "name": row['name'],
            "customer_id": row['customer_id'],
            "isPublic": row['isPublic'] in ['True', 'true', '1'],
            "items": json.loads(row['items'])
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)

@given('the following items')
def step_impl(context):
    headers = {'Content-Type': 'application/json'}
    # list all of the items and delete them one by one
    context.resp = requests.get(context.base_url + '/items', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for item in context.resp.json():
        context.resp = requests.delete(context.base_url + '/items/' + str(item["item_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)

    # load the database with new items
    create_url = context.base_url + '/items'
    for row in context.table:
        data = {
            "item_name": row['item_name'],
            "item_id": row['item_id'],
            "description": row['description'],
            "price": row['price'],
            "discount": row['discount'],
            "date_added": row['date_added']
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)
