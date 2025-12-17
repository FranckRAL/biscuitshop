$(document).ready(function() {
    // Add to cart
    $(document).on('click', '.add-cart-btn', function(e) {
        e.preventDefault();
        var url = $(this).data('url');
        
        makeAjaxRequest(url, 'POST',
            function(response) {
                if (response.success) {
                    $('#cart-count').text(response.cart_count);
                    alert('Product added to cart!');
                } else {
                    alert('Error: ' + (response.error || 'Unknown error'));
                }
            },
            function(xhr, status, error) {
                console.error('Add to cart error:', error);
                alert('Error adding product to cart: ' + error);
            }
        );
    });

    // Toggle favorite on wishlist page
    $(document).on('click', '.favorite-btn', function(e) {
        e.preventDefault();
        var url = $(this).data('url');
        var button = $(this);
        var productCard = button.closest('li');
        
        makeAjaxRequest(url, 'POST',
            function(response) {
                if (response.success) {
                    productCard.fadeOut(300, function() {
                        $(this).remove();
                        if ($('.product-card').length === 0) {
                            location.reload();
                        }
                    });
                    
                    if (response.wishlist_count > 0) {
                        $('#wishlist-count').text(response.wishlist_count);
                    } else {
                        $('#wishlist-count').remove();
                    }
                }
            },
            function(xhr, status, error) {
                console.error('Toggle favorite error:', error);
                alert('Error updating wishlist: ' + error);
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