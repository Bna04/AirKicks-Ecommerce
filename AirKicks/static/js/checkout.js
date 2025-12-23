function validateCheckout() {
    let isValid = true;
    // I start by thinking the form is valid and I'll change this if I find any errors
    // The comment about passing 'event' here was a note for myself earlier
    // because the actual preventDefault() call is in the event listener not this function

    // Card number validation
    const cardNumber = document.getElementById('card_number').value;
    // First I get what the user typed for the card number
    const cleanedCard = cardNumber.replace(/[-\s]/g, '');
    // Then I clean it up by removing any spaces or dashes they might have put in
    if (!/^\d{16}$/.test(cleanedCard)) {
        document.getElementById('card_number_error').textContent = 'Please enter a valid 16-digit card number';
        // If its not exactly 16 digits after cleaning I show an error message
        // I make sure my HTML has a span with id="card_number_error" for this
        isValid = false;
        // And I set isValid to false
    } else {
        document.getElementById('card_number_error').textContent = '';
        // If its okay I clear any old error message
    }

    // Expiry date validation
    const expiry = document.getElementById('expiry').value;
    // I get the expiry date value
    if (!/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(expiry)) {
        document.getElementById('expiry_error').textContent = 'Please enter a valid expiry date (MM/YY)';
        // I use a regular expression here to check if it looks like MM/YY
        isValid = false;
    } else {
        document.getElementById('expiry_error').textContent = '';
    }

    // CVV validation
    const cvv = document.getElementById('cvv').value;
    // Get the CVV
    if (!/^\d{3,4}$/.test(cvv)) {
        document.getElementById('cvv_error').textContent = 'Please enter a valid CVV';
        // I check if its 3 or 4 numbers long
        isValid = false;
    } else {
        document.getElementById('cvv_error').textContent = '';
    }

    // Check for other required fields if necessary
    // Example: Name on Card
    const cardName = document.getElementById('card_name').value;
    // Get the card name
    if (cardName.trim() === '') {
        // If the card name is empty after removing spaces
        // Assuming you add an error
        isValid = false;
    } else {
        // document.getElementById('card_name_error').textContent = '';
    }

    return isValid;
    // At the end I send back true if everything was good or false if there was a problem
}
// This function is what I use to check all the important fields on the checkout form
// like the card number expiry date and CVV before the form actually tries to submit to the server

// In your DOMContentLoaded or if this script is at the end of body:
const checkoutForm = document.getElementById('checkout-form');
// I find my checkout form on the page using its ID
if (checkoutForm) {
    // I only try to add the listener if the form actually exists on the current page
    checkoutForm.addEventListener('submit', function(e) {
        // When the user tries to submit the form (like by clicking the pay button)
        if (!validateCheckout()) { 
            // I run my validateCheckout function to see if everything is filled out right
            e.preventDefault();
            // If validateCheckout says something is wrong (returns false)
            // I stop the form from actually submitting to the server using preventDefault()
            // I would probably also call my displayGlobalMessage function here to tell the user to check errors
        }
    });
}
// This part sets up the checkout form so that when the user tries to submit it
// my validateCheckout function runs first to check for errors on the page itself