Feature: The wishlist service back-end
    As a e-commerce website Owner
    I need a RESTful wishlist service
    So that I can keep track of all the wishlists

Background:
    Given the following wishlists
        |   _id    | name       | customer_id | items | isPublic  |
        |   666f6f2d6261722d71757578    | clothes       | 1      | []      | False    |
        |   666f6f2d6261722d71757579   | jewellery      | 2      | []      | False  |
        |   666f6f2d6261722d71757577    | footwear        | 3     | []     | False    |
        |   666f6f2d6261722d71757576    | games      | 4    | []      | True |

    Given the following items
        |   item_id |   item_name   |   description |   price   |   discount    |   date_added  |
        |   77777  |    test_item   |   test_description    |   100 |   0   |   04/02/2022, 12:45:00    |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlist RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Update and search for an item in a wishlist
    When I visit the "Home Page"
    And I set the "Item ID" to "77777"
    And I set the "Item Wishlist ID" to "666f6f2d6261722d71757577"
    And I press the "Item-Update" button
    Then I should see "666f6f2d6261722d71757577" in the "Wishlist ID" field    
    When I press the "Item-Search" button
    Then I should see "test_item" in the "item search results"


Scenario: List wishlists for a specific customer
    When I visit the "Home Page"
    And I set the "Wishlist CustomerID" to "4"
    And I press the "Search" button
    Then I should see "666f6f2d6261722d71757576" in the "Wishlist ID" field
    And I should see "games" in the "Wishlist Name" field
    And I should see "True" in the "Wishlist IsPublic" dropdown

Scenario: Create a wishlist
    When I visit the "Home Page"
    And I set the "Wishlist Name" to "Happy"
    And I set the "Wishlist CustomerID" to "5"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Wishlist ID" field
    And I press the "Clear" button
    Then the "Wishlist Name" field should be empty
    And the "Wishlist CustomerID" field should be empty
    When I paste the "Wishlist ID" field
    And I press the "Retrieve" button
    Then I should see "Happy" in the "Wishlist Name" field
    And I should see "5" in the "Wishlist CustomerID" field

Scenario: Read a wishlist
    When I visit the "Home Page"
    And I set the "Wishlist ID" to "666f6f2d6261722d71757578"
    And I press the "Retrieve" button
    Then I should see "clothes" in the "Wishlist Name" field
    And I should see "1" in the "Wishlist CustomerID" field
    And I should see "False" in the "Wishlist IsPublic" dropdown

Scenario: Delete a wishlist
    When I visit the "Home Page"
    And I set the "Wishlist CustomerID" to "4"
    And I press the "Search" button
    Then I should see "666f6f2d6261722d71757576" in the "Wishlist ID" field
    And I should see "games" in the "Wishlist Name" field
    And I should see "True" in the "Wishlist IsPublic" dropdown
    
    When I copy the "Wishlist ID" field
    And I press the "Clear" button
    Then the "Wishlist Name" field should be empty
    And the "Wishlist CustomerID" field should be empty
    When I paste the "Wishlist ID" field
    And I press the "Delete" button
    Then I should see the message "Wishlist has been Deleted!"
    When I paste the "Wishlist ID" field
    And I press the "Retrieve" button
    Then the "Wishlist Name" field should be empty
    And the "Wishlist CustomerID" field should be empty

Scenario: Update a wishlist
    When I visit the "Home Page"
    And I set the "Wishlist CustomerID" to "4"
    And I press the "Search" button
    Then I should see "666f6f2d6261722d71757576" in the "Wishlist ID" field
    And I should see "games" in the "Wishlist Name" field
    And I should see "True" in the "Wishlist IsPublic" dropdown
    
    When I copy the "Wishlist ID" field
    And I set the "Wishlist Name" to "new_games"
    And I press the "Update" button
    Then I should see the message "Success"
    When I press the "Clear" button
    And I paste the "Wishlist ID" field
    And I press the "Retrieve" button
    Then I should see "new_games" in the "Wishlist Name" field