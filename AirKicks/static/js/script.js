// This is where all my JavaScript interactive stuff happens for the website

document.addEventListener('DOMContentLoaded', function() {
    setupProductHovers();
    setupAddToCartButtons();
    setupCartQuantityControls();
    setupRemoveFromCartButtons();
    setupCheckoutFormValidation();
});
// I put all my main setup functions inside this 'DOMContentLoaded' event
// This makes sure the HTML page is fully loaded before my JavaScript tries to find elements or add listeners
// So this is like the starting point for all the interactive features on my site

function displayGlobalMessage(message, type = 'info', duration = 3500) {
    const container = document.querySelector('.flash-messages-container');
    let alertDiv = document.createElement('div');
    // I create a new div here to hold the message text
    alertDiv.className = `alert alert-${type} global-js-message`;
    alertDiv.textContent = message;
    alertDiv.style.opacity = '0';
    // Setting up how the message looks and making it invisible at first so I can fade it in

    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
        // If I found that special flash message container from my base.html I put the new message there
    } else { 
        alertDiv.style.cssText = 'position:fixed; top:20px; left:50%; transform:translateX(-50%); z-index:10000; padding:10px 20px; border-radius:5px; transition: opacity 0.3s ease-in-out; color: white;';
        if(type === 'success') alertDiv.style.backgroundColor = 'var(--success-green, #388e3c)';
        else if(type === 'error') alertDiv.style.backgroundColor = 'var(--danger-red, #d32f2f)';
        else alertDiv.style.backgroundColor = 'var(--info-blue, #1976d2)';
        document.body.appendChild(alertDiv);
        // If there's no special container I just make the message appear at the top center of the screen
        // I also set some default colors here based on if its a success error or just info
    }
    
    void alertDiv.offsetWidth; 
    // This is a little trick I learned to make sure the browser applies the styles before I start the fade-in animation
    alertDiv.style.opacity = '1';
    // Now I make the message fade in

    setTimeout(() => {
        alertDiv.style.opacity = '0';
        // After a few seconds I make the message fade out
        setTimeout(() => alertDiv.remove(), 300);
        // And then I remove it completely from the page so it doesnt just pile up
    }, duration);
}
// This function is my helper for showing those little pop-up messages for success or errors
// I made it so I can tell it what message what type it is and how long it should stay on screen

// --- Setup Functions for Page Interactions ---
// I decided to group all the functions that set up event listeners and interactivity together here

function setupProductHovers() {
    const tooltip = document.getElementById('product-tooltip');
    if (!tooltip) { 
        console.warn('Product tooltip element not found so hover wont work'); 
        return; 
    }
    // I first grab the tooltip div from my HTML if it's not there this feature wont work

    document.querySelectorAll('.sneaker-card:not(.recent-item)').forEach(card => {
        // I find all the product cards but not the ones in the 'recently viewed' section
        card.addEventListener('mouseenter', function() {
            const productId = this.dataset.productId;
            if (!productId) return;
            // When the mouse goes over a card I get its product ID
            tooltip.innerHTML = '<div class="loading-spinner"></div>';
            tooltip.style.display = 'block';
            // I show a loading spinner and make the tooltip visible
            const rect = this.getBoundingClientRect();
            tooltip.style.left = `${Math.max(0, rect.left + window.scrollX)}px`;
            tooltip.style.top = `${rect.bottom + window.scrollY + 5}px`;
            // This part figures out where to put the tooltip right below the card

            fetch(`/product/${productId}/details_ajax`)
                // Then I fetch the extra details for that product from my Flask app
                .then(response => response.ok ? response.json() : Promise.reject(new Error(`Status ${response.status}`)))
                // I make sure the server responded okay before trying to get the JSON data
                .then(product => {
                    tooltip.innerHTML = `<h4>${product.name || 'Details'}</h4><p>${product.description ? product.description.substring(0,100) + '...' : 'No description.'}</p><p><strong>£${product.price ? product.price.toFixed(2) : 'N/A'}</strong> | 🌱 ${product.carbon_footprint ? product.carbon_footprint + 'kg CO₂' : 'N/A'}</p>`;
                    // If I get the details I put them into the tooltip
                })
                .catch(error => {
                    tooltip.innerHTML = '<p>Details unavailable.</p>';
                    console.error('Hover error:', error);
                    // If there was an error I just say details are unavailable
                });
        });
        card.addEventListener('mouseleave', () => { 
            tooltip.style.display = 'none'; 
        });
        // When the mouse leaves the card I hide the tooltip
    });
}
// This function is for that AJAX hover effect on the product cards on the homepage
// It fetches and shows more details about a product when you hover over it

