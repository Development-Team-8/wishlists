$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#wishlist_id").val(res._id);
        $("#wishlist_name").val(res.name);
        $("#wishlist_customerid").val(res.customer_id);
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

})
