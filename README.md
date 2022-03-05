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