/*
    JS for listing page (templates/listing.html)
    * - Handles deactivating and reactivating listings
    * - Handles buying listings
*/

import confirmModal from "./confirmModal.js";

const deactivate_button = document.getElementById('deactivate-listing');
if (deactivate_button) {
    deactivate_button.addEventListener('click', function() {
        const listing_id = window.location.pathname.split('/').pop();
        fetch(`/api/admin/listings/${listing_id}/deactivate`, {
            method: 'POST',
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to deactivate listing');
            }
        });
    });
}

const reactivate_button = document.getElementById('reactivate-listing');
if (reactivate_button) {
    reactivate_button.addEventListener('click', function() {
        const listing_id = window.location.pathname.split('/').pop();
        fetch(`/api/admin/listings/${listing_id}/reactivate`, {
            method: 'POST',
        })
        .then(response => {
            if (response.ok) {
                window.location.reload();
            } else {
                alert('Failed to reactivate listing');
            }
        });
    });
}

const buy_button = document.getElementById('buy-listing');
if (buy_button) {
    buy_button.addEventListener('click', function() {
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
