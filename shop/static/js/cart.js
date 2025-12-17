$(document).ready(function() {
    const csrftoken = getCSRFToken();

    // Increase quantity
    $(document).on('click', '.increase-cart-btn', function(e) {
        e.preventDefault();
        var url = $(this).data('url');
        
        makeAjaxRequest(url, 'POST',
            function(response) {
                if (response.success) {
                    location.reload();
                    displayMessage(response.message, 'success');
                } else {
                    displayMessage(response.message, 'error');
                }
            },
            function() {
                displayMessage('Error updating cart.', 'error');
            }
        );
    });

    // Decrease quantity
    $(document).on('click', '.decrease-cart-btn', function(e) {
        e.preventDefault();
        var url = $(this).data('url');
        
        makeAjaxRequest(url, 'POST',
            function(response) {
                if (response.success) {
                    location.reload();
                    displayMessage(response.message, 'success');
                } else {
                    displayMessage(response.message, 'error');
                }
            },
            function() {
                displayMessage('Error updating cart.', 'error');
            }
        );
    });

    // Remove from cart
    $(document).on('click', '.remove-cart-btn', function(e) {
        e.preventDefault();
        var url = $(this).data('url');
        
        makeAjaxRequest(url, 'POST',
            function(response) {
                if (response.success) {
                    location.reload();
                    displayMessage(response.message, 'success');
                } else {
                    displayMessage(response.error, 'error')
                }
            },
            function() {
                displayMessage('Error updating cart.', 'error');
            }
        );
    });
});