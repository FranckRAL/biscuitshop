$(document).ready(function() {
    // Add to cart
    $(document).on('click', '.add-cart-btn', function(e) {
        e.preventDefault();
        var url = $(this).data('url');
        
        makeAjaxRequest(url, 'POST',
            function(response) {
                if (response.success) {
                    $('#cart-count').text(response.cart_count);
                    displayMessage(response.message || 'Added to cart', 'success');
                } else {
                    displayMessage(response.error || 'Unknown error', 'error');
                }
            },
            function(xhr, status, error) {
                displayMessage('Error adding product to cart: ' + error, 'error');
            }
        );
    });

    // Toggle favorite
    $(document).on('click', '.favorite-btn', function(e) {
        e.preventDefault();
        var url = $(this).data('url');
        var button = $(this);
        var productId = button.data('product-id');
        
        makeAjaxRequest(url, 'POST',
            function(response) {
                if (response.success) {
                    if (response.is_favorited) {
                        button.html('<i class="bi bi-heart-fill text-red-500"></i>');
                    } else {
                        button.html('<i class="bi bi-heart text-white"></i>');
                    }
                    
                    if (response.wishlist_count > 0) {
                        $('#wishlist-count').text(response.wishlist_count);
                    } else {
                        $('#wishlist-count').remove();
                    }
                    displayMessage(response.message || 'Wishlist updated', 'success');
                } else {
                    displayMessage(response.error || 'Unknown error', 'error');
                }
            },
            function(xhr, status, error) {
                displayMessage('Error updating wishlist: ' + error, 'error');
            }
        );
    });

    // Product detail modal
    $(document).on('click', '.product-card img, .product-card h3', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var productCard = $(this).closest('.product-card');
        var url = productCard.data('detail-url');
        
        if (!url) {
            return;
        }
        
        $.ajax({
            url: url,
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            dataType: 'json',
            success: function(response) {
                
                // response is a JSON object with html property
                if (response.success && response.html) {
                    var contentDiv = $('#product-details-content');
                    contentDiv.html(response.html);
                    
                    var overlay = $('#product-detail-overlay');
                    overlay.removeClass('hidden');
                } else {
                    alert('Error loading product details: Invalid response');
                }
            },
            error: function(xhr, status, error) {
                alert('Error loading product details: ' + error);
            }
        });
    });

    // Close modal
    $(document).on('click', '#close-modal', function() {
        $('#product-detail-overlay').addClass('hidden');
    });
});