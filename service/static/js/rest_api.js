$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#wishlist_id").val(res._id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_customerid").val(res.customer_id);
        if (res.isPublic == true) {
            $("#wishlist_ispublic").val("true");
        } else {
            $("#wishlist_ispublic").val("false");
        }
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#wishlist_id").val("");
        $("#wishlist_name").val("");
        $("#wishlist_customerid").val("");
        $("#item_id").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Search for an item in a wishlist
    // ****************************************

    $("#item-search-btn").click(function () {

        let item_id = $("#item_id").val();
        let item_wishlist_id = $("#item_wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${item_wishlist_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#item_search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Item ID</th>'
            table += '<th class="col-md-2">Item Name</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Discount</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '<th class="col-md-2">Date Added</th>'
            table += '</tr></thead><tbody>'
            table +=  `<tr id="row_0"><td>${res.item_id}</td><td>${res.item_name}</td><td>${res.price}</td><td>${res.discount}</td><td>${res.description}</td><td>${res.date_added}</td></tr>`;
            table += '</tbody></table>';
            $("#item_search_results").append(table);
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // List a wishlist for a specific customer id
    // ****************************************

    $("#search-btn").click(function () {

        let wishlist_customerid = $("#wishlist_customerid").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists?customer_id=${wishlist_customerid}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Customer ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '</tr></thead><tbody>'
            let firstWishlist = "";
            let items = [];
            for(let i = 0; i < res.length; i++) {
                let wishlist = res[i];
                table +=  `<tr id="row_${i}"><td>${wishlist._id}</td><td>${wishlist.customer_id}</td><td>${wishlist.name}</td><td>`;
                if (i == 0) {
                    firstWishlist = wishlist;
                }
                items.push(wishlist.items);
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstWishlist != "") {
                update_form_data(firstWishlist)
            }

            $("#item_search_results").empty();
            table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Item ID</th>'
            table += '<th class="col-md-2">Item Name</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Discount</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '<th class="col-md-2">Date Added</th>'
            table += '</tr></thead><tbody>'
            for(let i = 0; i < items.length; i++) {
                let item = items[i][0];
                table +=  `<tr id="row_${i}"><td>${item.item_id}</td><td>${item.item_name}</td><td>${item.price}</td><td>${item.discount}</td><td>${item.description}</td><td>${item.date_added}</td></tr>`;
            }
            table += '</tbody></table>';
            $("#item_search_results").append(table);

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update a Wishlist with item
    // ****************************************

    $("#item-update-btn").click(function () {

        let item_id = $("#item_id").val();
        let item_wishlist_id = $("#item_wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "POST",
            url: `/wishlists/${item_wishlist_id}/items`,
            contentType: "application/json",
            data: JSON.stringify({"item_id": parseInt(item_id)})
        })

        
        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Create a Wishlist
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#wishlist_name").val();
        let customerid = $("#wishlist_customerid").val();

        let data = {
            "name": name,
            "customer_id": customerid,
            "items": []
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/wishlists",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Delete a Wishlist
    // ****************************************


    $("#delete-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Wishlist has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });


    // ****************************************
    // Update a Wishlist
    // ****************************************

    $("#update-btn").click(function () {
        
        let wishlist_id = $("#wishlist_id").val();
        let name = $("#wishlist_name").val();


        let data = {
            "name": name
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/wishlists/${wishlist_id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });



    // ****************************************
    // Retrieve a wishlist
    // ****************************************

    $("#retrieve-btn").click(function () {

        let wishlist_id = $("#wishlist_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/wishlists/${wishlist_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });


    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#wishlist_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

})
