![CI Build TDD](https://github.com/Development-Team-8/wishlists/actions/workflows/tdd.yml/badge.svg)

# wishlists

The wishlists resource allows customers to create a collection of products that they wish they had
the money to purchase.

## Setup and Usage

Clone this repo and run `code .` in the directory to launch VS Code. Click on 'Reopen in Container' and VS code will launch these three docker containers:
- app: Used for running the flask app on port 8000
- mongo: MongoDB database on port 27017
- mongo-express: Mongo Express frontend to interact with MongoDB on port 8081. Username and password for development is `dev` and `dev`

## Running the tests

- The tests can be executed by running `nosetests`
- To run the tests along with coverage report, run the command:<br/>
   `nosetests --with-coverage --cover-package=service`
- To see the code coverage report, execute:</br> 
  `coverage report -m`

## Files in the project

* service/routes.py -- the main Service routes using Python Flask
* service/models.py -- the data model
* tests/test_routes.py -- test cases against the Wishlist service
* tests/test_models.py -- test cases against the Wishlist model  

## Endpoints

| Endpoint | Payload | Error Codes | Description |
| -------- | ----------- | ----------- | ------------ |
| GET /   |  None  |  NONE  |  The root URL of the service |
| POST /wishlists | {</br>"name": "name", "customer_id": "customer_id", items:[]</br>} | 415: Unsupported Media TYPE | Creates a new wishlist |
| GET /wishlists | None | None | Returns a list of all the wishlists |
| PUT /wishlists/<string:wishlist_id> | None | 415: Unsupported Media TYPE | Updates a wishlist |
| DELETE /wishlists/<string:wishlist_id> | None | None | Deletes a wishlist |
| GET /wishlists/<string:wishlist_id>/items | None | 404: Not Found | List items in the wishlist |
| POST /wishlists/<string:wishlist_id>/items | {</br>"item_id": "item_id"</br>} | 415: Unsupported Media TYPE | Add an item to the wishlist |
| DELETE /wishlists/<string:wishlist_id>/items/<int:item_id> | None | 415: Unsupported Media TYPE | Remove an item from wishlist |
| POST /items | {</br>"item_id": item_id,</br>"item_name": "item_name",</br>"price": price,</br>"discount": discount,</br>"description": "description",</br>"date_added": "%m/%d/%Y, %H:%M:%S"</br>} | 415: Unsupported Media TYPE | Creates a new Item |
| GET /wishlists/<string:wishlist_id>/items/<int:item_id> | None | 404: Not Found | Get an item from a Wishlist |
