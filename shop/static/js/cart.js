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
                } else {
                    alert('Error: ' + response.error);
                }
            },
            function() {
                alert('Error updating cart.');
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
                } else {
                    alert('Error: ' + response.error);
                }
            },
            function() {
                alert('Error updating cart.');
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
                } else {
                    alert('Error: ' + response.error);
                }
            },
            function() {
                alert('Error removing item from cart.');
            }
        );
    });
});