function setupAddToCartButtons() {
    document.querySelectorAll('button.add-to-cart').forEach(button => {
        // I find all the 'Add to Cart' buttons on the page
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // I stop the button from doing its normal thing like trying to submit a form
            const productId = this.dataset.productId;
            if (!productId) { 
                displayGlobalMessage('Error Product ID missing', 'error'); 
                return; 
            }
            // I get the product ID from the button
            if (this.classList.contains('processing')) return;
            // If its already being added I dont want to do it again

            this.classList.add('processing'); this.disabled = true;
            const originalText = this.innerHTML; this.innerHTML = 'Adding...';
            // I change the button to say 'Adding...' and disable it

            fetch(`/add_to_cart/${productId}`, {
                method: 'POST',
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
            // I send a POST request to my Flask app to add the item
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.innerHTML = '✓ Added!';
                    displayGlobalMessage(data.message || `${data.product_name || 'Item'} added to cart!`, 'success');
                    // If it worked I show a success message and change the button text
                    setTimeout(() => { window.location.href = '/cart'; }, 1000);
                    // Then I decided to redirect to the cart page after a second
                } else { 
                    throw new Error(data.message || 'Could not add item'); 
                }
            })
            .catch(error => {
                displayGlobalMessage(error.message || 'Error adding item', 'error');
                this.innerHTML = originalText; this.disabled = false; this.classList.remove('processing');
                console.error('Add to cart error:', error);
                // If anything went wrong I show an error and change the button back
            });
        });
    });
}
// This whole function sets up the click event for all 'Add to Cart' buttons
// It uses AJAX so the page doesnt have to reload completely

