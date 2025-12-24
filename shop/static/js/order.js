$(function() {
    $('#payment_method').on('change', function() {
        const selected = $(this).val();
        const $extraFields = $('#extra-fields');
        $extraFields.empty(); // clear previous fields

        if (selected === 'mvola' || selected === 'orange' || selected === 'airtel') {
            $extraFields.html(`
                <label class="block text-sm font-medium text-gray-700">Wallet Number</label>
                <input type="text" name="wallet_number" 
                       class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" required>
            `);
        } else if (selected === 'card') {
            $extraFields.html(`
                <label class="block text-sm font-medium text-gray-700">Card Number</label>
                <input type="text" name="card_number" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" required>
                <label class="block text-sm font-medium text-gray-700 mt-2">Expiry Date</label>
                <input type="text" name="expiry_date" placeholder="MM/YY" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" required>
                <label class="block text-sm font-medium text-gray-700 mt-2">CVV</label>
                <input type="text" name="cvv" class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" required>
            `);
        } else if (selected === 'paypal') {
            $extraFields.html(`
                <label class="block text-sm font-medium text-gray-700">PayPal Email</label>
                <input type="email" name="paypal_email" 
                       class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500" required>
            `);
        } else if (selected === 'cod') {
            $extraFields.html(`
                <p class="text-sm text-gray-600">You will pay in cash upon delivery.</p>
            `);
        }
    });
});