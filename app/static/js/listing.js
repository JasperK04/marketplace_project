/*
    JS for listing page (templates/listing.html)
    * - Handles deactivating and reactivating listings
    * - Handles buying listings
*/

import confirmModal from "./confirmModal.js";
import { deactivate as deactivateListing, reactivate as reactivateListing } from "./activationFunctions.js";

const deactivate_button = document.getElementById('deactivate-listing');
if (deactivate_button) {
    deactivate_button.addEventListener('click', () => {
        confirmModal('Deactivate Listing', 'Are you sure you want to deactivate this listing?', "listings", deactivateListing);
    });
}

const reactivate_button = document.getElementById('reactivate-listing');
if (reactivate_button) {
    reactivate_button.addEventListener('click', () => {
        confirmModal('Reactivate Listing', 'Are you sure you want to reactivate this listing?', "listings", reactivateListing);
    });
}

const buy_button = document.getElementById('buy-listing');
if (buy_button) {
    buy_button.addEventListener('click', () => {
        confirmModal('Confirm Purchase', 'Are you sure you want to buy this listing?', buyListing);
    });
}

function buyListing() {
    const listing_id = window.location.pathname.split('/').pop();
    fetch(`/api/listings/${listing_id}/buy`, {
        method: 'POST',
    })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to buy listing');
            }
        });
}
