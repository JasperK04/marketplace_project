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