function setupCartQuantityControls() {
    document.querySelectorAll('.quantity-btn').forEach(button => {
        // I find all the plus and minus buttons for quantity in the cart page
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const cartItemId = this.dataset.itemId;
            const action = this.dataset.action; // This will be 'increase' or 'decrease'
            if (!cartItemId || !action) { 
                console.error('Quantity control ID or action missing'); 
                return; 
            }
            // I get the specific cart item's ID and whether to increase or decrease
            this.disabled = true;
            // Disable the button while it's working

            fetch(`/update_cart_item/${cartItemId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-Requested-With': 'XMLHttpRequest'},
                body: JSON.stringify({ action: action })
            })
            // I send a POST request to Flask telling it which item and what action
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success' || data.status === 'removed') {
                    displayGlobalMessage(data.message || 'Cart updated!', 'success');
                    window.location.reload();
                    // If it worked or the item was removed I show a message and reload the page
                    // I decided reloading was simpler than trying to update parts of the page with JS for this assignment
                } else { 
                    throw new Error(data.message || 'Could not update quantity'); 
                }
            })
            .catch(error => {
                displayGlobalMessage(error.message || 'Error updating quantity', 'error');
                this.disabled = false;
                console.error('Quantity update error:', error);
                // If there's an error I show a message and re-enable the button
            });
        });
    });
}
// This function is for the plus and minus buttons in the shopping cart
// It lets users change the quantity of items or remove them if quantity goes to zero

function setupRemoveFromCartButtons() {
    document.querySelectorAll('form.remove-item-form').forEach(form => {
        // I look for all the forms that are specifically for removing items
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // When the form is submitted (button clicked) I stop the normal form submission
            const button = form.querySelector('.remove-btn');
            const cartItemId = button ? button.dataset.cartItemId : null;
            // I get the cart item ID from the button inside the form

            if (!cartItemId) {
                 displayGlobalMessage('Error Cart Item ID missing for removal', 'error');
                 console.error('Remove from cart Cart Item ID missing');
                 return;
            }
            if (button) { button.disabled = true; button.innerHTML = 'Removing...'; }
            // Change the button to show it's working

            fetch(form.action, { 
                method: 'POST', 
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            })
            // I use fetch to send a POST request to the URL specified in the form's action attribute
            .then(response => response.json().then(data => ({ok: response.ok, status: response.status, data})))
            // I expect JSON back from my Flask app
            .then(result => {
                if (result.ok && result.data.status === 'success') {
                    displayGlobalMessage(result.data.message || 'Item removed!', 'success');
                    window.location.href = '/cart'; 
                    // If successful I show a message and then I redirect to the cart page so it updates
                } else {
                    throw new Error(result.data.message || `Could not remove Server status ${result.status}`);
                }
            })
            .catch(error => {
                displayGlobalMessage(error.message || 'Error removing item', 'error');
                if (button) { button.disabled = false; button.innerHTML = '🗑️ Remove';} 
                // If an error happens I show a message and reset the button
                console.error('Remove item error:', error);
            });
        });
    });
}
// This function sets up the 'Remove' buttons in the shopping cart
// It uses AJAX to tell the server to remove the item then refreshes the cart page

function setupCheckoutFormValidation() {
    const checkoutForm = document.getElementById('checkout-form');
    if (checkoutForm) {
        // I only run this if the checkout form actually exists on the current page
        checkoutForm.addEventListener('submit', function(event) {
            // When the user tries to submit the checkout form
            document.querySelectorAll('#checkout-form .js-error').forEach(el => el.textContent = ''); 
            // First I clear out any old JavaScript error messages I might have shown before
            if (!validateCheckoutFields()) {
                // Then I run my separate function to check all the fields
                event.preventDefault();
                // If that function says something is wrong I stop the form from actually submitting
                displayGlobalMessage('Please correct highlighted errors in the form', 'error');
                // And I show a general message telling the user to fix things
            }
        });
    }
}
// This function is for setting up the client-side (JavaScript) validation on my checkout form
// It runs when the user tries to submit the form

function validateCheckoutFields() {
    let isValid = true;
    // I start by assuming everything is okay
    const setError = (el, msg) => { if(el) el.textContent = msg; isValid = false; };
    // This is a little helper I made to show an error message next to a field and mark the form as not valid
    const clearError = (el) => { if(el) el.textContent = ''; };
    // And this one just clears any error message for a field

    const cnInput = document.getElementById('card_number'), cnError = document.getElementById('card_number_error');
    if (cnInput) { 
        const cleaned = cnInput.value.replace(/[-\s]/g, ''); 
        if (!/^\d{16}$/.test(cleaned)) setError(cnError, 'Valid 16-digit card required'); 
        else clearError(cnError); 
    }
    // For the card number I remove spaces and dashes then check if its exactly 16 digits

    const nameInput = document.getElementById('card_name'), nameError = document.getElementById('card_name_error');
    if (nameInput) { 
        if (nameInput.value.trim() === '') setError(nameError, 'Name on card required'); 
        else clearError(nameError); 
    }
    // For the name on the card I just check if its not empty after removing any leading/trailing spaces

    const expInput = document.getElementById('expiry'), expError = document.getElementById('expiry_error');
    if (expInput) { 
        if (!/^(0[1-9]|1[0-2])\/?([0-9]{2})$/.test(expInput.value)) setError(expError, 'Expiry MM/YY required'); 
        else clearError(expError); 
    }
    // For the expiry date I used a regular expression to check for MM/YY format

    const cvvInput = document.getElementById('cvv'), cvvError = document.getElementById('cvv_error');
    if (cvvInput) { 
        if (!/^\d{3,4}$/.test(cvvInput.value)) setError(cvvError, 'Valid CVV required'); 
        else clearError(cvvError); 
    }
    // For the CVV I check if its 3 or 4 digits
    
    return isValid;
    // Finally I return true if all checks passed or false if any of them failed
}
// This function does all the actual checking for each field in the checkout form
// It uses some regular expressions for formats and basic checks for empty fields
// It's my client-side validation part